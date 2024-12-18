import socket
import threading


# Обработчик для каждого клиента
def handle_client(client_socket, client_address):
    print(f"Подключение от {client_address}")

    # Бесконечный цикл для обработки сообщений от клиента
    while True:
        message = client_socket.recv(1024)
        if not message:
            break  # Если клиент разорвал соединение
        print(f"Получено от {client_address}: {message.decode()}")
        client_socket.send(message)  # Отправляем обратно эхо
    client_socket.close()
    print(f"Соединение с {client_address} закрыто.")


# Создание и запуск сервера
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9090))  # Сервер слушает на порту 9090
    server.listen(5)
    print("Сервер запущен, ожидаем подключения...")

    while True:
        client_socket, client_address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()


# Запуск сервера
if __name__ == "__main__":
    start_server()


