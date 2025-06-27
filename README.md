# KVM Web Platform

Веб-платформа для создания и управления виртуальными машинами KVM через браузер.

## Архитектура

- **Backend**: FastAPI + libvirt для управления KVM
- **Frontend**: React/Vue.js веб-интерфейс
- **VNC/Console**: noVNC для удаленного доступа к ВМ через браузер
- **WebSocket**: Для real-time обновлений статуса ВМ

## Возможности

- 🖥️ Веб-интерфейс для управления ВМ
- 🚀 Создание ВМ из готовых образов
- 📺 VNC консоль в браузере
- 📊 Мониторинг ресурсов в реальном времени
- 💾 Управление дисками и сетью
- 📷 Снапшоты и клонирование
- 🔧 REST API для автоматизации

## Установка

1. Установите зависимости системы (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager novnc websockify
```

2. Установите Python зависимости:
```bash
pip install -r requirements.txt
```

3. Добавьте пользователя в группу libvirt:
```bash
sudo usermod -a -G libvirt $USER
```

4. Запустите сервер:
```bash
python main.py
```

## Использование

1. Откройте браузер: http://localhost:8000
2. Загрузите образы ОС через веб-интерфейс
3. Создавайте и управляйте ВМ через GUI
4. Подключайтесь к консоли ВМ прямо в браузере

## API Endpoints

- `GET /api/vms` - Список всех ВМ
- `POST /api/vms` - Создать новую ВМ
- `GET /api/vms/{vm_id}` - Информация о ВМ
- `POST /api/vms/{vm_id}/start` - Запустить ВМ
- `POST /api/vms/{vm_id}/stop` - Остановить ВМ
- `GET /api/vms/{vm_id}/console` - VNC консоль
