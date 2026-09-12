@echo off
echo === Batch Generate Card Art (Arknights Style) ===
echo.
echo Usage:
echo   generate_cards.bat        - Generate missing cards only
echo   generate_cards.bat --force - Regenerate ALL cards
echo.
python "%~dp0batch_generate_cards.py" %*
echo.
pause