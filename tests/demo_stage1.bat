@echo off
setlocal
set "HOME=%USERPROFILE%"
set "DEMO_INPUT=%TEMP%\shell_emulator_demo_%RANDOM%.txt"
> "%DEMO_INPUT%" echo ls "$HOME"
>> "%DEMO_INPUT%" echo cd "folder with spaces"
>> "%DEMO_INPUT%" echo unknown-command argument
>> "%DEMO_INPUT%" echo cd ^"unterminated
set "SHELL_EMULATOR_STARTUP=%DEMO_INPUT%"
python "%~dp0..\run.py"
if errorlevel 1 echo Could not run the demo. Check that Python is installed.
set "SHELL_EMULATOR_STARTUP="
del "%DEMO_INPUT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
