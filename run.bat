@echo off
setlocal

REM Установка кодировки для корректного отображения в консоли
chcp 65001 >nul

REM Проверка наличия Python по указанному пути
set PYTHON_PATH=C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYTHON_PATH%" (
    echo Python не найден по пути %PYTHON_PATH%. Проверка в PATH...
    set PYTHON_PATH=
    for /f "usebackq tokens=*" %%i in (`where python 2^>nul`) do set PYTHON_PATH=%%i

    if "%PYTHON_PATH%"=="" (
        echo Python не найден. Скачивание и установка Python 3.12...
        curl -o python-installer.exe https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
        start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

        REM Проверка, удалось ли установить Python
        set PYTHON_PATH=C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe
        if not exist "%PYTHON_PATH%" (
            echo Ошибка установки Python. Убедитесь, что установка прошла успешно, и повторите попытку.
            pause
            exit /b
        )
    )
) else (
    echo Python найден по пути: %PYTHON_PATH%
)

REM Создание виртуального окружения
echo Создание виртуального окружения...
"%PYTHON_PATH%" -m venv venv

REM Проверка, что виртуальное окружение создано
if not exist venv\Scripts\activate.bat (
    echo Ошибка создания виртуального окружения.
    pause
    exit /b
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate

REM Установка зависимостей
echo Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

REM Запуск вашего приложения
echo Запуск приложения...
python linkedindumper.py

pause
