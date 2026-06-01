# 🚀 Local Messenger

> Анонимный локальный мессенджер для обмена сообщениями, файлами и голосовыми сообщениями внутри локальной сети.

<p align="center">

<a href="#-установка-openssl">
    <img src="https://img.shields.io/badge/OpenSSL-Установка-blue?style=for-the-badge">
</a>

<a href="#-создание-виртуального-окружения">
    <img src="https://img.shields.io/badge/Python-Venv-green?style=for-the-badge">
</a>

<a href="#-установка-зависимостей">
    <img src="https://img.shields.io/badge/PIP-Requirements-orange?style=for-the-badge">
</a>

<a href="#-создание-ssl-ключа">
    <img src="https://img.shields.io/badge/SSL-Generate-red?style=for-the-badge">
</a>

<a href="#-запуск-сервера">
    <img src="https://img.shields.io/badge/Launch-Run_Server-purple?style=for-the-badge">
</a>

</p>

---

# Проверка openssl

openssl version

Если не установлен:

Windows: 

https://slproweb.com/products/Win32OpenSSL.html

macOS: 

brew install openssl

Linux:

sudo apt update

sudo apt install openssl

---

## ⚡ Запуск

### Windows

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

openssl genrsa -out private.key 2048

openssl req -new -x509 -key private.key -out certificate.crt -days 365

python app.py

---

### macOS / Linux

cd backend

python3 -m venv venv

source venv/bin/activate 

pip install -r requirements.txt 

openssl genrsa -out private.key 2048 

openssl req -new -x509 -key private.key -out certificate.crt -days 365 

python app.py 

---

Открыть:

🔗 https://localhost:8888

или

🔗 https://IP_АДРЕС(будет виден после запуска app.py):8888
