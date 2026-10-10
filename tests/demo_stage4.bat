@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_vfs_stage4_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage4_%RANDOM%.txt"
set "HOME=%USERPROFILE%"
mkdir "%VFS_ROOT%\docs\deep\level3"
mkdir "%VFS_ROOT%\folder with spaces"
> "%VFS_ROOT%\root.txt" echo Root file.
> "%VFS_ROOT%\docs\guide.txt" echo Guide file.
> "%VFS_ROOT%\docs\deep\level3\leaf.txt" echo Deep file.
> "%VFS_ROOT%\folder with spaces\note.txt" echo File with spaces.
> "%DEMO_INPUT%" echo echo Stage 4 commands
>> "%DEMO_INPUT%" echo echo "$HOME"
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo ls docs
>> "%DEMO_INPUT%" echo ls root.txt
>> "%DEMO_INPUT%" echo tree
>> "%DEMO_INPUT%" echo cd docs
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo cd deep/level3
>> "%DEMO_INPUT%" echo tree /
>> "%DEMO_INPUT%" echo cd ../..
>> "%DEMO_INPUT%" echo cd /
>> "%DEMO_INPUT%" echo cd "folder with spaces"
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo echo "quoted text" from VFS
>> "%DEMO_INPUT%" echo cd /
>> "%DEMO_INPUT%" echo unknown-command example
>> "%DEMO_INPUT%" echo echo skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
