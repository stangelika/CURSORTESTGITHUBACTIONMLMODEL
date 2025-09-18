# Docker Desktop - Автоматическая установка для AMD64
# Скрипт для быстрой установки Docker Desktop на Windows AMD64

Write-Host "🐳 Установка Docker Desktop для AMD64..." -ForegroundColor Green
Write-Host ""

# Проверяем архитектуру
$arch = $env:PROCESSOR_ARCHITECTURE
Write-Host "💻 Архитектура процессора: $arch" -ForegroundColor Cyan

if ($arch -ne "AMD64") {
    Write-Host "⚠️ Внимание: Этот скрипт для AMD64, у вас $arch" -ForegroundColor Yellow
    Write-Host "Продолжить? (y/n): " -NoNewline
    $continue = Read-Host
    if ($continue -ne "y") {
        Write-Host "❌ Установка отменена" -ForegroundColor Red
        exit
    }
}

# URL для скачивания Docker Desktop AMD64
$dockerUrl = "https://desktop.docker.com/win/stable/amd64/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"

Write-Host "📥 Скачивание Docker Desktop..." -ForegroundColor Yellow
Write-Host "   URL: $dockerUrl"
Write-Host "   Путь: $installerPath"
Write-Host ""

try {
    # Скачивание
    Write-Host "⬇️ Загрузка файла..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing
    
    if (Test-Path $installerPath) {
        $fileSize = [math]::Round((Get-Item $installerPath).Length / 1MB, 2)
        Write-Host "✅ Загружено успешно! Размер: $fileSize MB" -ForegroundColor Green
        Write-Host ""
        
        # Запуск установщика
        Write-Host "🚀 Запуск установщика Docker Desktop..." -ForegroundColor Green
        Write-Host "💡 Следуйте инструкциям установщика" -ForegroundColor Yellow
        Write-Host ""
        
        Start-Process -FilePath $installerPath -Wait
        
        Write-Host "✅ Установщик завершен!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔄 Следующие шаги:" -ForegroundColor Cyan
        Write-Host "1. Перезагрузите компьютер если потребуется" -ForegroundColor White
        Write-Host "2. Запустите Docker Desktop из меню Пуск" -ForegroundColor White  
        Write-Host "3. Дождитесь полной загрузки Docker" -ForegroundColor White
        Write-Host "4. Проверьте: docker --version" -ForegroundColor White
        Write-Host "5. Запустите: python scripts/check_mcp_setup.py" -ForegroundColor White
        
        # Очистка
        Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
        
    } else {
        Write-Host "❌ Ошибка: Файл не был загружен" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Ошибка при скачивании: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Альтернативные варианты:" -ForegroundColor Yellow
    Write-Host "1. Скачайте вручную: https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    Write-Host "2. Или используйте winget: winget install Docker.DockerDesktop" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 После установки Docker вернитесь к настройке GitHub MCP!" -ForegroundColor Green





