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
