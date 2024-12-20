import asyncio
import argparse

# Конфигурация хоста и порта
HOST = '127.0.0.1'
PORT = 8888

# Асинхронная функция эхо-сервера
async def handle_echo(reader, writer):
    try:
        # Чтение данных от клиента
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Получено сообщение от {addr}: {message}")

        # Отправка данных обратно клиенту
        writer.write(data)
        await writer.drain()
        print(f"Сообщение отправлено обратно клиенту: {message}")

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        print("Закрытие соединения")
        writer.close()
        await writer.wait_closed()

# Запуск сервера
async def start_server():
    server = await asyncio.start_server(handle_echo, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"Сервер запущен на {addr}")

    async with server:
        await server.serve_forever()

# Асинхронная функция клиента
async def tcp_echo_client(host, port):
    try:
        # Установка соединения с сервером
        reader, writer = await asyncio.open_connection(host, port)
        print("Соединение с сервером установлено")

        # Отправка сообщения серверу
        message = input("Введите сообщение для сервера: ")
        writer.write(message.encode())
        await writer.drain()

        # Чтение ответа от сервера
        data = await reader.read(100)
        print(f"Ответ от сервера: {data.decode()}")

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        print("Закрытие соединения с сервером")
        writer.close()
        await writer.wait_closed()

# Основная функция для запуска сервера или клиента
def main():
    parser = argparse.ArgumentParser(description="Эхо-сервер и клиент")
    parser.add_argument(
        "mode", choices=["server", "client"], help="Режим работы: server или client"
    )
    args = parser.parse_args()

    if args.mode == "server":
        # Запуск сервера
        asyncio.run(start_server())
    elif args.mode == "client":
        # Запуск клиента
        asyncio.run(tcp_echo_client(HOST, PORT))

if __name__ == "__main__":
    main()
