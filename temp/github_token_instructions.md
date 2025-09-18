# GitHub Personal Access Token - Инструкции по созданию

## Для GitHub MCP сервера нужен Personal Access Token (PAT)

### Шаги создания:

1. **Перейти в GitHub Settings:**
   - Откройте https://github.com
   - Нажмите на аватар → Settings
   - В левом меню: Developer settings → Personal access tokens → Fine-grained tokens

2. **Создать новый токен:**
   - Click "Generate new token"
   - Название: `Cursor MCP Server Token`
   - Expiration: 90 days (или по вашему выбору)
   
3. **Необходимые права (Permissions):**
   - **Repository permissions:**
     - Contents: Read
     - Issues: Read (и Write, если нужно создавать)
     - Pull requests: Read (и Write, если нужно создавать)  
     - Actions: Read
     - Discussions: Read (опционально)
   - **Organization permissions:**
     - Organization: Read (если работаете с организациями)

4. **Ограничить репозитории:**
   - Выберите конкретные репозитории или оставьте "All repositories" (не рекомендуется для безопасности)

5. **Скопировать токен:**
   - После создания появится токен вида: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **ВНИМАНИЕ**: Сразу скопируйте - он больше не будет показан!

### После создания токена:

```cmd
# Установить в переменные окружения Windows (запустить как Администратор)
setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Проверить установку (в новом терминале)
echo %GITHUB_TOKEN%
```

### Если токен готов:
Сообщите мне, и я продолжу настройку MCP серверов с этим токеном.
