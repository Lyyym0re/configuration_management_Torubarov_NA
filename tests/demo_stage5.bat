@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_stage5_a_%RANDOM%"
set "VFS_NEXT=%TEMP%\shell_emulator_stage5_b_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage5_%RANDOM%.txt"
mkdir "%VFS_ROOT%\docs"
mkdir "%VFS_ROOT%\spare\nested"
mkdir "%VFS_NEXT%\new folder"
> "%VFS_ROOT%\docs\old.txt" echo Old document.
> "%VFS_ROOT%\spare\nested\deep.txt" echo Deep file.
> "%VFS_ROOT%\keep.txt" echo Keep this file.
> "%VFS_NEXT%\new folder\note.txt" echo New document.
> "%VFS_NEXT%\fresh.txt" echo Fresh file.
> "%DEMO_INPUT%" echo echo Stage 5 commands
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo tree
>> "%DEMO_INPUT%" echo cd docs
>> "%DEMO_INPUT%" echo rm old.txt
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo cd /
>> "%DEMO_INPUT%" echo rm -r spare
>> "%DEMO_INPUT%" echo tree
>> "%DEMO_INPUT%" echo vfs-load "%VFS_NEXT%"
>> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo cd "new folder"
>> "%DEMO_INPUT%" echo rm note.txt
>> "%DEMO_INPUT%" echo tree /
>> "%DEMO_INPUT%" echo cd /
>> "%DEMO_INPUT%" echo rm missing.txt
>> "%DEMO_INPUT%" echo echo skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
if exist "%VFS_ROOT%\docs\old.txt" echo Source file is still on disk.
if exist "%VFS_ROOT%\spare\nested\deep.txt" echo Source tree is intact.
if exist "%VFS_NEXT%\new folder\note.txt" echo New source is intact.
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
rmdir /s /q "%VFS_NEXT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
