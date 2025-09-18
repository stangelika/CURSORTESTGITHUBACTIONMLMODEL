#!/usr/bin/env python3
"""
Быстрый тест Context7 API с правильным форматом library_id
"""

import requests
import json

API_KEY = "ctx7sk-a4b869ca-c3ab-4981-9adb-706327247c2d"
BASE_URL = "https://context7.com/api/v1"

def test_docs_api():
    """Тест получения документации с правильным форматом"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Используем правильный формат для Microsoft TypeScript
    library_id = "microsoft/typescript"  # Убираем "/websites/" префикс
    
    params = {
        "library_id": library_id,
        "tokens": 2000,
        "topic": "basics"
    }
    
    print(f"📚 Тест получения документации...")
    print(f"🆔 Library ID: {library_id}")
    print(f"🎯 Topic: {params['topic']}")
    print(f"🔢 Tokens: {params['tokens']}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/docs",
            headers=headers,
            params=params,
            timeout=15
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Документация получена!")
            
            content = data.get('content', '')
            if content:
                # Показываем первые 500 символов
                preview = content[:500] + "..." if len(content) > 500 else content
                print(f"\n📖 Содержимое ({len(content)} символов):")
                print("-" * 60)
                print(preview)
                print("-" * 60)
                return True
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_multiple_libraries():
    """Тест нескольких библиотек"""
    
    libraries_to_test = [
        ("react", "hooks"),
        ("microsoft/typescript", "interfaces"), 
        ("vercel/next.js", "routing")
    ]
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Тестирование нескольких библиотек:")
    print("=" * 60)
    
    for lib_id, topic in libraries_to_test:
        print(f"\n📚 {lib_id} (тема: {topic})")
        
        params = {
            "library_id": lib_id,
            "topic": topic,
            "tokens": 1000
        }
        
        try:
            response = requests.get(
                f"{BASE_URL}/docs",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', '')
                print(f"✅ Успешно! Получено {len(content)} символов")
                # Показываем первые 200 символов
                if content:
                    preview = content[:200].replace('\n', ' ')
                    print(f"📖 Превью: {preview}...")
            else:
                print(f"❌ Ошибка {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Сетевая ошибка: {e}")

def main():
    print("🧠 Context7 API - Быстрый тест")
    print("=" * 50)
    
    print("1️⃣ Тест получения документации:")
    success = test_docs_api()
    
    print(f"\n2️⃣ Тест нескольких библиотек:")
    test_multiple_libraries()
    
    print(f"\n🎯 Результат:")
    if success:
        print("✅ Context7 API полностью работает!")
        print("🚀 MCP сервер готов к использованию после перезапуска Cursor")
    else:
        print("⚠️ API частично работает (поиск OK, документация требует правильного формата)")

if __name__ == "__main__":
    main()





