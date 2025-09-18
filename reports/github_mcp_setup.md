# GitHub MCP Сервер - Инструкция по настройке

## 🚀 Быстрый старт

Ваш GitHub MCP сервер уже настроен! Осталось только получить токен доступа GitHub.

## 📋 Шаги для активации

### 1. Получение GitHub Personal Access Token

1. Перейдите на [GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/tokens?type=beta)

2. Нажмите **"Generate new token"**

3. Настройте токен:
   - **Name**: `MCP Server Token`
   - **Expiration**: `90 days` (или больше по желанию)
   - **Resource owner**: выберите свой аккаунт или организацию
   - **Repository access**: `All repositories` или выберите конкретные

4. **Permissions** (Разрешения) - выберите нужные:
   ```
   Repository permissions:
   ✅ Actions: Read
   ✅ Contents: Read and Write  
   ✅ Issues: Read and Write
   ✅ Pull requests: Read and Write
   ✅ Discussions: Read and Write
   ✅ Security events: Read
   
   Account permissions:
   ✅ Codespaces: Read
   ✅ Git SSH keys: Read
   ✅ Notifications: Read and Write
   ```

5. Нажмите **"Generate token"** и **СОХРАНИТЕ ТОКЕН** - он больше не будет показан!

### 2. Настройка Docker

1. Убедитесь что Docker установлен и запущен:
   ```bash
   docker --version
   ```

2. Если Docker не установлен:
   - Скачайте с [docker.com](https://www.docker.com/products/docker-desktop/)
   - Установите и запустите Docker Desktop

### 3. Первый запуск в Cursor

1. **Перезапустите Cursor** полностью
2. Создайте новый чат
3. При первом обращении к GitHub вас попросят ввести токен
4. Вставьте ваш GitHub Personal Access Token

## ✨ Примеры использования

После настройки можете сразу использовать:

```
Покажи последние 10 коммитов в этом репозитории
```

```
Создай issue для добавления новой функциональности
```

```
Проверь статус последних GitHub Actions
```

```
Найди все TODO комментарии в коде
```

## 🔧 Конфигурация

Файл конфигурации находится в `.vscode/mcp.json` и включает следующие наборы инструментов:

- **context** - информация о пользователе и контексте
- **repos** - работа с репозиториями
- **issues** - управление задачами
- **pull_requests** - работа с PR
- **actions** - GitHub Actions и CI/CD
- **code_security** - проверки безопасности
- **discussions** - обсуждения
- **notifications** - уведомления
- **orgs** - работа с организациями
- **users** - управление пользователями

## 🛠️ Устранение проблем

### Docker не запускается
- Убедитесь что Docker Desktop запущен
- Перезапустите Docker Desktop
- Проверьте что у вас достаточно места на диске

### Токен не работает
- Проверьте что токен не истек
- Убедитесь что выбраны правильные разрешения
- Попробуйте создать новый токен

### MCP сервер не отвечает
- Перезапустите Cursor
- Проверьте что конфигурация в `.vscode/mcp.json` корректна
- Убедитесь что Docker контейнер запустился:
  ```bash
  docker ps
  ```

## 🔄 Обновление

Для получения последней версии GitHub MCP сервера:

```bash
docker pull ghcr.io/github/github-mcp-server
```

---

🎉 **Готово!** Теперь вы можете работать с GitHub через AI команды на естественном языке.





