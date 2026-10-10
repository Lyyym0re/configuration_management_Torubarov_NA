@echo off
setlocal
set "HOME=%USERPROFILE%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage2_all_%RANDOM%.txt"
> "%DEMO_INPUT%" echo ls "$HOME"
>> "%DEMO_INPUT%" echo cd "folder with spaces"
>> "%DEMO_INPUT%" echo unknown-command argument
>> "%DEMO_INPUT%" echo cd should-not-run
call "%~dp0..\run.bat" --vfs "%USERPROFILE%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
