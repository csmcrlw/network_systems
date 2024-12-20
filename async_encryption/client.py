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


# --- Клиентский код ---
def start_client(host="127.0.0.1", port=65432):
    # Проверяем, существуют ли уже ключи
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
        print("Генерация ключей...")
        generate_rsa_keys()

    # Создаем сокет
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Загружаем клиентские ключи
    private_key, public_key = load_keys()

    # Отправляем серверу свой публичный ключ
    client_socket.send(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

    # Получаем публичный ключ сервера
    server_public_key_data = client_socket.recv(4096)
    server_public_key = serialization.load_pem_public_key(server_public_key_data, backend=default_backend())

    print("Получен публичный ключ сервера.")

    # Шифруем сообщение и отправляем серверу
    message = "Привет, сервер!"
    encrypted_message = encrypt_message(message, server_public_key)
    client_socket.send(encrypted_message)

    # Получаем ответ от сервера
    encrypted_response = client_socket.recv(4096)
    decrypted_response = decrypt_message(encrypted_response, private_key)
    print(f"Расшифрованный ответ от сервера: {decrypted_response}")

    client_socket.close()


# --- Основной код для запуска клиента ---
if __name__ == "__main__":
    start_client()
