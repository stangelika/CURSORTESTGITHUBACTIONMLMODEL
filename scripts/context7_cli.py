#!/usr/bin/env python3
"""
Context7 CLI - Утилита командной строки для работы с Context7 API
Использование:
    python context7_cli.py search "react hooks"
    python context7_cli.py docs "/react-hook-form/documentation" --topic hooks --tokens 2000
"""

import requests
import json
import argparse
import sys
from typing import Optional, Dict, Any

# Ваш API ключ
API_KEY = "ctx7sk-a4b869ca-c3ab-4981-9adb-706327247c2d"
BASE_URL = "https://context7.com/api/v1"

class Context7API:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def search(self, query: str) -> Optional[Dict[Any, Any]]:
        """Поиск библиотек"""
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка поиска: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка сети: {e}")
            return None
    
    def get_docs(self, library_id: str, topic: str = "", tokens: int = 5000) -> Optional[Dict[Any, Any]]:
        """Получение документации"""
        params = {
            "library_id": library_id,
            "tokens": tokens
        }
        
        if topic:
            params["topic"] = topic
        
        try:
            response = self.session.get(
                f"{self.base_url}/docs",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка получения документации: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка сети: {e}")
            return None

def cmd_search(args):
    """Команда поиска"""
    api = Context7API(API_KEY)
    
    print(f"🔍 Поиск: {args.query}")
    results = api.search(args.query)
    
    if not results:
        return
    
    libraries = results.get('results', [])
    
    if not libraries:
        print("❌ Библиотеки не найдены")
        return
    
    print(f"\n📊 Найдено: {len(libraries)} библиотек")
    print("=" * 80)
    
    for i, lib in enumerate(libraries, 1):
        print(f"\n{i}. 📚 {lib.get('title', 'Без названия')}")
        print(f"   🆔 ID: {lib.get('id', 'N/A')}")
        print(f"   📝 Описание: {lib.get('description', 'Без описания')}")
        print(f"   ⭐ Рейтинг: {lib.get('trustScore', 0)}")
        print(f"   🔢 Примеров кода: {lib.get('totalSnippets', 0)}")
        print(f"   📄 Токенов: {lib.get('totalTokens', 0):,}")
        
        versions = lib.get('versions', [])
        if versions:
            print(f"   📦 Версии: {', '.join(versions[:5])}")
        
        if i >= args.limit:
            remaining = len(libraries) - args.limit
            if remaining > 0:
                print(f"\n... и ещё {remaining} результат(ов)")
            break

def cmd_docs(args):
    """Команда получения документации"""
    api = Context7API(API_KEY)
    
    print(f"📚 Получение документации: {args.library_id}")
    if args.topic:
        print(f"🎯 Тема: {args.topic}")
    print(f"🔢 Токенов: {args.tokens:,}")
    
    docs = api.get_docs(args.library_id, args.topic, args.tokens)
    
    if not docs:
        return
    
    print("\n" + "=" * 80)
    print("📖 ДОКУМЕНТАЦИЯ")
    print("=" * 80)
    
    content = docs.get('content', '')
    if content:
        # Разбиваем на строки и показываем с отступом
        lines = content.split('\n')
        for line in lines[:50]:  # Первые 50 строк
            print(f"   {line}")
        
        if len(lines) > 50:
            print(f"\n... (показано первых 50 строк из {len(lines)})")
    else:
        print("❌ Содержимое документации не найдено")
    
    # Дополнительная информация
    meta = docs.get('metadata', {})
    if meta:
        print(f"\n📊 Метаданные:")
        for key, value in meta.items():
            print(f"   {key}: {value}")

def cmd_interactive():
    """Интерактивный режим"""
    api = Context7API(API_KEY)
    
    print("🧠 Context7 Interactive Mode")
    print("Команды: search <query>, docs <library_id> [topic], exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n💡 Context7> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("👋 До свидания!")
                break
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'search' and len(parts) > 1:
                query = ' '.join(parts[1:])
                print(f"🔍 Поиск: {query}")
                results = api.search(query)
                
                if results and results.get('results'):
                    for i, lib in enumerate(results['results'][:3], 1):
                        print(f"{i}. {lib.get('title')} - {lib.get('id')}")
            
            elif cmd == 'docs' and len(parts) > 1:
                library_id = parts[1]
                topic = parts[2] if len(parts) > 2 else ""
                
                docs = api.get_docs(library_id, topic, 1000)
                if docs:
                    content = docs.get('content', '')[:300]
                    print(f"📚 {content}...")
            
            else:
                print("❌ Неизвестная команда. Используйте: search <query>, docs <library_id> [topic]")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    parser = argparse.ArgumentParser(description="Context7 CLI - работа с Context7 API")
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда поиска
    search_parser = subparsers.add_parser('search', help='Поиск библиотек')
    search_parser.add_argument('query', help='Поисковый запрос')
    search_parser.add_argument('--limit', type=int, default=10, help='Максимум результатов (по умолчанию: 10)')
    
    # Команда получения документации
    docs_parser = subparsers.add_parser('docs', help='Получение документации')
    docs_parser.add_argument('library_id', help='ID библиотеки')
    docs_parser.add_argument('--topic', default='', help='Конкретная тема')
    docs_parser.add_argument('--tokens', type=int, default=5000, help='Количество токенов (по умолчанию: 5000)')
    
    # Интерактивный режим
    subparsers.add_parser('interactive', help='Интерактивный режим')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Проверяем requests
    try:
        import requests
    except ImportError:
        print("❌ Модуль requests не установлен. Выполните: pip install requests")
        sys.exit(1)
    
    if args.command == 'search':
        cmd_search(args)
    elif args.command == 'docs':
        cmd_docs(args)
    elif args.command == 'interactive':
        cmd_interactive()

if __name__ == "__main__":
    main()





