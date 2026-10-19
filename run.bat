@echo off
chcp 65001 >nul
title AI-Based Rock, Paper, Scissors Game (Markov AI)
echo ======================================================
echo       AI-Based Rock, Paper, Scissors Game
echo           Adaptive Markov Chain Engine
echo ======================================================
echo.

:: Optional: Fast check for colorama
python -c "import colorama" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Checking dependencies...]
    python -m pip install -r requirements.txt
)

echo [Starting game session...]
echo ======================================================
echo  * Controls: 'r' for Rock, 'p' for Paper, 's' for Scissors
echo  * Type 'm' to inspect the live Markov transition matrix
echo  * Type 'q' to end the session and view full report card
echo ======================================================
echo.

python game.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Game terminated unexpectedly (code: %ERRORLEVEL%).
)

echo.
pause
