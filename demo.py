#!/usr/bin/env python3
"""
Демо-режим KVM Web Platform
Показывает интерфейс без реального подключения к libvirt
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Создаем демо-данные
demo_vms = [
    {
        "id": "vm-001",
        "name": "Ubuntu-Server-22.04",
        "status": "running",
        "memory": 2048,
        "vcpus": 2,
        "disk_size": "20G",
        "ip_address": "192.168.122.10",
        "os": "Ubuntu 22.04 LTS",
        "created": "2024-01-15T10:30:00",
        "uptime": "5 days, 3 hours"
    },
    {
        "id": "vm-002", 
        "name": "CentOS-Stream-9",
        "status": "stopped",
        "memory": 1024,
        "vcpus": 1,
        "disk_size": "15G",
        "ip_address": "192.168.122.11",
        "os": "CentOS Stream 9",
        "created": "2024-01-10T14:22:00",
        "uptime": "0"
    },
    {
        "id": "vm-003",
        "name": "Windows-11-Pro",
        "status": "running",
        "memory": 4096,
        "vcpus": 4,
        "disk_size": "50G",
        "ip_address": "192.168.122.12",
        "os": "Windows 11 Pro",
        "created": "2024-01-20T09:15:00",
        "uptime": "2 days, 15 hours"
    }
]

def create_demo_data():
    """Создает демо-данные для тестирования"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Создаем JSON файл с демо ВМ
    with open(data_dir / "demo_vms.json", "w", encoding="utf-8") as f:
        json.dump(demo_vms, f, indent=2, ensure_ascii=False)
    
    # Создаем демо ISO образы
    iso_dir = data_dir / "images" / "iso"
    iso_dir.mkdir(parents=True, exist_ok=True)
    
    demo_isos = [
        "ubuntu-22.04.3-desktop-amd64.iso",
        "CentOS-Stream-9-x86_64-dvd1.iso", 
        "Win11_22H2_Russian_x64.iso",
        "debian-12.2.0-amd64-DVD-1.iso"
    ]
    
    for iso in demo_isos:
        iso_file = iso_dir / iso
        if not iso_file.exists():
            # Создаем пустые файлы для демо
            iso_file.write_text(f"# Демо ISO файл: {iso}\n")
    
    print("✅ Демо-данные созданы!")
    print(f"📂 Директория данных: {data_dir.absolute()}")
    print(f"💿 ISO образы: {iso_dir.absolute()}")

if __name__ == "__main__":
    create_demo_data()
    print("\n🎭 Демо-режим готов!")
    print("Запустите: python main.py")
