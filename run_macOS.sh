#!/bin/bash

# Установка кодировки UTF-8 (по умолчанию в macOS)
export LANG=en_US.UTF-8

# Определение директории, в которой находится скрипт
SCRIPT_DIR=$(dirname "$0")

# Проверка наличия Python по указанному пути
PYTHON_PATH="/usr/local/bin/python3"
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Python не найден по пути $PYTHON_PATH. Проверка в PATH..."
    PYTHON_PATH=$(which python3)

    if [ -z "$PYTHON_PATH" ]; then
        echo "Python не найден. Скачивание и установка Python 3.12..."
        curl -o python-installer.pkg https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg
        sudo installer -pkg python-installer.pkg -target /

        # Проверка, удалось ли установить Python
        PYTHON_PATH=$(which python3)
        if [ -z "$PYTHON_PATH" ]; then
            echo "Ошибка установки Python. Убедитесь, что установка прошла успешно, и повторите попытку."
            exit 1
        fi
    fi
else
    echo "Python найден по пути: $PYTHON_PATH"
fi

# Создание виртуального окружения
echo "Создание виртуального окружения..."
$PYTHON_PATH -m venv "$SCRIPT_DIR/venv"

# Проверка, что виртуальное окружение создано
if [ ! -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "Ошибка создания виртуального окружения."
    exit 1
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source "$SCRIPT_DIR/venv/bin/activate"

# Установка зависимостей
echo "Установка зависимостей..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

# Запуск вашего приложения
echo "Запуск приложения..."
python "$SCRIPT_DIR/linkedindumper.py"
