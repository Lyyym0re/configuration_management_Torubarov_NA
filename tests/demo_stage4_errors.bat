@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_vfs_stage4_errors_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage4_errors_%RANDOM%.txt"
mkdir "%VFS_ROOT%\docs"
> "%VFS_ROOT%\file.txt" echo Sample file.
> "%DEMO_INPUT%" echo ls missing.txt
>> "%DEMO_INPUT%" echo echo skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
