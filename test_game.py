import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from game import (
    determine_winner,
    MarkovPredictor,
    RockPaperScissorsGame,
    COUNTERS,
    BEATS,
    MOVES
)


class TestRockPaperScissors(unittest.TestCase):

    def test_determine_winner(self):
        """Validates all 9 combinations of Rock, Paper, Scissors."""
        # Ties
        self.assertEqual(determine_winner("r", "r"), "tie")
        self.assertEqual(determine_winner("p", "p"), "tie")
        self.assertEqual(determine_winner("s", "s"), "tie")

        # User wins
        self.assertEqual(determine_winner("r", "s"), "user")  # Rock beats Scissors
        self.assertEqual(determine_winner("s", "p"), "user")  # Scissors beats Paper
        self.assertEqual(determine_winner("p", "r"), "user")  # Paper beats Rock

        # Computer wins
        self.assertEqual(determine_winner("r", "p"), "computer")  # Paper beats Rock
        self.assertEqual(determine_winner("p", "s"), "computer")  # Scissors beats Paper
        self.assertEqual(determine_winner("s", "r"), "computer")  # Rock beats Scissors

    def test_counter_rules(self):
        """Verifies winning counters guarantee a victory against the target."""
        for target_move in MOVES:
            counter_move = COUNTERS[target_move]
            # Counter move played against target_move should result in counter_move winning
            self.assertEqual(determine_winner(counter_move, target_move), "user")

    def test_markov_baseline_rounds(self):
        """Rounds 1-3 should flag is_random=True."""
        predictor = MarkovPredictor()
        for r in [1, 2, 3]:
            pred, conf, is_random = predictor.predict(round_number=r)
            self.assertTrue(is_random)
            self.assertEqual(conf, 33.3)
            self.assertIn(pred, MOVES)

    def test_markov_pattern_learning(self):
        """
        After training the Markov chain with a repeating habit:
        e.g., 'r' -> always followed by 'p'
        Round 4+ should predict 'p' after 'r' with 100% confidence.
        """
        predictor = MarkovPredictor()

        # Simulate user sequence: r -> p -> r -> p
        predictor.update("r")
        predictor.update("p")
        predictor.update("r")
        predictor.update("p")

        # Last move was 'p'. Let's update with 'r' so last move is 'r'
        predictor.update("r")

        # Now predict for round 6 (last move was 'r')
        pred, conf, is_random = predictor.predict(round_number=6)
        self.assertFalse(is_random)
        self.assertEqual(pred, "p")  # User always played 'p' after 'r'
        self.assertEqual(conf, 100.0)

    def test_markov_stats(self):
        """Validates pattern extraction logic."""
        predictor = MarkovPredictor()
        predictor.update("r")
        predictor.update("r")
        predictor.update("r")

        stats = predictor.get_pattern_stats()
        self.assertEqual(stats["fav_move"], "r")
        self.assertEqual(stats["fav_pct"], 100.0)
        self.assertEqual(stats["best_trans"], ("r", "r"))
        self.assertEqual(stats["best_trans_count"], 2)

    def test_game_engine_streaks(self):
        """Tests streak progression in RockPaperScissorsGame."""
        game = RockPaperScissorsGame()

        # Simulate round 1 user win
        game.predictor.predict = lambda r: ("s", 50.0, False)  # AI plays COUNTERS['s'] = 'r'
        # To make user win, user plays 'p' (Paper beats Rock)
        game.play_round("p")
        self.assertEqual(game.user_score, 1)
        self.assertEqual(game.current_streak, 1)
        self.assertEqual(game.best_win_streak, 1)

        # Round 2 user win
        game.predictor.predict = lambda r: ("s", 50.0, False)
        game.play_round("p")
        self.assertEqual(game.user_score, 2)
        self.assertEqual(game.current_streak, 2)
        self.assertEqual(game.best_win_streak, 2)

        # Round 3 computer win -> streak should flip to -1
        game.predictor.predict = lambda r: ("p", 50.0, False)  # AI plays COUNTERS['p'] = 's'
        game.play_round("p")  # User plays 'p', AI played 's', AI wins
        self.assertEqual(game.computer_score, 1)
        self.assertEqual(game.current_streak, -1)
        self.assertEqual(game.best_win_streak, 2)  # Best preserved


if __name__ == "__main__":
    unittest.main()
