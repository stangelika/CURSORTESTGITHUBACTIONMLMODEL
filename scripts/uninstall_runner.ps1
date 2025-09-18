param(
  [string]$InstallDir = "C:\actions-runner"
)

if (-not (Test-Path $InstallDir)) {
  Write-Host "Каталог $InstallDir не найден."
  exit 0
}

Set-Location $InstallDir
Write-Host "Останавливаю сервис ..."
cmd /c ".\svc stop" | Out-Null
Write-Host "Удаляю сервис ..."
cmd /c ".\svc uninstall" | Out-Null

Write-Host "Удаляю регистрацию раннера (может спросить подтверждение) ..."
cmd /c ".\config.cmd remove" 

Write-Host "Чищу каталог ..."
Set-Location \
Remove-Item -Recurse -Force $InstallDir

Write-Host "Готово."







