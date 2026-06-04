@echo off
setlocal
cd /d "%~dp0"

set "OUT=GILL_VEDIO_sender_fast.zip"
if exist "%OUT%" del /f /q "%OUT%"

rem Use 7-Zip if available (faster + more reliable on Windows)
set "SEVENZIP=%ProgramFiles%\7-Zip\7z.exe"
if exist "%SEVENZIP%" (
  "%SEVENZIP%" a -tzip "%OUT%" . -xr!build -xr!dist -xr!__pycache__ -xr!.git -xr!*.zip -mx=9
  echo Created: %OUT%
  goto :eof
)

rem Fallback to built-in PowerShell Compress-Archive
powershell -NoProfile -ExecutionPolicy Bypass -Command "$zip='GILL_VEDIO_sender_fast.zip'; if(Test-Path $zip){Remove-Item $zip -Force}; $items=Get-ChildItem -Force | Where-Object { $_.Name -notlike 'GILL_VEDIO_sender_fast.zip' -and $_.Name -notlike '*.zip' -and $_.Name -ne 'build' -and $_.Name -ne 'dist' -and $_.Name -ne '__pycache__' -and $_.Name -ne '.git' }; Compress-Archive -Path ($items | Select-Object -ExpandProperty FullName) -DestinationPath $zip -Force; Write-Host ('Created: '+(Resolve-Path $zip))"
endlocal

