@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_stage5_load_error_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage5_load_error_%RANDOM%.txt"
mkdir "%VFS_ROOT%"
> "%VFS_ROOT%\keep.txt" echo Original VFS file.
> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo vfs-load "%VFS_ROOT%\missing"
>> "%DEMO_INPUT%" echo echo skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
