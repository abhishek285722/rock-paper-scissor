# 🎮 Task 6 — AI-Based Rock, Paper, Scissors Game (Markov Chain AI)

An intelligent, terminal-based Rock, Paper, Scissors game powered by an adaptive **1st-Order Markov Chain** prediction model.

---

## 📌 Project Overview

This project implements **Task 6 (AI-Based Rock, Paper, Scissors)**:
- **Core Technology**: Pure Python with native ANSI terminal formatting and optional `colorama`.
- **Machine Learning Engine**: 3×3 Transition Frequency Matrix (Markov Chain) tracking human psychological patterns.
- **Fair Play Architecture**: The AI calculates its prediction and locks in its counter-move **before** the user's choice is revealed.
- **Diagnostics & Insights**: Real-time confidence ratings, streak tracking, 5-round milestone habit summaries, live matrix inspection, and a comprehensive end-of-session report card.

---

## 🧠 How the AI Works

Humans are notoriously bad at generating true randomness. When playing Rock, Paper, Scissors, human players exhibit consistent psychological biases:
- Repeating moves after winning.
- Cycling sequentially (Rock ➔ Paper ➔ Scissors).
- Switching away from losing moves.

### The 3×3 Markov Transition Matrix
The AI maps these behavioral habits by constructing a frequency matrix where:
- **Rows**: The move you played in the previous round ($t-1$).
- **Columns**: The move you choose in the current round ($t$).

$$\text{Matrix} = \begin{pmatrix} 
N(R \to R) & N(R \to P) & N(R \to S) \\
N(P \to R) & N(P \to P) & N(P \to S) \\
N(S \to R) & N(S \to P) & N(S \to S) 
\end{pmatrix}$$

### Decision Lifecycle
1. **Rounds 1–3 (Cold Start)**: The AI plays pseudo-random moves to establish an unbiased baseline while silently observing your opening choices.
2. **Round 4+ (Active Learning)**:
   - Identifies your last move ($m_{t-1}$).
   - Queries row $m_{t-1}$ in the transition matrix.
   - Selects the column with the highest transition frequency as the **Predicted Move**.
   - Calculates **Confidence** as $\frac{\text{max count}}{\sum \text{transitions for } m_{t-1}} \times 100\%$.
   - Locks in the **winning counter** to that predicted move.
3. **Model Adaptation**: After every round, the matrix updates: $\text{Matrix}[m_{t-1}][m_t] \mathrel{+}= 1$.

---

## ✨ Features & Enhancements

- 🔒 **Provable Fair Play**: The AI locks in its prediction before prompting the user for input.
- 🎯 **Dynamic Confidence Rating**: Shows how sure the AI was about your choice (e.g., *80.0% confidence*).
- 🔥 **Win/Loss Streak Tracking**: Real-time detection of consecutive user victories or AI winning sprees.
- 📊 **Milestone Habit Reports**: Every 5 rounds, an analytical card displays your most frequent move, your strongest decoded transition habit, and the AI's overall accuracy.
- 🔍 **Live Matrix Inspection**: Type `m` at any prompt to view the live 3×3 transition matrix in real time.
- 📋 **Final Session Report**: On quitting (`q`), a full report card summarizes win rates, move percentages, best streak, and declares the ultimate champion.

---

## 📁 Project Structure

```
rock paper scissor/
│
├── game.py             # Complete game engine, Markov predictor & CLI interface
├── test_game.py        # Automated unit test suite (6 test cases)
├── run.bat             # One-click Windows batch launcher (UTF-8 enabled)
├── run.sh              # One-click Linux / macOS launcher
├── requirements.txt    # Optional terminal formatting dependency (colorama)
├── .gitignore          # Git exclusion rules
└── README.md           # Documentation
```

---

## 🚀 How to Run

### Option 1: One-Click Launcher (Recommended)
- **Windows**: Double-click [`run.bat`](file:///c:/Users/mymai/OneDrive/Desktop/projects/rock%20paper%20scissor/run.bat)
- **macOS / Linux**: Run `bash run.sh` in your terminal

### Option 2: Direct Command Line
```bash
python game.py
```

### Controls During Gameplay
| Key | Action |
|---|---|
| `r` | Play **Rock** 🪨 |
| `p` | Play **Paper** 📄 |
| `s` | Play **Scissors** ✂️ |
| `m` | Inspect live **Markov Transition Matrix** |
| `q` | **Quit** and display Final Session Report Card |

---

## 🧪 Automated Testing

To run the automated unit test suite verifying outcome resolution, counter-moves, Markov matrix updates, and streak tracking:

```bash
python test_game.py
```

All tests execute in `< 0.01s`.
