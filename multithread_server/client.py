import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9090))  # Подключение к серверу

    while True:
        message = input("Введите сообщение для сервера (или 'exit' для выхода): ")
        if message.lower() == 'exit':
            client.send(message.encode())
            break
        client.send(message.encode())
        response = client.recv(1024)
        print(f"Ответ от сервера: {response.decode()}")

    client.close()

if __name__ == "__main__":
    start_client()


