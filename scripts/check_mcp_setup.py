#!/usr/bin/env python3
"""
Скрипт для проверки настройки MCP серверов
"""

import json
import subprocess
import sys
from pathlib import Path

def check_docker():
    """Проверка установки и запуска Docker"""
    print("🐳 Проверка Docker...")
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker установлен: {result.stdout.strip()}")
        
        # Проверка что Docker запущен
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, check=True)
        print("✅ Docker запущен и работает")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker не установлен или не запущен")
        print("💡 Установите Docker Desktop: https://www.docker.com/products/docker-desktop/")
        return False

def check_mcp_config():
    """Проверка конфигурации MCP"""
    print("\n⚙️ Проверка конфигурации MCP...")
    
    config_path = Path(".vscode/mcp.json")
    if not config_path.exists():
        print("❌ Файл .vscode/mcp.json не найден")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'servers' in config and 'github' in config['servers']:
            print("✅ Конфигурация GitHub MCP найдена")
            
            github_config = config['servers']['github']
            if github_config.get('command') == 'docker':
                print("✅ Настроен запуск через Docker")
            
            toolsets = github_config.get('env', {}).get('GITHUB_TOOLSETS', '')
            if toolsets:
                print(f"✅ Наборы инструментов: {toolsets}")
            
            return True
        else:
            print("❌ Конфигурация GitHub MCP не найдена")
            return False
            
    except json.JSONDecodeError:
        print("❌ Ошибка в JSON конфигурации")
        return False

def check_cursor_rules():
    """Проверка правил Cursor"""
    print("\n📋 Проверка правил Cursor...")
    
    rules_path = Path("cursorrules.txt")
    if not rules_path.exists():
        print("❌ Файл cursorrules.txt не найден")
        return False
    
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "GitHub MCP" in content:
            print("✅ Правила для GitHub MCP найдены")
            return True
        else:
            print("❌ Правила для GitHub MCP не найдены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при чтении правил: {e}")
        return False

def pull_github_mcp_image():
    """Загрузка Docker образа GitHub MCP"""
    print("\n📥 Загрузка Docker образа GitHub MCP...")
    try:
        result = subprocess.run([
            'docker', 'pull', 'ghcr.io/github/github-mcp-server'
        ], capture_output=True, text=True, check=True)
        print("✅ Docker образ GitHub MCP загружен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при загрузке образа: {e.stderr}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка настройки MCP серверов\n")
    
    checks = [
        ("Docker", check_docker),
        ("Конфигурация MCP", check_mcp_config),
        ("Правила Cursor", check_cursor_rules)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    if all_passed and check_docker():
        print("\n🎯 Все проверки прошли успешно!")
        
        # Попытка загрузить Docker образ
        if pull_github_mcp_image():
            print("\n✨ Настройка завершена! Следующие шаги:")
            print("1. Перезапустите Cursor")
            print("2. Получите GitHub Personal Access Token (см. GITHUB_MCP_SETUP.md)")
            print("3. Начните новый чат и попробуйте команду: 'Покажи информацию о репозитории'")
        else:
            print("\n⚠️ Образ не удалось загрузить, но настройки готовы.")
            print("Docker загрузит образ автоматически при первом использовании.")
    else:
        print("\n❌ Некоторые проверки не прошли. Исправьте ошибки и запустите снова.")
        sys.exit(1)

if __name__ == "__main__":
    main()





