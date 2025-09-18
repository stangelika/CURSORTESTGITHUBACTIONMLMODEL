#!/usr/bin/env python3
"""
Пересоздание конфигурации MCP серверов
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def backup_existing_config():
    """Создание резервной копии существующей конфигурации"""
    config_path = Path(".vscode/mcp.json")
    
    if config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(f".vscode/mcp.json.backup_{timestamp}")
        
        shutil.copy2(config_path, backup_path)
        print(f"✅ Резервная копия создана: {backup_path}")
        return str(backup_path)
    
    return None

def create_fresh_config():
    """Создание свежей конфигурации MCP"""
    
    config = {
        "inputs": [
            {
                "type": "promptString",
                "id": "github_token",
                "description": "GitHub Personal Access Token",
                "password": True
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
                    "run",
                    "-i", 
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "-e", 
                    "GITHUB_TOOLSETS",
                    "ghcr.io/github/github-mcp-server"
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}",
                    "GITHUB_TOOLSETS": "context,repos,issues,pull_requests,actions,code_security,discussions,notifications,orgs,users"
                }
            }
        }
    }
    
    return config

def save_config(config):
    """Сохранение конфигурации"""
    config_path = Path(".vscode/mcp.json")
    
    # Создаем директорию если не существует
    config_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Новая конфигурация сохранена: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def validate_config():
    """Проверка корректности конфигурации"""
    config_path = Path(".vscode/mcp.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        servers = config.get("servers", {})
        
        # Проверка Context7
        if "context7" in servers:
            context7 = servers["context7"]
            if context7.get("type") == "http" and context7.get("url"):
                print("✅ Context7 конфигурация корректна")
            else:
                print("❌ Context7 конфигурация неполная")
                return False
        
        # Проверка GitHub MCP
        if "github" in servers:
            github = servers["github"]
            if github.get("command") == "docker":
                print("✅ GitHub MCP конфигурация корректна")
            else:
                print("❌ GitHub MCP конфигурация неполная")
                return False
        
        print("✅ Конфигурация прошла валидацию")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        return False

def main():
    print("🔧 Пересоздание конфигурации MCP серверов")
    print("=" * 50)
    
    # Создаем резервную копию
    backup_path = backup_existing_config()
    
    # Создаем свежую конфигурацию
    print("\n📝 Создание новой конфигурации...")
    fresh_config = create_fresh_config()
    
    # Сохраняем
    if save_config(fresh_config):
        print("\n🔍 Валидация конфигурации...")
        
        if validate_config():
            print(f"\n🎉 Успешно! Конфигурация пересоздана")
            
            if backup_path:
                print(f"💾 Резервная копия: {backup_path}")
            
            print(f"\n🔄 Следующие шаги:")
            print("1. Полностью перезапустите Cursor")
            print("2. Подождите 2-3 минуты")
            print("3. Создайте новый чат")
            print("4. Попробуйте: 'Покажи примеры React хуков'")
            
        else:
            print(f"\n❌ Конфигурация содержит ошибки")
            
            if backup_path:
                print(f"💡 Восстановите из резервной копии: {backup_path}")
    
    else:
        print(f"\n❌ Не удалось пересоздать конфигурацию")
        
        if backup_path:
            print(f"💡 Исходная конфигурация сохранена: {backup_path}")

if __name__ == "__main__":
    main()



