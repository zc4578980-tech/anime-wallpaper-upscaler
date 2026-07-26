@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-wallpaper.ps1" %*
set "AUPS_EXIT=%errorlevel%"
if not "%AUPS_EXIT%"=="0" pause
exit /b %AUPS_EXIT%
