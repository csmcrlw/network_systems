import socket
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # Для отображения прогресс-бара

# Функция для проверки доступности порта
def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            return port  # Порт открыт
        return None  # Порт закрыт
    except socket.error:
        return None
    finally:
        sock.close()

# Функция для запуска сканера
def scan_ports(host):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:  # Пул потоков, 100 потоков одновременно
        futures = []
        progress_bar = tqdm(range(1, 65536), desc="Сканирование портов", ncols=100)

        for port in range(1, 65536):  # Сканируем все порты от 1 до 65535
            futures.append(executor.submit(check_port, host, port))

        # Ожидаем завершения всех потоков и собираем результаты
        for future in futures:
            result = future.result()
            if result:
                open_ports.append(result)
            progress_bar.update(1)

        progress_bar.close()

    return open_ports

# Основной код для запуска сканера
if __name__ == "__main__":
    host = input("Введите хост (IP или имя хоста): ")
    print("Начинаем сканирование портов...")

    open_ports = scan_ports(host)

    print(f"\nОткрытые порты на {host}:")
    for port in open_ports:
        print(f"Порт {port} открыт.")

