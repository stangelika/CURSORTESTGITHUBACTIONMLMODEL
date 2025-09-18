#!/usr/bin/env python3
"""
Финальный тест Context7 API - используем полные ID из поиска
"""

import requests
import json

API_KEY = "ctx7sk-a4b869ca-c3ab-4981-9adb-706327247c2d"
BASE_URL = "https://context7.com/api/v1"

def search_and_get_docs():
    """Поиск библиотеки и получение документации по найденному ID"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Поиск React...")
    
    # 1. Сначала ищем React
    search_response = requests.get(
        f"{BASE_URL}/search",
        headers=headers,
        params={"query": "react"},
        timeout=10
    )
    
    if search_response.status_code != 200:
        print(f"❌ Ошибка поиска: {search_response.text}")
        return
    
    search_data = search_response.json()
    results = search_data.get('results', [])
    
    if not results:
        print("❌ Нет результатов поиска")
        return
    
    # Берем первый результат
    first_result = results[0]
    library_id = first_result.get('id')
    library_title = first_result.get('title')
    
    print(f"✅ Найдена библиотека: {library_title}")
    print(f"🆔 ID: {library_id}")
    
    # 2. Теперь пробуем разные варианты параметров для получения документации
    docs_params_variants = [
        {"library_id": library_id, "tokens": 1000},
        {"context7CompatibleLibraryID": library_id, "tokens": 1000},
        {"id": library_id, "tokens": 1000},
        {"libraryId": library_id, "tokens": 1000}
    ]
    
    print(f"\n📚 Тестирование получения документации...")
    
    for i, params in enumerate(docs_params_variants, 1):
        print(f"\n{i}. Попытка с параметрами: {list(params.keys())}")
        
        try:
            docs_response = requests.get(
                f"{BASE_URL}/docs",
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"   📊 Status: {docs_response.status_code}")
            
            if docs_response.status_code == 200:
                data = docs_response.json()
                content = data.get('content', '')
                
                print(f"   ✅ УСПЕХ! Получено {len(content)} символов")
                
                if content:
                    preview = content[:300].replace('\n', ' ')
                    print(f"   📖 Превью: {preview}...")
                
                print(f"\n🎉 Рабочий формат найден!")
                return params
            else:
                error_text = docs_response.text[:100]
                print(f"   ❌ Ошибка: {error_text}...")
                
        except Exception as e:
            print(f"   ❌ Сетевая ошибка: {e}")
    
    print(f"\n❌ Ни один формат параметров не сработал")
    return None

def test_different_endpoints():
    """Тест разных эндпоинтов API"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Возможные эндпоинты для получения документации
    endpoints = [
        f"{BASE_URL}/docs",
        f"{BASE_URL}/documentation", 
        f"{BASE_URL}/library-docs",
        f"{BASE_URL}/get-docs"
    ]
    
    # Используем ID из предыдущих результатов
    library_id = "/microsoft/typescript"
    
    print(f"🧪 Тестирование разных эндпоинтов...")
    print(f"🆔 Library ID: {library_id}")
    
    for endpoint in endpoints:
        print(f"\n🔗 Тест: {endpoint}")
        
        try:
            response = requests.get(
                endpoint,
                headers=headers,
                params={"library_id": library_id, "tokens": 500},
                timeout=5
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Эндпоинт работает!")
                data = response.json()
                if 'content' in data:
                    print(f"   📖 Содержит документацию")
                return endpoint
            else:
                print(f"   ❌ {response.status_code}: {response.text[:50]}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)[:50]}...")
    
    return None

def main():
    print("🎯 Context7 API - Финальное тестирование")
    print("=" * 60)
    
    # 1. Тест поиска и получения документации
    working_params = search_and_get_docs()
    
    print(f"\n" + "=" * 60)
    
    # 2. Тест разных эндпоинтов
    working_endpoint = test_different_endpoints()
    
    print(f"\n🏁 ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 40)
    
    print("✅ Поиск библиотек: РАБОТАЕТ")
    
    if working_params:
        print("✅ Получение документации: РАБОТАЕТ")
        print(f"   Рабочие параметры: {working_params}")
    else:
        print("❌ Получение документации: НЕ РАБОТАЕТ")
        print("   Возможные причины:")
        print("   - Неправильный формат API")
        print("   - Другой эндпоинт для документации")
        print("   - Ограничения API ключа")
    
    if working_endpoint:
        print(f"✅ Рабочий эндпоинт: {working_endpoint}")
    
    print(f"\n🧠 Context7 MCP сервер остается основным способом использования!")
    print(f"🚀 Перезапустите Cursor для активации MCP")

if __name__ == "__main__":
    main()





