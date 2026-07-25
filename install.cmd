@echo off
setlocal
title Anime Wallpaper Upscaler Setup

echo Anime Wallpaper Upscaler - one-click setup
echo The installer will show upstream sources and license terms before downloading anything.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
set "AUPS_EXIT=%ERRORLEVEL%"

if not "%AUPS_EXIT%"=="0" (
  echo.
  echo Setup did not complete. Read the repair message above, then run install.cmd again.
  pause
  exit /b %AUPS_EXIT%
)

echo.
echo Setup complete. You can now drag images or folders onto the desktop shortcut.
pause
exit /b 0
