#!/bin/bash

# Определение ОС
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "🖥️  Обнаружена система: $OS $ARCH"

# Установка зависимостей системы
echo "📦 Установка системных зависимостей..."

# Для macOS (с поддержкой M1/M2)
if [[ "$OS" == "Darwin" ]]; then
    echo "🍎 Настройка для macOS..."
    
    # Проверка Homebrew
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew не найден. Установите Homebrew сначала:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Установка QEMU для эмуляции (KVM не поддерживается на macOS)
    brew install qemu python3
    
    echo "⚠️  На macOS будет использоваться QEMU эмуляция (медленнее KVM)"

# Для Ubuntu/Debian
elif command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager python3-pip python3-venv

# Для CentOS/RHEL/Fedora  
elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
    if command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
    else
        PKG_MANAGER="yum"
    fi
    
    sudo $PKG_MANAGER install -y qemu-kvm libvirt libvirt-daemon-system libvirt-clients bridge-utils virt-manager python3-pip python3-venv
fi

# Создание виртуального окружения
echo "🐍 Создание Python окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
echo "📚 Установка Python библиотек..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание локальных директорий в проекте
echo "📁 Создание локальных директорий..."
mkdir -p data/images/iso
mkdir -p data/vms
mkdir -p data/storage
mkdir -p logs

# Настройка libvirt (только для Linux)
if [[ "$OS" != "Darwin" ]]; then
    echo "👤 Настройка пользователя..."
    sudo usermod -a -G libvirt $USER

    # Запуск libvirt
    echo "🚀 Запуск libvirt..."
    sudo systemctl enable libvirtd
    sudo systemctl start libvirtd
fi

echo "✅ Установка завершена!"
echo ""
echo "Для запуска платформы:"
echo "1. source venv/bin/activate"
echo "2. python main.py"
echo ""
echo "Откройте браузер: http://localhost:8000"
