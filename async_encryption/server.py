import socket
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Путь к файлам для хранения ключей
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"


# Генерация пары ключей RSA
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    # Сохраняем приватный ключ
    with open(PRIVATE_KEY_FILE, "wb") as private_key_file:
        private_key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Сохраняем публичный ключ
    with open(PUBLIC_KEY_FILE, "wb") as public_key_file:
        public_key_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return private_key, public_key


# Загрузка ключей из файлов
def load_keys():
    # Загрузка приватного ключа
    with open(PRIVATE_KEY_FILE, "rb") as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None,
            backend=default_backend()
        )

    # Загрузка публичного ключа
    with open(PUBLIC_KEY_FILE, "rb") as public_key_file:
        public_key = serialization.load_pem_public_key(
            public_key_file.read(),
            backend=default_backend()
        )

    return private_key, public_key


# Шифрование сообщения с использованием публичного ключа
def encrypt_message(message, public_key):
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


# Дешифрование сообщения с использованием приватного ключа
def decrypt_message(encrypted_message, private_key):
    decrypted = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()


# --- Обработка подключения клиента ---
def handle_client_connection(client_socket):
    # Загружаем серверный приватный и публичный ключи
    private_key, public_key = load_keys()

    # Получаем публичный ключ клиента
    client_public_key_data = client_socket.recv(4096)
    client_public_key = serialization.load_pem_public_key(client_public_key_data, backend=default_backend())

    print("Получен публичный ключ клиента.")

    # Отправляем свой публичный ключ клиенту
    client_socket.send(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

    # Получаем зашифрованное сообщение от клиента
    encrypted_message = client_socket.recv(4096)
    decrypted_message = decrypt_message(encrypted_message, private_key)
    print(f"Расшифрованное сообщение от клиента: {decrypted_message}")

    # Отправляем ответ клиенту, шифруя его с помощью публичного ключа клиента
    response = "Сообщение от сервера"
    encrypted_response = encrypt_message(response, client_public_key)
    client_socket.send(encrypted_response)

    client_socket.close()


# Серверный код
def start_server(host="127.0.0.1", port=65432):
    # Проверяем, существуют ли уже ключи
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
        print("Генерация ключей...")
        generate_rsa_keys()

    # Создаем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Подключен клиент {addr}")
        handle_client_connection(client_socket)


# --- Основной код для запуска сервера ---
if __name__ == "__main__":
    start_server()
