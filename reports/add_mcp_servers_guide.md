# 🛠️ Руководство по добавлению новых MCP серверов

## 🎯 Как добавить любой MCP сервер

### 📁 Шаг 1: Обновление конфигурации
Откройте файл `.vscode/mcp.json` и добавьте новый сервер в секцию `"servers"`:

```json
{
  "inputs": [...],
  "servers": {
    "context7": {...},
    "github": {...},
    
    "НОВЫЙ_СЕРВЕР": {
      "command": "npx",
      "args": ["-y", "пакет@latest"]
    }
  }
}
```

---

## 🔥 Быстрое добавление ТОП-3 серверов

### 1️⃣ **Markitdown** (самый популярный)
```json
"markitdown": {
  "command": "npx", 
  "args": ["-y", "@microsoft/markitdown-mcp@latest"]
}
```

### 2️⃣ **Playwright** (автоматизация браузера)
```json
"playwright": {
  "command": "npx",
  "args": ["-y", "@microsoft/playwright-mcp@latest"]  
}
```

### 3️⃣ **Firecrawl** (веб-скрапинг)
```json
"firecrawl": {
  "command": "npx",
  "args": ["-y", "@firecrawl/mcp@latest"]
}
```

---

## 📋 Полная конфигурация с новыми серверами

### Обновленный `.vscode/mcp.json`:
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "github_token", 
      "description": "GitHub Personal Access Token",
      "password": true
    }
  ],
  "servers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "Authorization": "Bearer ctx7sk-a4b869ca-c3ab-4981-9adb-706327247c2d"
      }
    },
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_TOOLSETS", "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}",
        "GITHUB_TOOLSETS": "context,repos,issues,pull_requests,actions,code_security,discussions,notifications,orgs,users"
      }
    },
    "markitdown": {
      "command": "npx",
      "args": ["-y", "@microsoft/markitdown-mcp@latest"]
    },
    "playwright": {
      "command": "npx", 
      "args": ["-y", "@microsoft/playwright-mcp@latest"]
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@firecrawl/mcp@latest"]
    }
  }
}
```

---

## 🧪 Тестирование новых серверов

### После добавления серверов:
1. **Сохраните** `.vscode/mcp.json`
2. **Перезапустите Cursor** полностью
3. **Создайте новый чат**
4. **Протестируйте:**

```
// Markitdown
Конвертируй этот PDF файл в Markdown

// Playwright  
Сделай скриншот главной страницы github.com

// Firecrawl
Извлеки все ссылки с главной страницы wikipedia.org
```

---

## 🔧 Серверы с дополнительными настройками

### **Notion** (требует API токен):
```json
"notion": {
  "command": "npx",
  "args": ["-y", "@makenotion/notion-mcp@latest"],
  "env": {
    "NOTION_API_TOKEN": "your-notion-api-token"
  }
}
```

### **Azure** (требует Service Principal):
```json
"azure": {
  "command": "npx",
  "args": ["-y", "@azure/mcp@latest"], 
  "env": {
    "AZURE_CLIENT_ID": "your-client-id",
    "AZURE_CLIENT_SECRET": "your-client-secret",
    "AZURE_TENANT_ID": "your-tenant-id"
  }
}
```

### **Stripe** (требует API ключ):
```json
"stripe": {
  "command": "npx",
  "args": ["-y", "@stripe/agent-toolkit@latest"],
  "env": {
    "STRIPE_API_KEY": "sk_test_..."
  }
}
```

---

## 📊 Мониторинг MCP серверов

### Создайте скрипт для проверки всех серверов:

```python
# scripts/check_all_mcp_servers.py
import json
from pathlib import Path

def check_mcp_config():
    config_path = Path(".vscode/mcp.json")
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        
        servers = config.get("servers", {})
        print(f"🔍 Найдено {len(servers)} MCP серверов:")
        
        for name, server_config in servers.items():
            print(f"  ✅ {name}")
            if 'command' in server_config:
                print(f"     Команда: {server_config['command']}")
    
if __name__ == "__main__":
    check_mcp_config()
```

---

## 🚨 Устранение проблем

### Сервер не запускается:
1. Проверьте синтаксис JSON в `.vscode/mcp.json`
2. Убедитесь что пакет существует в npm
3. Перезапустите Cursor полностью

### Сервер не отвечает:
1. Проверьте переменные окружения (API ключи)
2. Убедитесь в правильности команды запуска
3. Посмотрите логи в выводе Cursor

### Медленная работа:
1. Не добавляйте слишком много серверов сразу
2. Отключите неиспользуемые серверы
3. Используйте локальные серверы вместо удаленных где возможно

---

## 🎯 Рекомендуемая стратегия добавления

### **Фаза 1** (сейчас):
- ✅ Context7 (документация)  
- ✅ GitHub (репозитории)

### **Фаза 2** (добавить 2-3 самых нужных):
- 📄 Markitdown (конвертация документов)
- 🎭 Playwright (автоматизация браузера)  
- 🕷️ Firecrawl (веб-скрапинг)

### **Фаза 3** (по мере необходимости):
- 📝 Notion (если используете)
- ☁️ Azure/AWS (если работаете с облаком)
- 🔧 Специализированные серверы

---

🎉 **Готово!** Теперь вы можете добавлять любые MCP серверы из реестра!





