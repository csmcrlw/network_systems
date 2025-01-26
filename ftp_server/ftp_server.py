import os
import socket

# Настройки сервера
HOST = '127.0.0.1'  # Локальный хост
PORT = 65432  # Порт для прослушивания
WORKING_DIR = "./server_directory"  # Рабочая директория сервера

# Создание рабочей директории, если её нет
os.makedirs(WORKING_DIR, exist_ok=True)


# Функция для обработки команд
def handle_command(command, conn):
    try:
        parts = command.strip().split(' ', 2)
        cmd = parts[0].lower()

        if cmd == 'ls':  # Просмотр списка файлов и папок
            files = os.listdir(WORKING_DIR)
            conn.sendall("\n".join(files).encode())

        elif cmd == 'mkdir':  # Создание папки
            if len(parts) < 2:
                conn.sendall(b"Error: Directory name is required")
            else:
                dir_name = os.path.join(WORKING_DIR, parts[1])
                os.makedirs(dir_name, exist_ok=True)
                conn.sendall(b"Directory created successfully")

        elif cmd == 'rmdir':  # Удаление папки
            if len(parts) < 2:
                conn.sendall(b"Error: Directory name is required")
            else:
                dir_name = os.path.join(WORKING_DIR, parts[1])
                os.rmdir(dir_name)
                conn.sendall(b"Directory removed successfully")

        elif cmd == 'create':  # Создание файла
            if len(parts) < 3:
                conn.sendall(b"Error: File name and content are required")
            else:
                file_name = os.path.join(WORKING_DIR, parts[1])
                with open(file_name, 'w') as f:
                    f.write(parts[2])
                conn.sendall(b"File created successfully")

        elif cmd == 'read':  # Чтение файла
            if len(parts) < 2:
                conn.sendall(b"Error: File name is required")
            else:
                file_name = os.path.join(WORKING_DIR, parts[1])
                with open(file_name, 'r') as f:
                    content = f.read()
                conn.sendall(content.encode())

        elif cmd == 'rename':  # Переименование файла/папки
            if len(parts) < 3:
                conn.sendall(b"Error: Source and target names are required")
            else:
                src = os.path.join(WORKING_DIR, parts[1])
                dest = os.path.join(WORKING_DIR, parts[2])
                os.rename(src, dest)
                conn.sendall(b"Renamed successfully")

        elif cmd == 'delete':  # Удаление файла
            if len(parts) < 2:
                conn.sendall(b"Error: File name is required")
            else:
                file_name = os.path.join(WORKING_DIR, parts[1])
                os.remove(file_name)
                conn.sendall(b"File deleted successfully")

        elif cmd == 'copy':  # Копирование файла
            if len(parts) < 3:
                conn.sendall(b"Error: Source and destination names are required")
            else:
                src = os.path.join(WORKING_DIR, parts[1])
                dest = os.path.join(WORKING_DIR, parts[2])
                with open(src, 'r') as f_src:
                    with open(dest, 'w') as f_dest:
                        f_dest.write(f_src.read())
                conn.sendall(b"File copied successfully")

        else:
            conn.sendall(b"Error: Unknown command")

    except Exception as e:
        conn.sendall(f"Error: {str(e)}".encode())


# Точка входа
if __name__ == "__main__":
    # Запуск сервера
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server started at {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode()
                    handle_command(command, conn)
