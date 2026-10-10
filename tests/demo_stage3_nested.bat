@echo off
setlocal
set "VFS_ROOT=%TEMP%\shell_emulator_vfs_nested_%RANDOM%"
set "DEMO_INPUT=%TEMP%\shell_emulator_stage3_nested_%RANDOM%.txt"
mkdir "%VFS_ROOT%\level1\level2\level3"
> "%VFS_ROOT%\root.txt" echo Root-level file.
> "%VFS_ROOT%\level1\level2\level3\deep.txt" echo File at level three.
> "%DEMO_INPUT%" echo ls
>> "%DEMO_INPUT%" echo cd "level1"
>> "%DEMO_INPUT%" echo cd "level2"
>> "%DEMO_INPUT%" echo cd "level3"
>> "%DEMO_INPUT%" echo unknown-command nested-error
>> "%DEMO_INPUT%" echo cd skipped-after-error
call "%~dp0..\run.bat" --vfs "%VFS_ROOT%" --script "%DEMO_INPUT%"
del "%DEMO_INPUT%"
rmdir /s /q "%VFS_ROOT%"
echo.
echo CLI finished. Press any key to close this window.
pause >nul
