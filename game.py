"""
game.py - AI-Based Rock, Paper, Scissors Game
Task 6: Implementation of an Adaptive Markov Chain Game Engine

Core Features:
1. 3x3 Transition Probability Matrix for tracking human move psychology.
2. AI locks in its prediction and counter-move before user input is revealed.
3. Adaptive confidence display (round 4+) and streak tracker.
4. Periodic pattern analysis reports every 5 rounds.
5. Rich ANSI formatted CLI terminal presentation.
6. Comprehensive end-of-session diagnostic report.
"""

import os
import sys
import random
from typing import Dict, Tuple, Optional, List, Any

# Ensure stdout and stderr use UTF-8 encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Enable native ANSI escape codes in Windows cmd/PowerShell
if os.name == "nt":
    os.system("")

# Optional colorama support
try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass


class Colors:
    """ANSI color codes for terminal styling."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Backgrounds
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_DARK = "\033[40m"


MOVES = ["r", "p", "s"]

MOVE_NAMES = {
    "r": "Rock",
    "p": "Paper",
    "s": "Scissors"
}

MOVE_EMOJIS = {
    "r": "🪨 Rock",
    "p": "📄 Paper",
    "s": "✂️  Scissors"
}

# Rule table: key beats value
BEATS = {
    "r": "s",  # Rock crushes Scissors
    "s": "p",  # Scissors cuts Paper
    "p": "r"   # Paper covers Rock
}

# Winning counter table: key countered by value
COUNTERS = {
    "r": "p",  # Counter to Rock is Paper
    "p": "s",  # Counter to Paper is Scissors
    "s": "r"   # Counter to Scissors is Rock
}


class MarkovPredictor:
    """
    Adaptive Markov Chain prediction engine.
    Constructs a 3x3 transition probability matrix tracking
    user move transitions (previous_move -> current_move).
    """

    def __init__(self):
        # 3x3 Transition Frequency Matrix: row = previous move, col = next move
        self.transitions: Dict[str, Dict[str, int]] = {
            "r": {"r": 0, "p": 0, "s": 0},
            "p": {"r": 0, "p": 0, "s": 0},
            "s": {"r": 0, "p": 0, "s": 0}
        }
        self.total_user_moves: Dict[str, int] = {"r": 0, "p": 0, "s": 0}
        self.last_user_move: Optional[str] = None

    def predict(self, round_number: int) -> Tuple[str, float, bool]:
        """
        Predicts the user's next move based on historical transitions.
        Returns:
            (predicted_move, confidence_percentage, is_random_fallback)
        """
        # Rounds 1 to 3 or when no prior move exists: fallback to random
        if round_number <= 3 or self.last_user_move is None:
            pred = random.choice(MOVES)
            return pred, 33.3, True

        row = self.transitions[self.last_user_move]
        total_transitions_from_last = sum(row.values())

        # If user hasn't played this transition yet, fallback to overall favorite or random
        if total_transitions_from_last == 0:
            total_played = sum(self.total_user_moves.values())
            if total_played > 0:
                # Predict user's overall favorite move
                best_overall = max(self.total_user_moves, key=self.total_user_moves.get)
                conf = (self.total_user_moves[best_overall] / total_played) * 100
                return best_overall, round(conf, 1), False
            return random.choice(MOVES), 33.3, True

        # Find the move(s) with highest transition frequency
        max_count = max(row.values())
        candidates = [m for m, count in row.items() if count == max_count]
        predicted_move = random.choice(candidates)
        
        confidence = (max_count / total_transitions_from_last) * 100.0
        return predicted_move, round(confidence, 1), False

    def update(self, current_user_move: str):
        """Updates the transition matrix and state with the latest user move."""
        self.total_user_moves[current_user_move] += 1
        if self.last_user_move is not None:
            self.transitions[self.last_user_move][current_user_move] += 1
        self.last_user_move = current_user_move

    def get_pattern_stats(self) -> Dict[str, Any]:
        """Returns statistics on user move distribution and dominant transitions."""
        total_moves = sum(self.total_user_moves.values())
        
        # Most played move
        fav_move = None
        fav_pct = 0.0
        if total_moves > 0:
            fav_move = max(self.total_user_moves, key=self.total_user_moves.get)
            fav_pct = (self.total_user_moves[fav_move] / total_moves) * 100.0

        # Most common transition
        best_trans = None
        best_trans_count = 0
        best_trans_pct = 0.0
        
        for prev_m in MOVES:
            row_sum = sum(self.transitions[prev_m].values())
            if row_sum > 0:
                for curr_m in MOVES:
                    count = self.transitions[prev_m][curr_m]
                    if count > best_trans_count:
                        best_trans_count = count
                        best_trans = (prev_m, curr_m)
                        best_trans_pct = (count / row_sum) * 100.0

        return {
            "total_moves": total_moves,
            "fav_move": fav_move,
            "fav_pct": round(fav_pct, 1),
            "move_counts": dict(self.total_user_moves),
            "best_trans": best_trans,
            "best_trans_count": best_trans_count,
            "best_trans_pct": round(best_trans_pct, 1),
            "matrix": self.transitions
        }


def determine_winner(user_move: str, computer_move: str) -> str:
    """
    Resolves outcome of a round.
    Returns:
        'tie', 'user', or 'computer'
    """
    if user_move == computer_move:
        return "tie"
    if BEATS[user_move] == computer_move:
        return "user"
    return "computer"


class RockPaperScissorsGame:
    """Main game engine and state supervisor."""

    def __init__(self):
        self.round_number = 0
        self.user_score = 0
        self.computer_score = 0
        self.tie_count = 0
        
        # Streaks: positive = user streak, negative = AI streak, 0 = neutral
        self.current_streak = 0
        self.best_win_streak = 0
        
        self.ai_correct_predictions = 0
        self.round_log: List[Dict[str, Any]] = []
        self.predictor = MarkovPredictor()

    def print_welcome(self):
        """Displays formatted arcade header and instructions."""
        print(f"\n{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║         🤖 AI-BASED ROCK, PAPER, SCISSORS (MARKOV)           ║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print(f"{Colors.WHITE}Welcome to the Adaptive AI Arena!{Colors.RESET}")
        print(f"• {Colors.YELLOW}Rounds 1-3{Colors.RESET} : AI explores your style using pseudo-random moves.")
        print(f"• {Colors.GREEN}Rounds 4+{Colors.RESET}  : AI activates its {Colors.BOLD}Markov Chain Model{Colors.RESET} to predict")
        print(f"               your patterns and counter your next move!")
        print(f"• Controls   : [{Colors.CYAN}r{Colors.RESET}] Rock  [{Colors.CYAN}p{Colors.RESET}] Paper  [{Colors.CYAN}s{Colors.RESET}] Scissors  [{Colors.RED}q{Colors.RESET}] Quit  [{Colors.YELLOW}m{Colors.RESET}] Matrix")
        print(f"{Colors.DIM}────────────────────────────────────────────────────────────────{Colors.RESET}")

    def prompt_user_move(self) -> Optional[str]:
        """Prompts user for input with validation. Returns 'r', 'p', 's', or None to quit."""
        while True:
            try:
                raw = input(f"\n{Colors.BOLD}Round {self.round_number + 1} ➔ Choose [r / p / s / q]: {Colors.RESET}").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print()
                return None

            if raw in ["q", "quit", "exit"]:
                return None

            if raw in ["m", "matrix"]:
                self.print_matrix_inspection()
                continue

            # Standardized move mappings
            if raw in ["r", "rock"]:
                return "r"
            if raw in ["p", "paper"]:
                return "p"
            if raw in ["s", "scissors", "scissor"]:
                return "s"

            print(f"{Colors.RED}⚠️  Invalid move '{raw}'. Please enter 'r' (Rock), 'p' (Paper), 's' (Scissors), or 'q' to quit.{Colors.RESET}")

    def play_round(self, user_move: str):
        """Executes a single 6-phase game round."""
        self.round_number += 1

        # Phase 1: AI Predicts and Locks In Counter BEFORE reveal
        predicted_user_move, confidence, is_random = self.predictor.predict(self.round_number)
        
        # AI plays the winning counter to its predicted user move
        ai_move = COUNTERS[predicted_user_move]

        # Phase 2: Evaluate Outcome
        result = determine_winner(user_move, ai_move)
        pred_correct = (predicted_user_move == user_move)
        if pred_correct:
            self.ai_correct_predictions += 1

        # Phase 3: Update Scores and Streaks
        if result == "user":
            self.user_score += 1
            if self.current_streak >= 0:
                self.current_streak += 1
            else:
                self.current_streak = 1
            if self.current_streak > self.best_win_streak:
                self.best_win_streak = self.current_streak
        elif result == "computer":
            self.computer_score += 1
            if self.current_streak <= 0:
                self.current_streak -= 1
            else:
                self.current_streak = -1
        else:
            self.tie_count += 1
            # Ties do not reset win streak

        # Phase 4: Model Adaptation - Update Transition Matrix
        self.predictor.update(user_move)

        # Log round record
        self.round_log.append({
            "round": self.round_number,
            "user_move": user_move,
            "ai_move": ai_move,
            "result": result,
            "predicted_user_move": predicted_user_move,
            "confidence": confidence,
            "is_random": is_random,
            "pred_correct": pred_correct
        })

        # Phase 5: Display Feedback
        self.print_round_result(user_move, ai_move, result, predicted_user_move, confidence, is_random, pred_correct)

        # Phase 6: Periodic Pattern Report every 5 rounds
        if self.round_number % 5 == 0:
            self.print_periodic_stats()

    def print_round_result(self, user_m: str, ai_m: str, result: str, pred_m: str, conf: float, is_rand: bool, pred_correct: bool):
        """Prints rich formatted round results and AI diagnostics."""
        print(f"\n{Colors.DIM}┌──────────────────────── ROUND {self.round_number} ────────────────────────┐{Colors.RESET}")
        
        # Moves display
        print(f"│  🧑 You: {Colors.BOLD}{MOVE_EMOJIS[user_m]:<14}{Colors.RESET} vs  🤖 AI: {Colors.BOLD}{MOVE_EMOJIS[ai_m]:<14}{Colors.RESET}│")
        
        # Outcome banner
        if result == "user":
            verdict = f"{Colors.GREEN}{Colors.BOLD}🎉 YOU WIN THIS ROUND!{Colors.RESET}"
        elif result == "computer":
            verdict = f"{Colors.RED}{Colors.BOLD}💀 AI WINS THIS ROUND!{Colors.RESET}"
        else:
            verdict = f"{Colors.YELLOW}{Colors.BOLD}🤝 IT'S A TIE!{Colors.RESET}"
        print(f"│  Outcome : {verdict:<43}│")

        # AI Thought Box
        if is_rand:
            ai_thought = f"{Colors.DIM}AI moved randomly (Rounds 1-3 baseline){Colors.RESET}"
        else:
            hit_symbol = f"{Colors.GREEN}✓ MATCHED{Colors.RESET}" if pred_correct else f"{Colors.RED}✗ MISSED{Colors.RESET}"
            ai_thought = (
                f"Predicted you'd pick {Colors.CYAN}{MOVE_NAMES[pred_m]}{Colors.RESET} "
                f"({Colors.BOLD}{conf}%{Colors.RESET} conf) ➔ {hit_symbol}"
            )
        print(f"│  🧠 Mind  : {ai_thought}")

        # Streak display
        if self.current_streak > 1:
            streak_str = f"{Colors.GREEN}🔥 {self.current_streak} Win Streak!{Colors.RESET}"
        elif self.current_streak < -1:
            streak_str = f"{Colors.RED}❄️ AI on {abs(self.current_streak)} Win Streak!{Colors.RESET}"
        else:
            streak_str = f"{Colors.DIM}Neutral{Colors.RESET}"

        # Scoreboard line
        score_line = (
            f"You: {Colors.GREEN}{self.user_score}{Colors.RESET} | "
            f"AI: {Colors.RED}{self.computer_score}{Colors.RESET} | "
            f"Ties: {Colors.YELLOW}{self.tie_count}{Colors.RESET} | "
            f"Streak: {streak_str}"
        )
        print(f"│  Score   : {score_line}")
        print(f"{Colors.DIM}└────────────────────────────────────────────────────────┘{Colors.RESET}")

    def print_periodic_stats(self):
        """Prints a 5-round milestone analytical summary."""
        stats = self.predictor.get_pattern_stats()
        acc = (self.ai_correct_predictions / self.round_number) * 100.0

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}╔════════════════ MILESTONE: ROUND {self.round_number} PATTERNS ═══════════════╗{Colors.RESET}")
        
        # User favorite move
        if stats["fav_move"]:
            fav_name = MOVE_NAMES[stats["fav_move"]]
            print(f"║ • Your Most Frequent Move  : {Colors.CYAN}{fav_name}{Colors.RESET} ({stats['fav_pct']}% of choices)")

        # Dominant transition
        if stats["best_trans"]:
            from_m, to_m = stats["best_trans"]
            print(f"║ • Markov Habit Detected    : After {Colors.YELLOW}{MOVE_NAMES[from_m]}{Colors.RESET} ➔ You play {Colors.CYAN}{MOVE_NAMES[to_m]}{Colors.RESET} ({stats['best_trans_pct']}%)")
        else:
            print(f"║ • Markov Habit Detected    : Gathering transition samples...")

        # AI Prediction Accuracy
        print(f"║ • Overall AI Prediction Acc: {Colors.BOLD}{acc:.1f}%{Colors.RESET} ({self.ai_correct_predictions}/{self.round_number} rounds correctly read)")
        print(f"{Colors.MAGENTA}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")

    def print_matrix_inspection(self):
        """Displays the live 3x3 Markov transition probability matrix."""
        m = self.predictor.transitions
        print(f"\n{Colors.YELLOW}{Colors.BOLD}📊 Current Markov Transition Matrix (Counts of Next Move Given Prev):{Colors.RESET}")
        print("         ➔ Next Rock    ➔ Next Paper   ➔ Next Scissors")
        for prev in MOVES:
            row = m[prev]
            print(f" Prev {MOVE_NAMES[prev]:<8}: {row['r']:^12} {row['p']:^14} {row['s']:^16}")
        print()

    def print_session_summary(self):
        """Displays full comprehensive final report on game exit."""
        if self.round_number == 0:
            print(f"\n{Colors.YELLOW}No rounds were played. See you next time!{Colors.RESET}\n")
            return

        user_pct = (self.user_score / self.round_number) * 100.0
        ai_pct = (self.computer_score / self.round_number) * 100.0
        tie_pct = (self.tie_count / self.round_number) * 100.0
        acc_pct = (self.ai_correct_predictions / self.round_number) * 100.0
        stats = self.predictor.get_pattern_stats()

        # Determine winner
        if self.user_score > self.computer_score:
            champion = f"{Colors.GREEN}{Colors.BOLD}🏆 CHAMPION: HUMAN PLAYER! Outstanding intuition!{Colors.RESET}"
        elif self.computer_score > self.user_score:
            champion = f"{Colors.RED}{Colors.BOLD}🤖 CHAMPION: MARKOV AI! The machine decoded your habits!{Colors.RESET}"
        else:
            champion = f"{Colors.YELLOW}{Colors.BOLD}⚖️ DEAD HEAT: IT'S A PERFECT DRAW!{Colors.RESET}"

        print(f"\n{Colors.CYAN}{Colors.BOLD}════════════════════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}                    FINAL SESSION REPORT CARD                   {Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}════════════════════════════════════════════════════════════════{Colors.RESET}")
        print(f" {champion}\n")
        print(f" Total Rounds Played    : {Colors.BOLD}{self.round_number}{Colors.RESET}")
        print(f" • You Won              : {Colors.GREEN}{self.user_score:<4}{Colors.RESET} ({user_pct:.1f}%)")
        print(f" • Computer Won         : {Colors.RED}{self.computer_score:<4}{Colors.RESET} ({ai_pct:.1f}%)")
        print(f" • Ties                 : {Colors.YELLOW}{self.tie_count:<4}{Colors.RESET} ({tie_pct:.1f}%)")
        print(f" • Best Win Streak      : {Colors.BOLD}{self.best_win_streak}{Colors.RESET} consecutive wins")
        print(f" • AI Prediction Rate   : {Colors.BOLD}{acc_pct:.1f}%{Colors.RESET} ({self.ai_correct_predictions}/{self.round_number} rounds predicted)")
        
        # Move distribution
        total_m = stats["total_moves"]
        if total_m > 0:
            counts = stats["move_counts"]
            r_pct = (counts['r'] / total_m) * 100
            p_pct = (counts['p'] / total_m) * 100
            s_pct = (counts['s'] / total_m) * 100
            print(f"\n {Colors.BOLD}Your Move Distribution:{Colors.RESET}")
            print(f" • Rock 🪨     : {counts['r']:<3} ({r_pct:.1f}%)")
            print(f" • Paper 📄    : {counts['p']:<3} ({p_pct:.1f}%)")
            print(f" • Scissors ✂️ : {counts['s']:<3} ({s_pct:.1f}%)")

        # Top transition
        if stats["best_trans"]:
            from_m, to_m = stats["best_trans"]
            print(f"\n {Colors.BOLD}Strongest Pattern Decoded:{Colors.RESET}")
            print(f" • When you play {Colors.YELLOW}{MOVE_NAMES[from_m]}{Colors.RESET}, you choose {Colors.CYAN}{MOVE_NAMES[to_m]}{Colors.RESET} next ({stats['best_trans_pct']}% of the time).")

        print(f"{Colors.CYAN}{Colors.BOLD}════════════════════════════════════════════════════════════════{Colors.RESET}\n")


def main():
    """Main CLI entrypoint."""
    game = RockPaperScissorsGame()
    game.print_welcome()

    while True:
        user_move = game.prompt_user_move()
        if user_move is None:
            # User chose to quit or interrupted
            game.print_session_summary()
            break
        game.play_round(user_move)


if __name__ == "__main__":
    main()
