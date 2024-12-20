import random
from collections import Counter

# --- Задание 1: Функция шифрования и дешифрования текста обобщенным шифром Цезаря ---
def caesar_cipher(text, key, decrypt=False):
    """
    Шифрует или дешифрует текст обобщенным шифром Цезаря.

    :param text: Исходный текст.
    :param key: Сдвиг для шифрования.
    :param decrypt: Если True, выполняется дешифрование.
    :return: Зашифрованный или расшифрованный текст.
    """
    if decrypt:
        key = -key  # При дешифровании сдвиг в обратную сторону
    encrypted_text = []
    for char in text:
        if char.isalpha():  # Шифруем только буквы
            offset = 65 if char.isupper() else 97
            encrypted_char = chr((ord(char) - offset + key) % 26 + offset)
            encrypted_text.append(encrypted_char)
        else:
            encrypted_text.append(char)  # Оставляем символы без изменений
    return ''.join(encrypted_text)

# --- Задание 2: Функция восстановления текста без знания ключа ---
def caesar_crack(ciphertext):
    """
    Восстанавливает текст, зашифрованный шифром Цезаря, без знания ключа.

    :param ciphertext: Зашифрованный текст.
    :return: Вероятно восстановленный текст.
    """
    # Подсчет частоты символов для предположения сдвига
    letter_counts = Counter(filter(str.isalpha, ciphertext.lower()))
    most_common_char, _ = letter_counts.most_common(1)[0]
    # Предполагаем, что наиболее частая буква — 'e' (в английском) или 'о'/'е' (в русском)
    assumed_char = 'e' if 'e' in ciphertext else 'о'
    key = (ord(most_common_char) - ord(assumed_char)) % 26
    return caesar_cipher(ciphertext, key, decrypt=True), key

# --- Задание 3: Шифр Вернама ---
def vernam_encrypt_decrypt(text, key=None):
    """
    Реализует шифрование и дешифрование текста шифром Вернама.

    :param text: Исходный текст.
    :param key: Ключ для шифрования/дешифрования. Если None, генерируется случайный.
    :return: Кортеж (зашифрованный текст, ключ).
    """
    if key is None:
        # Генерируем ключ равной длины случайными байтами
        key = ''.join(chr(random.randint(0, 255)) for _ in range(len(text)))
    encrypted_text = ''.join(chr(ord(t) ^ ord(k)) for t, k in zip(text, key))
    return encrypted_text, key

# --- Примеры использования ---
if __name__ == "__main__":
    print("=== Шифр Цезаря ===")
    # Шифрование
    plaintext = "Hello, World!"
    key = 3
    ciphertext = caesar_cipher(plaintext, key)
    print("Зашифрованный текст (Цезарь):", ciphertext)

    # Дешифрование
    decrypted_text = caesar_cipher(ciphertext, key, decrypt=True)
    print("Расшифрованный текст (Цезарь):", decrypted_text)

    # Взлом шифра Цезаря
    cracked_text, cracked_key = caesar_crack(ciphertext)
    print("Восстановленный текст:", cracked_text)
    print("Восстановленный ключ:", cracked_key)

    print("\n=== Шифр Вернама ===")
    # Шифрование
    plaintext_vernam = "Hello, Vernam Cipher!"
    ciphertext_vernam, vernam_key = vernam_encrypt_decrypt(plaintext_vernam)
    print("Зашифрованный текст (Вернам):", ciphertext_vernam)
    print("Ключ:", vernam_key)

    # Дешифрование
    decrypted_vernam, _ = vernam_encrypt_decrypt(ciphertext_vernam, vernam_key)
    print("Расшифрованный текст (Вернам):", decrypted_vernam)
