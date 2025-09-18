# Cursor + MCP + ML Workstation — Полная автоматизация (Runbook)

Цель: максимально автоматизировать настройку и эксплуатацию среды для научной ML‑работы:
- Cursor (MCP) с 5 серверами
- GPU стек (PyTorch CUDA, опц. TF)
- GitHub Actions (self‑hosted GPU runner, длительные запуски до 72ч)
- Автоматические проверки, отчёты, мониторинг, ротация логов

Минимальные требования:
- Windows 11 Pro, RTX 4060 (8 GB), NVIDIA Driver ~577.00, CUDA 12.x
- Python 3.11.4
- Docker Desktop 28.x+
- GitHub PAT c правами repo + workflow
- Путь базовой директории: S:\\mr Lopata\\

ВАЖНО (безопасность):
- Никогда не коммитьте секреты в repo/конфиги. Хранение только в Windows Env и GitHub Secrets.

Содержание:
- 01. Секреты и безопасность
- 02. Быстрый старт (1 команда)
- 03. Переменные окружения (env) и проверка
- 04. MCP автоматизация (5 серверов)
- 05. GitHub Actions: self‑hosted runner (полная автоинсталляция)
- 06. Workflows: короткие и 72ч
- 07. GPU/ML стек и TensorFlow стратегия
- 08. Мониторинг, отчёты, ротация
- 09. Тесты "end‑to‑end"
- 10. Траблшутинг

## 02. Быстрый старт (1 команда)
Запуск (PowerShell от администратора):
```
cd "S:\\mr Lopata"
.\\scripts\\run_end_to_end.ps1 `
  -Repo "stangelika/CURSORTESTGITHUBACTIONMLMODEL" `
  -Pat "`<PAT_TOKEN>`" `
  -Context7Key "<KEY|''>" `
  -InstallRunner:$true `
  -RunnerDir "C:\\actions-runner" `
  -RunnerLabels "self-hosted,windows,gpu" `
  -StartCursorPath "C:\\Users\\<YOU>\\AppData\\Local\\Programs\\cursor\\Cursor.exe" `
  -TriggerWorkflows:$true
```

Подробности, проверки и траблшутинг — ниже.