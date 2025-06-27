from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class VMCreate(BaseModel):
    """Схема для создания новой ВМ"""
    name: str = Field(..., description="Имя виртуальной машины")
    memory: int = Field(1024, description="Объем оперативной памяти в МБ", ge=512)
    vcpus: int = Field(1, description="Количество виртуальных процессоров", ge=1, le=16)
    disk_size: int = Field(10, description="Размер диска в ГБ", ge=5)
    iso_path: Optional[str] = Field(None, description="Путь к ISO образу для установки")
    network: str = Field("default", description="Сетевая конфигурация")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "ubuntu-server-01",
                "memory": 2048,
                "vcpus": 2,
                "disk_size": 20,
                "iso_path": "/var/lib/libvirt/images/iso/ubuntu-22.04.iso",
                "network": "default"
            }
        }


class VMMemoryInfo(BaseModel):
    """Информация о памяти ВМ"""
    max: int = Field(..., description="Максимальный объем памяти в байтах")
    used: int = Field(..., description="Используемый объем памяти в байтах")


class VMResponse(BaseModel):
    """Схема ответа с информацией о ВМ"""
    id: Optional[int] = Field(None, description="ID запущенной ВМ")
    name: str = Field(..., description="Имя виртуальной машины")
    uuid: str = Field(..., description="Уникальный идентификатор ВМ")
    state: str = Field(..., description="Состояние ВМ")
    memory: VMMemoryInfo = Field(..., description="Информация о памяти")
    vcpus: int = Field(..., description="Количество виртуальных процессоров")
    cpu_time: int = Field(..., description="Время процессора в наносекундах")
    is_active: bool = Field(..., description="Запущена ли ВМ")
    
    # Дополнительные поля для детальной информации
    xml: Optional[str] = Field(None, description="XML конфигурация")
    disks: Optional[List[str]] = Field(None, description="Список дисков")
    vnc: Optional[Dict[str, Any]] = Field(None, description="Информация VNC")


class VMListResponse(BaseModel):
    """Схема списка ВМ"""
    vms: List[VMResponse]
    total: int = Field(..., description="Общее количество ВМ")


class VMAction(BaseModel):
    """Схема для действий с ВМ"""
    action: str = Field(..., description="Действие: start, stop, restart, pause, resume")
    force: bool = Field(False, description="Принудительное выполнение")


class VNCInfo(BaseModel):
    """Информация для VNC подключения"""
    host: str = Field(..., description="Хост для подключения")
    port: int = Field(..., description="Порт VNC")
    url: str = Field(..., description="URL для подключения")


class HostStats(BaseModel):
    """Статистика хост-системы"""
    cpu_percent: float = Field(..., description="Загрузка процессора в %")
    memory: Dict[str, Any] = Field(..., description="Информация о памяти")
    disk: Dict[str, Any] = Field(..., description="Информация о дисках")
    network: Dict[str, Any] = Field(..., description="Сетевая статистика")
    timestamp: str = Field(..., description="Время получения статистики")


class APIResponse(BaseModel):
    """Базовая схема ответа API"""
    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    data: Optional[Any] = Field(None, description="Данные ответа")


class ErrorResponse(BaseModel):
    """Схема ошибки"""
    detail: str = Field(..., description="Описание ошибки")
    error_code: Optional[str] = Field(None, description="Код ошибки")


# Схемы для ISO образов
class ISOInfo(BaseModel):
    """Информация об ISO образе"""
    name: str = Field(..., description="Имя файла")
    path: str = Field(..., description="Полный путь к файлу")
    size: int = Field(..., description="Размер файла в байтах")
    created: datetime = Field(..., description="Дата создания")


class NetworkInfo(BaseModel):
    """Информация о сети"""
    name: str = Field(..., description="Имя сети")
    bridge: str = Field(..., description="Мост сети")
    is_active: bool = Field(..., description="Активна ли сеть")
    autostart: bool = Field(..., description="Автозапуск")


# Схемы для снапшотов
class SnapshotCreate(BaseModel):
    """Создание снапшота"""
    name: str = Field(..., description="Имя снапшота")
    description: Optional[str] = Field(None, description="Описание снапшота")


class SnapshotInfo(BaseModel):
    """Информация о снапшоте"""
    name: str = Field(..., description="Имя снапшота")
    description: Optional[str] = Field(None, description="Описание")
    created: datetime = Field(..., description="Дата создания")
    state: str = Field(..., description="Состояние ВМ в момент снапшота")
