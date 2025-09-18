param(
  [string]$RepoUrl = "https://github.com/stangelika/ml-monitoring",
  [string]$Token,                           # ОБЯЗАТЕЛЬНО: registration token со страницы New self-hosted runner
  [string]$RunnerZipUrl = "",               # Необязательно: если пусто — попросим вставить вручную
  [string]$InstallDir = "C:\actions-runner",
  [string]$Labels = "self-hosted,Windows,X64"
)

if (-not $Token) {
  Write-Error "Не указан -Token. Возьми его на GitHub: Repo → Settings → Actions → Runners → New self-hosted → Windows."
  exit 1
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Set-Location $InstallDir

if ([string]::IsNullOrWhiteSpace($RunnerZipUrl)) {
  Write-Host "Открой страницу New self-hosted runner (Windows x64) и скопируй ссылку на ZIP. Вставь её сюда:"
  $RunnerZipUrl = Read-Host "Runner ZIP URL"
}

$zip = "actions-runner-win-x64.zip"
Write-Host "Скачиваю $RunnerZipUrl ..."
Invoke-WebRequest -Uri $RunnerZipUrl -OutFile $zip
Expand-Archive -Path $zip -DestinationPath . -Force

Write-Host "Регистрирую раннер для $RepoUrl ..."
cmd /c ".\config.cmd --url $RepoUrl --token $Token --labels `"$Labels`" --unattended"

Write-Host "Устанавливаю и запускаю сервис ..."
cmd /c ".\svc install"
cmd /c ".\svc start"

Write-Host "Готово. Проверь статус в репозитории: Settings → Actions → Runners (должен быть Online / Idle)."







