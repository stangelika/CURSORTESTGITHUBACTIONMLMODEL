#!/usr/bin/env python3
"""
Проверка всех конфигурационных файлов MCP
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

def check_json_file(file_path: Path) -> tuple[bool, str]:
    """Проверка корректности JSON файла"""
    
    if not file_path.exists():
        return False, f"Файл не найден: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, f"✅ Валидный JSON: {len(data)} ключей"
    except json.JSONDecodeError as e:
        return False, f"❌ Ошибка JSON: {e}"
    except Exception as e:
        return False, f"❌ Ошибка файла: {e}"

def validate_context7_config(config_path: Path) -> List[str]:
    """Валидация конфигурации Context7"""
    results = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверки Context7
        if config.get('name') == 'context7':
            results.append("✅ Имя сервера корректно")
        else:
            results.append("❌ Неправильное имя сервера")
        
        server = config.get('server', {})
        if server.get('type') == 'http':
            results.append("✅ Тип подключения: HTTP")
        else:
            results.append("❌ Неправильный тип подключения")
        
        if server.get('url') == 'https://mcp.context7.com/mcp':
            results.append("✅ URL Context7 корректен")
        else:
            results.append("❌ Неправильный URL")
        
        headers = server.get('headers', {})
        auth = headers.get('Authorization', '')
        if auth.startswith('Bearer ctx7sk-'):
            results.append("✅ API ключ настроен")
        else:
            results.append("❌ API ключ отсутствует")
        
        tools = config.get('tools', [])
        if 'resolve-library-id' in tools and 'get-library-docs' in tools:
            results.append("✅ Инструменты Context7 настроены")
        else:
            results.append("❌ Инструменты Context7 не настроены")
            
    except Exception as e:
        results.append(f"❌ Ошибка валидации Context7: {e}")
    
    return results

def validate_github_config(config_path: Path) -> List[str]:
    """Валидация конфигурации GitHub MCP"""
    results = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверки GitHub MCP
        if config.get('name') == 'github':
            results.append("✅ Имя сервера корректно")
        else:
            results.append("❌ Неправильное имя сервера")
        
        server = config.get('server', {})
        if server.get('command') == 'docker':
            results.append("✅ Команда Docker настроена")
        else:
            results.append("❌ Команда Docker не настроена")
        
        args = server.get('args', [])
        if 'ghcr.io/github/github-mcp-server' in args:
            results.append("✅ Docker образ корректен")
        else:
            results.append("❌ Docker образ не настроен")
        
        toolsets = config.get('toolsets', [])
        required_toolsets = ['context', 'repos', 'issues', 'pull_requests']
        if all(t in toolsets for t in required_toolsets):
            results.append("✅ Основные toolsets настроены")
        else:
            results.append("❌ Не все toolsets настроены")
            
    except Exception as e:
        results.append(f"❌ Ошибка валидации GitHub: {e}")
    
    return results

def check_file_structure():
    """Проверка структуры файлов"""
    print("📁 Проверка структуры файлов MCP...")
    print("=" * 50)
    
    files_to_check = [
        Path(".cursor/mcp/context7.json"),
        Path(".cursor/mcp/github.json"), 
        Path(".cursor/mcp/servers.json"),
        Path(".vscode/mcp.json"),
        Path(".vscode/mcp-servers.json")
    ]
    
    all_valid = True
    
    for file_path in files_to_check:
        valid, message = check_json_file(file_path)
        print(f"📄 {file_path}: {message}")
        if not valid:
            all_valid = False
    
    return all_valid

def main():
    """Главная функция валидации"""
    print("🔍 Валидация всех MCP конфигураций")
    print("=" * 60)
    
    # Проверка структуры файлов
    structure_valid = check_file_structure()
    
    if not structure_valid:
        print("\n❌ Не все файлы найдены или валидны")
        return
    
    # Валидация Context7
    print(f"\n🧠 Валидация Context7 конфигурации:")
    print("-" * 40)
    context7_results = validate_context7_config(Path(".cursor/mcp/context7.json"))
    for result in context7_results:
        print(f"   {result}")
    
    # Валидация GitHub MCP  
    print(f"\n🐙 Валидация GitHub MCP конфигурации:")
    print("-" * 40)
    github_results = validate_github_config(Path(".cursor/mcp/github.json"))
    for result in github_results:
        print(f"   {result}")
    
    # Итоговый статус
    print(f"\n📊 Общий статус:")
    print("=" * 30)
    
    context7_success = all("✅" in r for r in context7_results)
    github_success = all("✅" in r for r in github_results)
    
    if context7_success:
        print("🧠 Context7: ✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    else:
        print("🧠 Context7: ❌ ЕСТЬ ПРОБЛЕМЫ")
    
    if github_success:
        print("🐙 GitHub MCP: ✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
    else:
        print("🐙 GitHub MCP: ❌ ЕСТЬ ПРОБЛЕМЫ")
    
    if context7_success and github_success:
        print(f"\n🎉 ВСЕ КОНФИГУРАЦИИ ВАЛИДНЫ!")
        print("🔄 Следующие шаги:")
        print("1. Полностью перезапустите Cursor")  
        print("2. Подождите 2-3 минуты")
        print("3. Создайте новый чат")
        print("4. Попробуйте: 'Покажи примеры React хуков'")
    else:
        print(f"\n⚠️ Найдены проблемы в конфигурациях")

if __name__ == "__main__":
    main()


