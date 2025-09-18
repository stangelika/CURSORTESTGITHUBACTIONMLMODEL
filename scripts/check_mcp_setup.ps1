# GitHub MCP Setup Checker for Windows
# Проверка настройки MCP серверов

Write-Host "🚀 Проверка настройки MCP серверов" -ForegroundColor Green
Write-Host ""

$allPassed = $true

# Проверка Docker
Write-Host "🐳 Проверка Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker установлен: $dockerVersion" -ForegroundColor Green
        
        # Проверка что Docker запущен
        $dockerPs = docker ps 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker запущен и работает" -ForegroundColor Green
        } else {
            Write-Host "❌ Docker установлен, но не запущен" -ForegroundColor Red
            Write-Host "💡 Запустите Docker Desktop" -ForegroundColor Yellow
            $allPassed = $false
        }
    } else {
        throw "Docker не найден"
    }
} catch {
    Write-Host "❌ Docker не установлен или не запущен" -ForegroundColor Red
    Write-Host "💡 Установите Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    $allPassed = $false
}

# Проверка конфигурации MCP
Write-Host ""
Write-Host "⚙️ Проверка конфигурации MCP..." -ForegroundColor Cyan

if (Test-Path ".vscode\mcp.json") {
    try {
        $config = Get-Content ".vscode\mcp.json" | ConvertFrom-Json
        
        if ($config.servers -and $config.servers.github) {
            Write-Host "✅ Конфигурация GitHub MCP найдена" -ForegroundColor Green
            
            if ($config.servers.github.command -eq "docker") {
                Write-Host "✅ Настроен запуск через Docker" -ForegroundColor Green
            }
            
            $toolsets = $config.servers.github.env.GITHUB_TOOLSETS
            if ($toolsets) {
                Write-Host "✅ Наборы инструментов: $toolsets" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ Конфигурация GitHub MCP не найдена" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "❌ Ошибка в JSON конфигурации" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "❌ Файл .vscode\mcp.json не найден" -ForegroundColor Red
    $allPassed = $false
}

# Проверка правил Cursor
Write-Host ""
Write-Host "📋 Проверка правил Cursor..." -ForegroundColor Cyan

if (Test-Path "cursorrules.txt") {
    $rules = Get-Content "cursorrules.txt" -Raw
    if ($rules -like "*GitHub MCP*") {
        Write-Host "✅ Правила для GitHub MCP найдены" -ForegroundColor Green
    } else {
        Write-Host "❌ Правила для GitHub MCP не найдены" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "❌ Файл cursorrules.txt не найден" -ForegroundColor Red
    $allPassed = $false
}

# Загрузка Docker образа
if ($allPassed) {
    Write-Host ""
    Write-Host "📥 Загрузка Docker образа GitHub MCP..." -ForegroundColor Cyan
    try {
        docker pull ghcr.io/github/github-mcp-server 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker образ GitHub MCP загружен" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Образ не удалось загрузить, но настройки готовы." -ForegroundColor Yellow
            Write-Host "Docker загрузит образ автоматически при первом использовании." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Образ не удалось загрузить, но настройки готовы." -ForegroundColor Yellow
        Write-Host "Docker загрузит образ автоматически при первом использовании." -ForegroundColor Yellow
    }
}

Write-Host ""

if ($allPassed) {
    Write-Host "🎯 Все проверки прошли успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ Настройка завершена! Следующие шаги:" -ForegroundColor Green
    Write-Host "1. Перезапустите Cursor" -ForegroundColor White
    Write-Host "2. Получите GitHub Personal Access Token (см. GITHUB_MCP_SETUP.md)" -ForegroundColor White
    Write-Host "3. Начните новый чат и попробуйте: 'Покажи информацию о репозитории'" -ForegroundColor White
} else {
    Write-Host "❌ Некоторые проверки не прошли. Исправьте ошибки и запустите снова." -ForegroundColor Red
    exit 1
}





