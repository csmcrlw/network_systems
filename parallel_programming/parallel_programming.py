import random
import os
from multiprocessing import Pool
from typing import List, Tuple
import json

# Функция для генерации случайной матрицы заданной размерности
def generate_matrix(size: int) -> List[List[int]]:
    return [[random.randint(0, 10) for _ in range(size)] for _ in range(size)]

# Функция для записи матрицы в файл
def save_matrix_to_file(matrix: List[List[int]], filename: str):
    with open(filename, "w") as file:
        json.dump(matrix, file)

# Функция для чтения матрицы из файла
def load_matrix_from_file(filename: str) -> List[List[int]]:
    with open(filename, "r") as file:
        return json.load(file)

# Функция для вычисления одного элемента результирующей матрицы
def compute_element(args: Tuple[int, int, List[List[int]], List[List[int]]]) -> Tuple[int, int, int]:
    i, j, A, B = args
    result = sum(A[i][k] * B[k][j] for k in range(len(A[0])))
    return i, j, result

# Функция для выполнения перемножения матриц с использованием пула процессов
def multiply_matrices(A: List[List[int]], B: List[List[int]], result_file: str, pool_size: int):
    # Проверка на совместимость матриц
    if len(A[0]) != len(B):
        raise ValueError("Матрицы несовместимы для умножения.")

    # Создаем промежуточный файл для записи результата
    with open(result_file, "w") as f:
        f.write(json.dumps([[None] * len(B[0]) for _ in range(len(A))]))

    # Функция для записи результата в файл
    def write_result_to_file(index: Tuple[int, int, int]):
        i, j, value = index
        with open(result_file, "r+") as f:
            result_matrix = json.load(f)
            result_matrix[i][j] = value
            f.seek(0)
            json.dump(result_matrix, f)

    # Создаем задачи для пула процессов
    tasks = [(i, j, A, B) for i in range(len(A)) for j in range(len(B[0]))]
    with Pool(pool_size) as pool:
        for result in pool.imap(compute_element, tasks):
            write_result_to_file(result)

# Основная функция для управления процессом
def main():
    # Размер матриц
    size = 5  # Задайте размер матриц

    # Генерация и сохранение случайных матриц
    matrix1 = generate_matrix(size)
    matrix2 = generate_matrix(size)

    save_matrix_to_file(matrix1, "matrix1.json")
    save_matrix_to_file(matrix2, "matrix2.json")

    print("Матрицы сгенерированы и сохранены в файлы.")

    # Загрузка матриц из файлов
    A = load_matrix_from_file("matrix1.json")
    B = load_matrix_from_file("matrix2.json")

    print("Матрицы загружены из файлов.")

    # Умножение матриц с использованием пула процессов
    result_file = "result_matrix.json"
    try:
        multiply_matrices(A, B, result_file, pool_size=os.cpu_count())
        print(f"Результаты умножения записаны в файл {result_file}.")
    except ValueError as e:
        print(f"Ошибка: {e}")

    # Печать результата из файла
    result_matrix = load_matrix_from_file(result_file)
    print("Результирующая матрица:")
    for row in result_matrix:
        print(row)

if __name__ == "__main__":
    main()
