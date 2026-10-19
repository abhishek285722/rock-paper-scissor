#!/usr/bin/env bash
echo "======================================================"
echo "       AI-Based Rock, Paper, Scissors Game"
echo "           Adaptive Markov Chain Engine"
echo "======================================================"
echo ""

# Optional dependency check
python3 -c "import colorama" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[Checking dependencies...]"
    python3 -m pip install -r requirements.txt
fi

echo "[Starting game session...]"
python3 game.py
