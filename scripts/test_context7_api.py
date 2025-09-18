#!/usr/bin/env python3
"""
Тестирование Context7 REST API
"""

import requests
import json
import sys
from typing import Optional, Dict, Any

# Ваш API ключ
API_KEY = "ctx7sk-a4b869ca-c3ab-4981-9adb-706327247c2d"
BASE_URL = "https://context7.com/api/v1"

def search_libraries(query: str) -> Optional[Dict[Any, Any]]:
    """Поиск библиотек через Context7 API"""
    
    url = f"{BASE_URL}/search"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"query": query}
    
    try:
        print(f"🔍 Поиск: {query}")
        print(f"📡 URL: {url}")
        print(f"🔑 API Key: {API_KEY[:20]}...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Успешный ответ!")
            return data
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return None

def get_library_docs(library_id: str, topic: str = "", tokens: int = 5000) -> Optional[Dict[Any, Any]]:
    """Получение документации библиотеки"""
    
    url = f"{BASE_URL}/docs"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "library_id": library_id,
        "tokens": tokens
    }
    
    if topic:
        params["topic"] = topic
    
    try:
        print(f"📚 Получение документации: {library_id}")
        if topic:
            print(f"🎯 Тема: {topic}")
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Документация получена!")
            return data
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return None

def display_search_results(results: Dict[Any, Any]):
    """Отображение результатов поиска"""
    
    if not results or 'results' not in results:
        print("❌ Нет результатов поиска")
        return
    
    libraries = results['results']
    print(f"\n📊 Найдено библиотек: {len(libraries)}")
    print("=" * 60)
    
    for i, lib in enumerate(libraries[:5], 1):  # Показываем первые 5
        print(f"\n{i}. {lib.get('title', 'Без названия')}")
        print(f"   ID: {lib.get('id', 'N/A')}")
        print(f"   Описание: {lib.get('description', 'Без описания')}")
        print(f"   ⭐ Рейтинг: {lib.get('trustScore', 0)}")
        print(f"   📝 Примеров: {lib.get('totalSnippets', 0)}")
        print(f"   🔤 Токенов: {lib.get('totalTokens', 0)}")
        
        versions = lib.get('versions', [])
        if versions:
            print(f"   📦 Версии: {', '.join(versions[:3])}")

def main():
    """Основная функция тестирования"""
    
    print("🧠 Тестирование Context7 REST API")
    print("=" * 50)
    
    # Проверяем requests модуль
    try:
        import requests
        print("✅ Модуль requests доступен")
    except ImportError:
        print("❌ Модуль requests не найден. Установите: pip install requests")
        sys.exit(1)
    
    print()
    
    # 1. Тест поиска
    search_queries = [
        "react hook form",
        "nextjs",
        "typescript",
    ]
    
    for query in search_queries:
        print(f"\n{'='*60}")
        results = search_libraries(query)
        
        if results:
            display_search_results(results)
            
            # Попробуем получить документацию первой библиотеки
            if results.get('results') and len(results['results']) > 0:
                first_lib = results['results'][0]
                lib_id = first_lib.get('id')
                
                if lib_id:
                    print(f"\n📚 Тестирование получения документации...")
                    docs = get_library_docs(lib_id, tokens=1000)
                    
                    if docs:
                        print(f"✅ Документация получена для {first_lib.get('title')}")
                        # Показываем первые 200 символов
                        content = docs.get('content', '')
                        if content:
                            preview = content[:200] + "..." if len(content) > 200 else content
                            print(f"📖 Превью: {preview}")
        
        print("-" * 60)
    
    print(f"\n🎉 Тестирование завершено!")
    print(f"💡 Context7 API работает через MCP сервер автоматически после перезапуска Cursor")

if __name__ == "__main__":
    main()





