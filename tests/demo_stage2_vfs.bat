@echo off
setlocal
call "%~dp0..\run.bat" --vfs "%USERPROFILE%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
