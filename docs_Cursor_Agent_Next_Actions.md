# Cursor + MCP + ML Workstation — Дальнейшие действия (пошагово для агента)

Цель: довести установку до “топовой” конфигурации для научной работы по ML: разработка и обучение моделей (GPU), длительные эксперименты до 72ч с мониторингом и артефактами, интеграция с GitHub Actions (self‑hosted GPU runner), безопасность секретов и воспроизводимость.

Дата лога: 2025‑09‑18 19:23–19:32  
Окружение: Windows 11 Pro, 32 GB RAM, RTX 4060 (8 GB), CUDA 12.9, Python 3.11.4, Cursor 1.6.27

---

## 0) Краткий статус по логу (исходные данные для этого плана)

Уже выполнено:
- Структура логирования и каталогов S:\mr Lopata\ — OK
- ОС/GPU/CUDA — OK (Driver 577.00, CUDA 12.9, 8 GB VRAM)
- Энергоплан — “Высокая производительность” — OK
- Docker 28.4.0 — OK
- Cursor 1.6.27 — определён, конфиги MCP приведены в порядок, Context7 ключ вынесен в env — OK
- Python 3.11.4 — OK
- PyTorch 2.5.1+cu121 (GPU) — OK
- pandas 2.3.2, scikit‑learn 1.7.2, matplotlib 3.10.6, JupyterLab 4.4.7 — OK

Осталось:
- Завершить тестирование MCP серверов (в т.ч. GitHub MCP — создать и подключить GITHUB_TOKEN)
- TensorFlow: GPU не виден (CPU‑only) — определить стратегию (см. Раздел 3)
- Исследовательское окружение (шаблон проектов, Jupyter) — довести
- GitHub Actions: self‑hosted GPU runner, длительный workflow, мониторинг
- Безопасность: PAT/Secrets/Env
- Финальные тесты и выпуск артефактов (отчёт, логи, шаблоны)

---

## 1) MCP: финальное тестирование 5 серверов и доводка

Цель: все 5 серверов видны и работоспособны в Cursor без ошибок.

Шаги:
1. Проверить JSON в S:\mr Lopata\.cursor\mcp\ (servers.json и отдельные *.json) на валидность.
   - Вставить результаты проверки в итоговый отчёт (OK/FAIL с причиной).
2. Context7:
   - Убедиться, что ключ хранится в переменных окружения (например, CONTEXT7_API_KEY), а не в файлах.
   - Тест в новом чате Cursor: “Покажи примеры React хуков” — должен отвечать без ошибок.
3. Filesystem / SQLite / Memory (NPX):
   - Убедиться, что инструменты появляются внизу окна Cursor (иконки MCP).
   - Тестовые запросы:
     - Filesystem: “Прочитай файл package.json” (или любой реальный файл).
     - SQLite: “Покажи схему таблиц в <путь к БД>” (если БД есть).
     - Memory: “Запомни моё имя <X>”, затем “Как меня зовут?”.
4. GitHub MCP (Docker):
   - Создать PAT (см. Раздел 5 “Безопасность”) и положить в переменные окружения Windows (GITHUB_TOKEN).
   - Перезапустить Cursor (закрыть все процессы, ждать 3–4 мин после старта).
   - Тест: “Покажи мои репозитории” или “Покажи открытые Issues в <owner/repo>”.
   - Критерий: операции проходят, ошибок “Tool not found”/“auth” нет.

Критерии приёмки:
- Все 5 MCP серверов отображаются в Cursor и успешно выполняют тестовые запросы.
- Секреты отсутствуют в конфигурационных файлах, хранятся только в env.

Подсказка по env (Win, для текущего пользователя):
- Открыть PowerShell “От имени администратора” и выполнить:
  ```
  setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  setx CONTEXT7_API_KEY "xxxxx"
  ```
  После — полностью перезапустить Cursor.

---

## 2) Доведение исследовательского окружения (папки, шаблоны, Jupyter)

Цель: получить удобный шаблон для экспериментов с логами, метриками и моделями.

Шаги:
1. В S:\mr Lopata\ или в выбранном рабочем репозитории подготовить структуру:
   ```
   experiments/
   ├─ configs/
   ├─ data/
   ├─ models/
   ├─ notebooks/
   ├─ results/
   └─ src/
   ```
2. Создать шаблонный PyTorch train‑скрипт (минимальная CNN/MLP на MNIST/CIFAR10) и проверить запуск на GPU:
   - Логи и чекпоинты класть в experiments/results и experiments/models соответственно.
3. JupyterLab:
   - Проверить запуск: `jupyter lab` (в логе — URL/порт).
   - Создать пример ноутбука в notebooks/ c коротким GPU‑тестом и минимальным обучением.
4. Зафиксировать версии пакетов в requirements.txt/pyproject.toml (рекомендация — продублировать список используемых библиотек и их версии для воспроизводимости).

Критерии приёмки:
- Пример обучения на GPU успешно проходит и сохраняет артефакты (лог, метрики, чекпоинт модели).
- В репозитории/каталоге есть requirements.txt с согласованными версиями.

---

## 3) TensorFlow GPU: выбрать стратегию и реализовать

На Windows с потребительскими GPU оптимальные варианты:
- Вариант A (рекомендуется для Windows): tensorflow‑directml
  - Команды:
    ```
    python -m pip uninstall -y tensorflow tensorflow-intel
    python -m pip install tensorflow-directml
    ```
  - Тест:
    ```python
    import tensorflow as tf
    print("TF:", tf.__version__)
    print("Physical devices:", tf.config.list_physical_devices())
    print("GPUs:", tf.config.list_physical_devices('GPU'))
    ```
  - Ожидание: появится устройство GPU через D3D12/DML. Производительность хорошая для многих задач.
- Вариант B: WSL2 (Ubuntu) + CUDA + официальный TF GPU (Linux)
  - Установка WSL2: `wsl --install -d Ubuntu` (перезагрузка)
  - Внутри WSL: установить CUDA Toolkit/NVIDIA Container Toolkit по официальной инструкции, поставить `tensorflow` (Linux wheels).
  - Плюсы: официальная линуксовая поддержка TF GPU; Минусы: сложнее интеграция с Windows‑инструментами, потребуется хранить данные в доступных путях.
- Вариант C: Оставить TF CPU‑only
  - Если PyTorch закрывает все GPU‑задачи и TF нужен эпизодически для инференса/экспериментов, можно отложить.

Выбрать Вариант A по умолчанию (быстрее и проще на Windows). Отразить выбор и результат теста в итоговом отчёте.

Критерии приёмки:
- Либо TF видит “GPU” (через DirectML) и простая модель обучается, либо задокументировано, что TF сознательно оставлен CPU‑only (с обоснованием).

---

## 4) GitHub Actions: self‑hosted GPU runner на Windows + длительные эксперименты (72ч)

Цель: длительные джобы до 72 часов, доступ к GPU, мониторинг GPU и сохранение артефактов.

Шаги:
1. Зарегистрировать self‑hosted runner в выбранном репозитории (Settings → Actions → Runners → New self‑hosted runner → Windows).
   - Распаковать архив, выполнить `config.cmd`
   - Ввести URL репо и токен регистрации (из UI GitHub)
   - Добавить метки: `self-hosted`, `windows`, `gpu`
   - Установить сервис:
     ```
     .\svc install
     .\svc start
     ```
   - Убедиться, что Runner “online”.
2. Энергосхема и стабильность 72ч:
   - Убедиться, что система не уходит в сон (уже стоит “Высокая производительность”).
   - Отключить автоматические перезагрузки Windows Update на период эксперимента (Активные часы/политики).
3. В репозитории создать workflow `.github/workflows/ml-long-run.yml` (пример ниже) и скрипт мониторинга `scripts/gpu_monitor.py` (пример ниже).
   - Модифицировать под конкретный проект (requirements, путь к train.py и т.д.).
4. Прогон “короткого” теста (например, 10–30 минут) для проверки:
   - Логи сохраняются, артефакты собираются (train.log, gpu_usage.csv, модели).

Критерии приёмки:
- Runner “online”, workflow запускается на метках [self-hosted, windows, gpu].
- GPU виден в шаге проверки (nvidia‑smi, torch.cuda).
- По завершении артефакты доступны в GitHub Actions (retention ≥ 14 дней).

Пример workflow (вставить в репозиторий):
```yaml
name: ML Long Training (72h, self-hosted GPU)

on:
  workflow_dispatch:
    inputs:
      run_name:
        description: "Имя запуска/эксперимента"
        required: false
        default: "exp-${{ github.run_number }}"

jobs:
  train-long:
    runs-on: [self-hosted, windows, gpu]
    timeout-minutes: 4320 # 72 часа
    env:
      PYTHON_VERSION: "3.11"
      LOG_DIR: logs/actions-run-${{ github.run_id }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Ensure log directory
        shell: pwsh
        run: New-Item -ItemType Directory -Force -Path "$env:LOG_DIR" | Out-Null

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install requirements
        shell: pwsh
        run: |
          python -m pip install --upgrade pip
          if (Test-Path "requirements.txt") {
            python -m pip install -r requirements.txt
          } else {
            python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
            python -m pip install numpy pandas scikit-learn matplotlib
          }

      - name: Print GPU info (nvidia-smi)
        shell: pwsh
        continue-on-error: true
        run: |
          $smi = "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
          if (Test-Path $smi) {
            & "$smi" | Tee-Object -FilePath "$env:LOG_DIR\nvidia-smi.txt"
          } else {
            Write-Host "nvidia-smi not found."
          }

      - name: Quick CUDA checks (PyTorch/TensorFlow)
        shell: pwsh
        continue-on-error: true
        run: |
          python - << 'PY'
import sys
def safe(fn):
    try: fn()
    except Exception as e: print("ERROR:", e, file=sys.stderr)
safe(lambda: __import__("torch"))
import torch
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device count:", torch.cuda.device_count())
    print("Device 0:", torch.cuda.get_device_name(0))
safe(lambda: __import__("tensorflow"))
import tensorflow as tf
print("TF:", tf.__version__)
print("GPUs:", tf.config.list_physical_devices('GPU'))
PY

      - name: Start background GPU monitor
        shell: pwsh
        continue-on-error: true
        run: |
          if (Test-Path "scripts\gpu_monitor.py") {
            python scripts\gpu_monitor.py --interval 60 --out "$env:LOG_DIR\gpu_usage.csv" &
          } else {
            Write-Host "scripts/gpu_monitor.py not found (monitoring skipped)."
          }

      - name: Run training
        shell: pwsh
        run: |
          if (Test-Path "scripts\train.py") {
            python scripts\train.py 2>&1 | Tee-Object -FilePath "$env:LOG_DIR\train.log"
          } else {
            Write-Host "scripts/train.py not found. Running placeholder..."
            python - << 'PY' 2>&1 | Tee-Object -FilePath "$env:LOG_DIR\train.log"
import time
print("Placeholder long run started...")
for i in range(60):  # ~60 минут демонстрации
    print(f"step {i} ...")
    time.sleep(60)
print("Placeholder long run finished.")
PY

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: "${{ github.workflow }}-${{ github.run_id }}"
          path: |
            ${{ env.LOG_DIR }}/
            models/
            results/
          if-no-files-found: ignore
          retention-days: 14
```

Скрипт мониторинга GPU (добавить в репозиторий как scripts/gpu_monitor.py):
```python
import argparse, time, csv, os, subprocess

def read_nvidia_smi():
    try:
        out = subprocess.check_output(
            ['nvidia-smi','--query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.total','--format=csv,noheader,nounits'],
            stderr=subprocess.STDOUT, text=True
        ).strip()
        return [[p.strip() for p in line.split(',')] for line in out.splitlines() if line.strip()]
    except Exception:
        return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=60)
    ap.add_argument('--out', type=str, default='gpu_usage.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    first = not os.path.exists(args.out)
    with open(args.out, 'a', newline='') as f:
        w = csv.writer(f)
        if first:
            w.writerow(["timestamp","name","util_gpu","util_mem","mem_used","mem_total"])
        try:
            while True:
                rows = read_nvidia_smi()
                for r in rows: w.writerow(r)
                f.flush()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
```

---

## 5) Безопасность: PAT/Secrets/env и защита логов

Цель: секреты не хранятся в репозитории или MCP‑конфигах, не попадают в логи.

Шаги:
1. GitHub Personal Access Token (PAT):
   - Создать Fine‑grained токен, ограничить репозиториями/организациями и правами:
     - repo (contents/issues/pulls), workflow, read:org, discussions (по необходимости).
   - Срок жизни токена — ограниченный, с напоминанием о ротации.
2. Переменные окружения Windows:
   - Установить `GITHUB_TOKEN` и другие ключи через `setx` (не хранить в *.json).
   - Перезапустить приложения после установки env.
3. В репозитории — хранить секреты только через GitHub Secrets (Repository → Settings → Secrets and variables → Actions).
4. Проверка логов:
   - Верифицировать, что паттерны токенов не утекли (минимум grep по `ghp_`, `gho_`, `ghs_` и т.п.).
   - Исключить из логов команды, печатающие секреты.

Критерии приёмки:
- Все секреты в env/Secrets, отсутствуют в файлах MCP и в репозитории.
- Логи не содержат секретов (в отчёте — отметка о проверке).

---

## 6) Финальные тесты и отчёт

Шаги:
1. Перезапустить Cursor (полный рестарт, подождать 3–4 мин).
2. MCP:
   - Context7 — тестовый запрос проходит.
   - Filesystem/SQLite/Memory — проходят тесты.
   - GitHub MCP — видит репозитории, читает Issues/PRs (без модификаций).
3. ML:
   - PyTorch — короткая тренировка (GPU), сохраняет артефакты.
   - TensorFlow — согласно выбранной стратегии (см. Раздел 3).
4. Actions:
   - self‑hosted runner — “online”.
   - Запуск короткой версии workflow (10–30 мин), проверка артефактов (train.log, gpu_usage.csv).
5. Артефакты:
   - Сформировать итоговый отчёт: `S:\mr Lopata\reports\cursor-agent-verify-{YYYYMMDD_HHMM}.md`
   - Приложить:
     - Вывод nvidia‑smi
     - Вывод проверок torch/tf
     - Логи MCP тестов (краткие выдержки)
     - Скрин/описание статуса runner
     - Ссылку на workflow run с артефактами

Критерии приёмки:
- Все тесты успешны, отчёт полон, ссылки/пути валидны.

---

## 7) Рекомендации по надёжности длительных прогонов (72ч)

- Дисковое пространство: контролировать свободное место (логи/артефакты растут). План ротации логов и очистки temp/.
- Windows Update: на время прогонов — активные часы/политики, чтобы избежать перезагрузки.
- Чекпоинты: сохранять модель и прогресс по времени/эпохам, чтобы можно было продолжить при сбое.
- Разбиение на стадии: если обучение >72ч, разбить на несколько job/run с передачей чекпоинтов.
- UPS/питание: по возможности обеспечить бесперебойность.
- Мониторинг: помимо gpu_monitor.py, писать метрики (loss/accuracy) в CSV/JSON и грузить вместе с артефактами.

---

## 8) Что именно сделать прямо сейчас (чек‑лист для агента)

- [ ] Установить GITHUB_TOKEN в env (Windows) и перезапустить Cursor.
- [ ] Протестировать все 5 MCP серверов (Context7/Filesystem/SQLite/Memory/GitHub), зафиксировать результат.
- [ ] Выбрать стратегию TF (рекомендуется tensorflow‑directml), установить и проверить GPU‑видимость; альтернативно — зафиксировать решение оставить CPU‑only.
- [ ] Подготовить проектный шаблон для экспериментов (структура папок, пример train.py, ноутбук).
- [ ] Настроить self‑hosted runner с метками [self‑hosted, windows, gpu] как сервис.
- [ ] Залить в репозиторий workflow (ml‑long‑run.yml) и скрипт мониторинга (gpu_monitor.py).
- [ ] Выполнить короткий прогон workflow, проверить логи и артефакты.
- [ ] Сформировать итоговый отчёт в S:\mr Lopata\reports\ с результатами и выводами.

---

## Приложение A: Мини‑тесты (вставить вывод в отчёт)

PyTorch:
```python
import torch
print("Torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device count:", torch.cuda.device_count())
    print("Device 0:", torch.cuda.get_device_name(0))
```

TensorFlow (после выбора стратегии):
```python
import tensorflow as tf
print("TF:", tf.__version__)
print("Physical devices:", tf.config.list_physical_devices())
print("GPUs:", tf.config.list_physical_devices('GPU'))
```

nvidia‑smi:
```
"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
```

---

## Приложение B: Полезные команды

- Обновить Docker образ GitHub MCP:
  ```
  docker pull ghcr.io/github/github-mcp-server:latest
  ```
- Постоянные переменные окружения (перезапуск приложений обязателен):
  ```
  setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  setx CONTEXT7_API_KEY "xxxxx"
  ```
- Проверка Python/pip:
  ```
  python --version
  python -m pip --version
  python -m pip list
  ```

---

Готово. Следуя этому плану, вы завершите конфигурацию “под ключ” для научной работы: Cursor + MCP (5 серверов), PyTorch GPU, опциональный TensorFlow GPU (DirectML/WSL2), self‑hosted GitHub Actions runner на Windows с длительными экспериментами до 72ч, мониторингом и артефактами.