@echo off
setlocal
set "HOME=%USERPROFILE%"
set "DEMO_INPUT=%TEMP%\shell_emulator_demo_%RANDOM%.txt"
(
    echo ls "$HOME"
    echo cd "folder with spaces"
    echo unknown-command argument
    echo cd ^"unterminated
) > "%DEMO_INPUT%"
python "%~dp0..\run.py" < "%DEMO_INPUT%"
del "%DEMO_INPUT%"
