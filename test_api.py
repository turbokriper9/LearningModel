import requests
import json
import time

def test_attendance_api():
    """
    Тестирование API для отправки данных о посещаемости
    """
    url = "http://localhost:8000/api/v1/attendance"
    
    # Данные для отправки
    data = {
        "count": 5
    }
    
    try:
        print(f"Отправка данных: {data}")
        response = requests.post(url, json=data)
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {response.headers}")
        
        # Попытка получить JSON
        try:
            json_data = response.json()
            print(f"Ответ в формате JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"Ответ не является JSON: {response.text}")
        
        # Проверяем успешность запроса
        if response.ok:
            print("Тест УСПЕШЕН: данные сохранены")
        else:
            print(f"Тест ПРОВАЛЕН: ошибка сохранения данных ({response.status_code})")
            
    except requests.RequestException as e:
        print(f"Тест ПРОВАЛЕН: ошибка соединения - {e}")
    
    # Теперь попробуем получить список записей
    try:
        print("\nПолучение списка записей...")
        response = requests.get(url)
        
        if response.ok:
            data = response.json()
            print(f"Получено {len(data)} записей")
            if data:
                print("Последняя запись:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            print("Тест УСПЕШЕН: данные получены")
        else:
            print(f"Тест ПРОВАЛЕН: ошибка получения данных ({response.status_code})")
    
    except requests.RequestException as e:
        print(f"Тест ПРОВАЛЕН: ошибка соединения - {e}")

if __name__ == "__main__":
    # Ждем 3 секунды, чтобы сервер успел запуститься
    print("Ожидание запуска сервера...")
    time.sleep(3)
    
    # Запускаем тест
    test_attendance_api() 