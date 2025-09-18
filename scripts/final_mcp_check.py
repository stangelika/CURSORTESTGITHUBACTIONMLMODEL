#!/usr/bin/env python3
"""
Финальная проверка настройки MCP серверов после добавления API ключа Context7
"""

import json
import subprocess
from pathlib import Path

def check_context7_config():
    """Проверка конфигурации Context7"""
    print("🧠 Проверка конфигурации Context7...")
    
    config_path = Path(".vscode/mcp.json")
    if not config_path.exists():
        print("❌ Файл .vscode/mcp.json не найден")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'servers' in config and 'context7' in config['servers']:
            context7_config = config['servers']['context7']
            
            print("✅ Конфигурация Context7 найдена")
            
            if context7_config.get('type') == 'http':
                print("✅ Тип подключения: HTTP (remote server)")
            
            if context7_config.get('url') == 'https://mcp.context7.com/mcp':
                print("✅ URL: https://mcp.context7.com/mcp")
            
            auth_header = context7_config.get('headers', {}).get('Authorization', '')
            if auth_header.startswith('Bearer ctx7sk-'):
                print("✅ API ключ настроен")
            else:
                print("❌ API ключ не найден или неправильный формат")
                return False
            
            return True
        else:
            print("❌ Конфигурация Context7 не найдена")
            return False
            
    except json.JSONDecodeError:
        print("❌ Ошибка в JSON конфигурации")
        return False
    except Exception as e:
        print(f"❌ Ошибка при чтении конфигурации: {e}")
        return False

def check_github_config():
    """Проверка конфигурации GitHub MCP"""
    print("\n🐙 Проверка конфигурации GitHub MCP...")
    
    config_path = Path(".vscode/mcp.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'servers' in config and 'github' in config['servers']:
            github_config = config['servers']['github']
            
            print("✅ Конфигурация GitHub MCP найдена")
            
            if github_config.get('command') == 'docker':
                print("✅ Настроен запуск через Docker")
                
                # Проверка Docker
                try:
                    subprocess.run(['docker', '--version'], 
                                 capture_output=True, text=True, check=True)
                    print("✅ Docker установлен")
                    
                    subprocess.run(['docker', 'ps'], 
                                 capture_output=True, text=True, check=True)
                    print("✅ Docker запущен")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("❌ Docker не установлен или не запущен")
                    return False
            
        else:
            print("❌ Конфигурация GitHub MCP не найдена")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке GitHub MCP: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🎯 Финальная проверка MCP серверов")
    print("=" * 50)
    print()
    
    context7_ok = check_context7_config()
    github_ok = check_github_config()
    
    print("\n📊 Результаты проверки:")
    print("=" * 30)
    
    if context7_ok:
        print("🧠 Context7 MCP: ✅ ГОТОВ")
        print("   • Конфигурация: OK")
        print("   • API ключ: OK")
        print("   • Требует: Перезапуск Cursor")
    else:
        print("🧠 Context7 MCP: ❌ ОШИБКА")
    
    print()
    
    if github_ok:
        print("🐙 GitHub MCP: ✅ ГОТОВ")
        print("   • Конфигурация: OK")
        print("   • Docker: OK")
        print("   • Требует: GitHub Personal Access Token")
    else:
        print("🐙 GitHub MCP: ❌ ТРЕБУЕТ DOCKER")
    
    print("\n🚀 Следующие шаги:")
    print("=" * 20)
    
    if context7_ok:
        print("1. 🔄 ПЕРЕЗАПУСТИТЕ CURSOR полностью")
        print("2. 🧪 Создайте новый чат")
        print("3. 🧠 Попробуйте: 'Покажи примеры React хуков'")
    else:
        print("1. ❌ Исправьте конфигурацию Context7")
    
    if not github_ok:
        print("4. 🐳 Установите Docker Desktop")
        print("5. 🔑 Получите GitHub Personal Access Token")
    else:
        print("4. 🔑 Получите GitHub Personal Access Token")
    
    if context7_ok and github_ok:
        print("\n🎉 ВСЕ ГОТОВО! После перезапуска Cursor оба MCP сервера будут работать!")
    elif context7_ok or github_ok:
        print(f"\n⚠️ Один сервер готов, второй требует настройки")
    else:
        print(f"\n❌ Оба сервера требуют дополнительной настройки")

if __name__ == "__main__":
    main()





