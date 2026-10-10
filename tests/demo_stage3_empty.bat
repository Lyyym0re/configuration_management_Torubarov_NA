@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_vfs_empty_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage3_empty_%RANDOM%.txt"
mkdir "%VFS_ROOT%"
> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo cd "empty root"
>> "%DEMO_INPUT%" echo unknown-command argument
>> "%DEMO_INPUT%" echo cd skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
