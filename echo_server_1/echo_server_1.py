import socket
import threading
import logging
import json
import hashlib
import os

# Настройки по умолчанию
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9090
LOG_FILE = "server.log"
USER_FILE = "users.json"  # Для хранения имен и паролей

# Установка логирования
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Загрузка пользователей из файла или создание нового
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}
    with open(USER_FILE, "w") as f:
        json.dump(user_data, f)


def save_users():
    """Сохранить данные пользователей."""
    with open(USER_FILE, "w") as f:
        json.dump(user_data, f)


def hash_password(password):
    """Хэшировать пароль для безопасного хранения."""
    return hashlib.sha256(password.encode()).hexdigest()


def send_message(sock, message):
    """Отправка сообщения с заголовком длины."""
    message = message.encode()
    length = len(message)
    sock.send(f"{length:<10}".encode() + message)


def receive_message(sock):
    """Получение сообщения с учетом заголовка длины."""
    header = sock.recv(10).decode().strip()
    if not header:
        return None
    length = int(header)
    return sock.recv(length).decode()


def handle_client(conn, addr):
    """Обработка подключенного клиента."""
    try:
        logging.info(f"Подключился клиент {addr}")

        # Проверка идентификации
        if addr[0] in user_data:
            send_message(conn, f"Добро пожаловать обратно, {user_data[addr[0]]['name']}!")
        else:
            send_message(conn, "Вы новый клиент! Пожалуйста, введите ваше имя:")
            name = receive_message(conn)
            send_message(conn, "Введите пароль:")
            password = receive_message(conn)

            user_data[addr[0]] = {"name": name, "password": hash_password(password)}
            save_users()
            send_message(conn, f"Добро пожаловать, {name}! Ваши данные сохранены.")

        # Аутентификация
        while True:
            send_message(conn, "Введите ваш пароль для входа:")
            password = receive_message(conn)
            if user_data[addr[0]]["password"] == hash_password(password):
                send_message(conn, "Успешная аутентификация!")
                break
            else:
                send_message(conn, "Неверный пароль. Попробуйте снова.")

        # Общение
        while True:
            send_message(conn, "Введите сообщение (или 'exit' для выхода):")
            message = receive_message(conn)
            if message == "exit":
                send_message(conn, "Вы отключились от сервера.")
                break
            send_message(conn, f"Вы сказали: {message}")
    except Exception as e:
        logging.error(f"Ошибка при работе с клиентом {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Клиент {addr} отключился.")


def start_server():
    """Запуск сервера."""
    host = input(f"Введите хост (по умолчанию {DEFAULT_HOST}): ") or DEFAULT_HOST
    port = input(f"Введите порт (по умолчанию {DEFAULT_PORT}): ") or DEFAULT_PORT

    try:
        port = int(port)
    except ValueError:
        port = DEFAULT_PORT

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.listen(5)
            logging.info(f"Сервер запущен на {host}:{port}")
            print(f"Сервер запущен на {host}:{port}")
            break
        except OSError:
            logging.warning(f"Порт {port} занят, пытаюсь использовать следующий.")
            port += 1

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()
