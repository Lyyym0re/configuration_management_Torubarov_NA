@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_vfs_files_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage3_files_%RANDOM%.txt"
mkdir "%VFS_ROOT%"
mkdir "%VFS_ROOT%\inner"
> "%VFS_ROOT%\readme.txt" echo Sample text file.
> "%VFS_ROOT%\file with spaces.txt" echo A file with spaces in its name.
> "%VFS_ROOT%\inner\note.txt" echo Another sample file.
> "%DEMO_INPUT%" echo ls "$HOME"
>> "%DEMO_INPUT%" echo cd "file with spaces.txt"
>> "%DEMO_INPUT%" echo cd ^"unterminated
>> "%DEMO_INPUT%" echo cd skipped-after-error
set "HOME=%USERPROFILE%"
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
