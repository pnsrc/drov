import os
from pathlib import Path


class Settings:
    """Простая конфигурация без pydantic для демо-режима"""
    
    def __init__(self):
        # Server settings
        self.HOST = "0.0.0.0"
        self.PORT = 8001  # Изменим на 8001 чтобы избежать конфликтов
        self.DEBUG = True
        
        # Database
        self.DATABASE_URL = "sqlite:///./kvm_platform.db"
        
        # Пути к директориям (относительно корня проекта)
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        
        # KVM/Libvirt settings
        self.LIBVIRT_URI = "qemu:///system"
        self.VM_STORAGE_PATH = str(self.DATA_DIR / "vms")
        self.ISO_STORAGE_PATH = str(self.DATA_DIR / "images" / "iso")
        
        # VNC settings
        self.VNC_HOST = "localhost"
        self.VNC_PORT_RANGE_START = 5900
        self.VNC_PORT_RANGE_END = 5999
        
        # Security
        self.SECRET_KEY = "your-secret-key-change-in-production"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        # Создаем директории если их нет
        self._create_directories()
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.DATA_DIR,
            self.DATA_DIR / "vms",
            self.DATA_DIR / "images" / "iso",
            self.DATA_DIR / "storage",
            self.BASE_DIR / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()


settings = Settings()
