from pyngrok import ngrok
import sys

def setup_ngrok_auth():
    print("=== Настройка аутентификации ngrok ===")
    print("Эта программа настроит ваш токен аутентификации ngrok.\n")
    
    if len(sys.argv) > 1:
        auth_token = sys.argv[1]
    else:
        print("Пожалуйста, получите ваш токен по адресу:")
        print("https://dashboard.ngrok.com/get-started/your-authtoken")
        print("(Требуется бесплатная регистрация)\n")
        auth_token = input("Введите ваш токен аутентификации ngrok: ")
    
    if not auth_token:
        print("Ошибка: Токен не был введен.")
        return False
    
    try:
        print(f"Настройка токена: {auth_token}")
        ngrok.set_auth_token(auth_token)
        print("\n✅ Токен успешно настроен!")
        print("Теперь вы можете запустить 'start_public_server.bat' или 'python run_with_ngrok.py'")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка при настройке токена: {str(e)}")
        return False

if __name__ == "__main__":
    setup_ngrok_auth() 