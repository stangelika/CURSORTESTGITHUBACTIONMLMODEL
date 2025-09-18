# ML Workstation - GitHub Actions GPU Runner

Этот репозиторий демонстрирует использование self-hosted GPU runner для длительных ML экспериментов (до 72 часов).

## 🎯 Особенности

- **Self-hosted Windows runner** с GPU поддержкой
- **PyTorch 2.5.1 + CUDA** для обучения моделей  
- **Мониторинг GPU** в реальном времени
- **Артефакты** - сохранение логов, моделей, метрик
- **72-часовой timeout** для длительных экспериментов

## 🚀 Использование

1. **Ручной запуск:** Actions → ML Long Training → Run workflow
2. **Мониторинг:** Логи GPU сохраняются в `gpu_usage.csv`
3. **Артефакты:** Модели и результаты доступны после завершения

## 🔧 Технические детали

- **OS:** Windows 11 Pro
- **GPU:** NVIDIA GeForce RTX 4060 (8GB)  
- **Python:** 3.11.4
- **CUDA:** 12.9

## 📊 Структура проекта

```
├── .github/workflows/
│   └── ml-long-run.yml       # Главный workflow (72h)
├── scripts/
│   ├── gpu_monitor.py        # Мониторинг GPU
│   └── train.py              # Демо тренировка
├── experiments/              # ML эксперименты
└── requirements.txt          # Зависимости
```

Создан согласно [docs_Cursor_Agent_Next_Actions.md](docs_Cursor_Agent_Next_Actions.md)

---

## 🔄 Complete ML Workstation Automation Stack

This repository now includes a complete automation stack for ML workstation workflows.

### 🚀 Quick Start (One Command)

For Windows 11 + RTX 4060 + Python 3.11.4:

```powershell
# Run as Administrator
cd "S:\mr Lopata"
.\scripts\run_end_to_end.ps1 `
  -Repo "stangelika/CURSORTESTGITHUBACTIONMLMODEL" `
  -Pat $env:GITHUB_TOKEN `
  -Context7Key $env:CONTEXT7_API_KEY `
  -InstallRunner:$true `
  -TriggerWorkflows:$true
```

### 🛠️ New Components Added

- **Complete PowerShell automation** - End-to-end setup with one command
- **Comprehensive GPU monitoring** - Python script with NVML/nvidia-smi support  
- **MCP server automation** - Cursor setup with 5 servers (Context7, GitHub, Filesystem, SQLite, Memory)
- **Environment validation** - Pre-flight checks and troubleshooting
- **Report generation** - Automated status reports with system info
- **Log management** - Rotation and cleanup scripts
- **Test suite** - Complete validation of automation stack

### 📚 New Documentation

- **[Automation Runbook](docs/Automation_Runbook.md)** - Complete setup and usage guide
- **[Report Template](docs/Report_Template.md)** - Status reporting format

### 🔒 Security Features

- No secrets in code - uses Windows environment variables and GitHub Secrets
- Self-hosted runners with isolated labels: `[self-hosted, windows, gpu]`

See the automation components above for the complete ML workstation solution.

