#!/bin/bash

echo "🚀 Запуск KVM Web Platform..."

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Запустите: ./install.sh"
    exit 1
fi

# Активация виртуального окружения
source venv/bin/activate

# Проверка операционной системы
OS="$(uname -s)"
if [[ "$OS" == "Darwin" ]]; then
    echo "🍎 macOS обнаружена - используется QEMU эмуляция"
else
    echo "🐧 Linux обнаружена - используется KVM"
fi

# Создание директорий если их нет
mkdir -p data/images/iso data/vms data/storage logs

# Запуск сервера
echo "🌐 Сервер будет доступен по адресу: http://localhost:8000"

# Активация окружения
source venv/bin/activate

# Проверка libvirt
if ! systemctl is-active --quiet libvirtd; then
    echo "🔧 Запуск libvirt..."
    sudo systemctl start libvirtd
fi

# Запуск приложения
echo "🌐 Сервер запускается на http://localhost:8000"
python main.py
