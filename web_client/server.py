import socket
import os

HOST = ''  # Сервер слушает все доступные интерфейсы
PORT = 80  # Используем порт 80, если доступен, иначе 8080

# Попытка запустить сервер на порту 80, если занят, переключаемся на 8080
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
except OSError:
    PORT = 8080
    server_socket.bind((HOST, PORT))

server_socket.listen(5)
print(f"Сервер запущен на порту {PORT}...")

def get_content_type(file_path):
    """ Определение MIME-типа файла """
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".js"):
        return "application/javascript"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    elif file_path.endswith(".png"):
        return "image/png"
    else:
        return "text/plain"

while True:
    conn, addr = server_socket.accept()
    print("Подключение от", addr)

    request = conn.recv(1024).decode()
    if not request:
        conn.close()
        continue

    # Разбираем HTTP-запрос
    first_line = request.split("\n")[0]
    parts = first_line.split()
    if len(parts) < 2:
        conn.close()
        continue

    method, path = parts[0], parts[1]

    if path == "/":
        path = "/index.html"  # По умолчанию загружаем index.html

    file_path = "." + path  # Делаем путь относительным к текущей папке

    # Проверяем существование файла
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            response_body = f.read()
        content_type = get_content_type(file_path)
        response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response_body)}\r\n\r\n"
        conn.send(response_header.encode() + response_body)
    else:
        # Если файл не найден, отправляем 404
        response_body = b"<h1>404 Not Found</h1>"
        response_header = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(response_body)}\r\n\r\n"
        conn.send(response_header.encode() + response_body)

    conn.close()
