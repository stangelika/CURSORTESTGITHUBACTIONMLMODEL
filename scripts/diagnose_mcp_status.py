#!/usr/bin/env python3
"""
Диагностика статуса MCP серверов
"""

import json
from pathlib import Path

def check_mcp_config():
    """Проверка конфигурации MCP"""
    print("🔍 Диагностика MCP серверов...")
    print("=" * 50)
    
    config_path = Path(".vscode/mcp.json")
    
    if not config_path.exists():
        print("❌ Файл .vscode/mcp.json не найден")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Конфигурационный файл найден")
        
        servers = config.get("servers", {})
        print(f"📊 Найдено серверов: {len(servers)}")
        
        for name, server_config in servers.items():
            print(f"\n🔧 Сервер: {name}")
            
            if name == "context7":
                print("   Тип: HTTP remote server")
                url = server_config.get("url", "")
                print(f"   URL: {url}")
                
                headers = server_config.get("headers", {})
                auth = headers.get("Authorization", "")
                if auth.startswith("Bearer"):
                    print(f"   API ключ: {auth[:20]}...")
                    print("   ✅ API ключ настроен")
                else:
                    print("   ❌ API ключ не найден")
            
            elif name == "github":
                print("   Тип: Docker container")
                command = server_config.get("command", "")
                print(f"   Команда: {command}")
                
                if command == "docker":
                    print("   ✅ Docker настроен")
                else:
                    print("   ❌ Docker не настроен")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Ошибка в JSON конфигурации")
        return False

def provide_troubleshooting():
    """Советы по устранению проблем"""
    print(f"\n🛠️ Устранение проблем с MCP:")
    print("=" * 40)
    
    print("1. 🔄 Убедитесь что Cursor ПОЛНОСТЬЮ перезапущен")
    print("   • Закройте все окна Cursor")
    print("   • Завершите процесс через диспетчер задач")
    print("   • Запустите Cursor заново")
    
    print("\n2. 🧠 Context7 MCP проблемы:")
    print("   • Проверьте интернет соединение")
    print("   • API ключ может быть временно недоступен")
    print("   • Попробуйте через 1-2 минуты")
    
    print("\n3. 🐙 GitHub MCP проблемы:")
    print("   • Убедитесь что Docker Desktop запущен")
    print("   • Проверьте: docker --version")
    print("   • Создайте GitHub Personal Access Token")
    
    print("\n4. 📝 Проверка в Cursor:")
    print("   • Откройте новый чат")
    print("   • Посмотрите статус MCP внизу экрана")
    print("   • Проверьте логи в Developer Tools")

def main():
    if check_mcp_config():
        provide_troubleshooting()
    
    print(f"\n🎯 Следующие шаги:")
    print("1. Полностью перезапустите Cursor")
    print("2. Подождите 1-2 минуты для загрузки MCP")
    print("3. Создайте новый чат")
    print("4. Попробуйте снова: 'Покажи примеры React хуков'")

if __name__ == "__main__":
    main()



