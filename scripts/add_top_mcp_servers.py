#!/usr/bin/env python3
"""
Быстрое добавление топ-3 MCP серверов в конфигурацию
"""

import json
import shutil
from pathlib import Path

# Топ-3 рекомендуемых сервера
TOP_SERVERS = {
    "markitdown": {
        "command": "npx",
        "args": ["-y", "@microsoft/markitdown-mcp@latest"],
        "description": "Конвертация PDF/Word/Excel в Markdown (74,351⭐)",
        "examples": [
            "Конвертируй этот PDF файл в Markdown",
            "Извлеки текст из изображения", 
            "Преобразуй Word документ в Markdown"
        ]
    },
    "playwright": {
        "command": "npx", 
        "args": ["-y", "@microsoft/playwright-mcp@latest"],
        "description": "Автоматизация браузера и веб-тестирование (19,749⭐)",
        "examples": [
            "Сделай скриншот главной страницы github.com",
            "Автоматизируй заполнение формы на сайте",
            "Протестируй веб-приложение"
        ]
    },
    "firecrawl": {
        "command": "npx",
        "args": ["-y", "@firecrawl/mcp@latest"],
        "description": "Веб-скрапинг и извлечение данных (4,514⭐)",
        "examples": [
            "Извлеки все ссылки с главной страницы сайта",
            "Скачай содержимое блога в Markdown формате",
            "Получи данные о товарах с сайта интернет-магазина"
        ]
    }
}

def backup_config():
    """Создание резервной копии конфигурации"""
    config_path = Path(".vscode/mcp.json")
    backup_path = Path(".vscode/mcp.json.backup")
    
    if config_path.exists():
        shutil.copy2(config_path, backup_path)
        print(f"✅ Создана резервная копия: {backup_path}")
        return True
    return False

def load_current_config():
    """Загрузка текущей конфигурации"""
    config_path = Path(".vscode/mcp.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("❌ Ошибка в JSON конфигурации")
            return None
    else:
        print("❌ Файл .vscode/mcp.json не найден")
        return None

def add_servers_to_config(config, servers_to_add):
    """Добавление серверов в конфигурацию"""
    if "servers" not in config:
        config["servers"] = {}
    
    added_servers = []
    skipped_servers = []
    
    for server_name, server_config in servers_to_add.items():
        if server_name not in config["servers"]:
            # Убираем description и examples - они не нужны в JSON конфиге
            clean_config = {
                "command": server_config["command"],
                "args": server_config["args"]
            }
            config["servers"][server_name] = clean_config
            added_servers.append(server_name)
        else:
            skipped_servers.append(server_name)
    
    return config, added_servers, skipped_servers

def save_config(config):
    """Сохранение обновленной конфигурации"""
    config_path = Path(".vscode/mcp.json")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Конфигурация сохранена: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        return False

def show_server_info():
    """Показать информацию о серверах"""
    print("🔥 Топ-3 рекомендуемых MCP сервера:")
    print("=" * 60)
    
    for i, (server_name, server_info) in enumerate(TOP_SERVERS.items(), 1):
        print(f"\n{i}. 📦 {server_name.upper()}")
        print(f"   {server_info['description']}")
        print(f"   📝 Примеры использования:")
        for example in server_info['examples']:
            print(f"      • {example}")

def main():
    print("🚀 Добавление топ-3 MCP серверов")
    print("=" * 50)
    
    # Показываем информацию о серверах
    show_server_info()
    
    print(f"\n🤔 Добавить эти серверы в конфигурацию? (y/n): ", end="")
    choice = input().lower()
    
    if choice != 'y':
        print("❌ Добавление отменено")
        return
    
    # Создаем резервную копию
    print(f"\n📋 Обработка конфигурации...")
    backup_created = backup_config()
    
    # Загружаем текущую конфигурацию
    config = load_current_config()
    if config is None:
        return
    
    print(f"✅ Текущая конфигурация загружена")
    print(f"   Существующие серверы: {list(config.get('servers', {}).keys())}")
    
    # Добавляем серверы
    updated_config, added, skipped = add_servers_to_config(config, TOP_SERVERS)
    
    # Сохраняем обновленную конфигурацию
    if save_config(updated_config):
        print(f"\n🎉 Результат:")
        
        if added:
            print(f"   ✅ Добавлено серверов: {len(added)}")
            for server in added:
                print(f"      • {server}")
        
        if skipped:
            print(f"   ⚠️ Пропущено (уже существуют): {len(skipped)}")
            for server in skipped:
                print(f"      • {server}")
        
        print(f"\n🔄 Следующие шаги:")
        print(f"   1. Перезапустите Cursor полностью")
        print(f"   2. Создайте новый чат")
        print(f"   3. Попробуйте команды:")
        
        for server_name, server_info in TOP_SERVERS.items():
            if server_name in added:
                example = server_info['examples'][0]
                print(f"      • {example}")
        
        print(f"\n💡 Полный список примеров в RECOMMENDED_MCP_SERVERS.md")
        
        if backup_created:
            print(f"\n🛡️ Резервная копия: .vscode/mcp.json.backup")
    else:
        print(f"\n❌ Не удалось сохранить конфигурацию")
        if backup_created:
            print(f"💡 Восстановите из резервной копии: .vscode/mcp.json.backup")

if __name__ == "__main__":
    main()





