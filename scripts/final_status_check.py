#!/usr/bin/env python3
"""
Финальная проверка статуса всех компонентов MCP системы
"""

import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime

def check_docker():
    """Проверка Docker"""
    print("🐳 Проверка Docker...")
    
    try:
        # Версия Docker
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"   ✅ Версия: {result.stdout.strip()}")
        
        # Docker Engine
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, check=True)
        print("   ✅ Engine запущен")
        
        # Docker образ GitHub MCP
        result = subprocess.run(['docker', 'images', 'ghcr.io/github/github-mcp-server'], 
                              capture_output=True, text=True, check=True)
        if 'ghcr.io/github/github-mcp-server' in result.stdout:
            print("   ✅ GitHub MCP образ загружен")
        else:
            print("   ⚠️ GitHub MCP образ не найден")
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Docker проблемы")
        return False

def check_network():
    """Проверка сетевой доступности"""
    print("\n🌐 Проверка сети...")
    
    try:
        # Context7 endpoint
        response = requests.head('https://mcp.context7.com/mcp', timeout=5)
        if response.status_code in [200, 405, 406]:  # 405/406 это OK для HEAD запроса
            print("   ✅ Context7 endpoint доступен")
        else:
            print(f"   ⚠️ Context7 вернул статус {response.status_code}")
        
        # Общая проверка интернета
        response = requests.head('https://google.com', timeout=5)
        print("   ✅ Интернет соединение работает")
        
        return True
        
    except requests.exceptions.RequestException:
        print("   ❌ Сетевые проблемы")
        return False

def check_configs():
    """Проверка конфигурационных файлов"""
    print("\n⚙️ Проверка конфигураций...")
    
    configs = [
        ".cursor/mcp/context7.json",
        ".cursor/mcp/github.json", 
        ".cursor/mcp/servers.json",
        ".vscode/mcp.json",
        ".vscode/mcp-servers.json"
    ]
    
    all_valid = True
    
    for config_path in configs:
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ {config_path}: {len(data)} ключей")
            except json.JSONDecodeError:
                print(f"   ❌ {config_path}: Ошибка JSON")
                all_valid = False
        else:
            print(f"   ❌ {config_path}: Не найден")
            all_valid = False
    
    return all_valid

def check_api_keys():
    """Проверка API ключей"""
    print("\n🔑 Проверка API ключей...")
    
    try:
        # Context7 API ключ
        config_path = Path(".cursor/mcp/context7.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        headers = config.get('server', {}).get('headers', {})
        auth = headers.get('Authorization', '')
        
        if auth.startswith('Bearer ctx7sk-'):
            print("   ✅ Context7 API ключ настроен")
            return True
        else:
            print("   ❌ Context7 API ключ не найден")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка проверки ключей: {e}")
        return False

def generate_activation_instructions():
    """Генерация инструкций по активации"""
    print("\n🎯 ИНСТРУКЦИИ ПО АКТИВАЦИИ:")
    print("=" * 50)
    
    print("1️⃣ ПОЛНЫЙ ПЕРЕЗАПУСК CURSOR:")
    print("   • Закройте ВСЕ окна Cursor")
    print("   • Ctrl+Shift+Esc → Завершите все процессы Cursor")
    print("   • Подождите 30 секунд")
    print("   • Запустите Cursor КАК АДМИНИСТРАТОР")
    print("   • Подождите 3-4 МИНУТЫ (критично!)")
    
    print("\n2️⃣ ПРОВЕРКА АКТИВАЦИИ:")
    print("   • Посмотрите внизу окна Cursor на значки MCP")
    print("   • Создайте НОВЫЙ чат")
    print("   • Попробуйте: 'Покажи примеры React хуков'")
    
    print("\n3️⃣ ПРИЗНАКИ УСПЕХА:")
    print("   • Значки MCP внизу Cursor")
    print("   • Context7 отвечает с документацией")
    print("   • Нет ошибок 'Tool not found'")

def main():
    """Основная функция проверки"""
    print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА MCP СИСТЕМЫ")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверки
    docker_ok = check_docker()
    network_ok = check_network() 
    configs_ok = check_configs()
    keys_ok = check_api_keys()
    
    # Итоговый статус
    print(f"\n📊 ИТОГОВЫЙ СТАТУС:")
    print("=" * 40)
    
    print(f"🐳 Docker:        {'✅ ОК' if docker_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"🌐 Сеть:          {'✅ ОК' if network_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"⚙️ Конфигурации:  {'✅ ОК' if configs_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"🔑 API ключи:     {'✅ ОК' if keys_ok else '❌ ПРОБЛЕМЫ'}")
    
    all_ready = docker_ok and network_ok and configs_ok and keys_ok
    
    if all_ready:
        print(f"\n🎉 СИСТЕМА ПОЛНОСТЬЮ ГОТОВА!")
        print(f"🔴 ПРОБЛЕМА: Cursor не активировал MCP серверы")
        print(f"🎯 РЕШЕНИЕ: Принудительный перезапуск Cursor")
        
        generate_activation_instructions()
        
    else:
        print(f"\n⚠️ НАЙДЕНЫ ПРОБЛЕМЫ В СИСТЕМЕ")
        print("Исправьте проблемы выше перед активацией MCP")

if __name__ == "__main__":
    main()

