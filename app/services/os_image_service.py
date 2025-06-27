import json
import os
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class OSImageService:
    """Сервис для управления образами операционных систем"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.iso_dir = self.data_dir / "images" / "iso"
        self.catalog_file = self.data_dir / "os_catalog.json"
        
        # Создаем директории если их нет
        self.iso_dir.mkdir(parents=True, exist_ok=True)
    
    def get_os_catalog(self) -> List[Dict]:
        """Получить каталог доступных ОС"""
        try:
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
            
            # Добавляем информацию о наличии ISO файлов
            for os_info in catalog:
                iso_path = self.iso_dir / os_info['iso_filename']
                os_info['downloaded'] = iso_path.exists()
                if os_info['downloaded']:
                    stat = iso_path.stat()
                    os_info['file_size'] = stat.st_size
                    os_info['download_date'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                else:
                    os_info['file_size'] = 0
                    os_info['download_date'] = None
            
            return catalog
        except FileNotFoundError:
            return []
    
    def get_available_isos(self) -> List[Dict]:
        """Получить список скачанных ISO образов"""
        catalog = self.get_os_catalog()
        return [os_info for os_info in catalog if os_info.get('downloaded', False)]
    
    def get_os_by_id(self, os_id: str) -> Optional[Dict]:
        """Получить информацию об ОС по ID"""
        catalog = self.get_os_catalog()
        for os_info in catalog:
            if os_info['id'] == os_id:
                return os_info
        return None
    
    def download_iso(self, os_id: str, progress_callback=None) -> Dict:
        """Скачать ISO образ"""
        os_info = self.get_os_by_id(os_id)
        if not os_info:
            return {"success": False, "message": "ОС не найдена в каталоге"}
        
        iso_path = self.iso_dir / os_info['iso_filename']
        
        # Проверяем, не скачан ли уже файл
        if iso_path.exists():
            return {"success": False, "message": "ISO файл уже существует"}
        
        try:
            # Скачиваем файл
            print(f"🔽 Начинаем скачивание {os_info['name']}...")
            response = requests.get(os_info['download_url'], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(iso_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            # Проверяем контрольную сумму если есть
            if os_info.get('checksum'):
                if not self.verify_checksum(iso_path, os_info['checksum']):
                    iso_path.unlink()  # Удаляем поврежденный файл
                    return {"success": False, "message": "Ошибка контрольной суммы"}
            
            print(f"✅ {os_info['name']} успешно скачан")
            return {"success": True, "message": f"ISO образ {os_info['name']} скачан"}
            
        except requests.RequestException as e:
            return {"success": False, "message": f"Ошибка скачивания: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Неожиданная ошибка: {str(e)}"}
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Проверить контрольную сумму файла"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest() == expected_checksum
        except Exception:
            return False
    
    def delete_iso(self, os_id: str) -> Dict:
        """Удалить ISO образ"""
        os_info = self.get_os_by_id(os_id)
        if not os_info:
            return {"success": False, "message": "ОС не найдена"}
        
        iso_path = self.iso_dir / os_info['iso_filename']
        
        try:
            if iso_path.exists():
                iso_path.unlink()
                return {"success": True, "message": f"ISO образ {os_info['name']} удален"}
            else:
                return {"success": False, "message": "ISO файл не найден"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка удаления: {str(e)}"}
    
    def get_iso_info(self, iso_filename: str) -> Optional[Dict]:
        """Получить информацию об ISO файле"""
        iso_path = self.iso_dir / iso_filename
        
        if not iso_path.exists():
            return None
        
        stat = iso_path.stat()
        
        # Ищем в каталоге
        catalog = self.get_os_catalog()
        os_info = None
        for os_data in catalog:
            if os_data['iso_filename'] == iso_filename:
                os_info = os_data
                break
        
        return {
            "filename": iso_filename,
            "path": str(iso_path),
            "size": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "os_info": os_info
        }
    
    def scan_iso_directory(self) -> List[Dict]:
        """Сканировать директорию на наличие ISO файлов"""
        iso_files = []
        
        if not self.iso_dir.exists():
            return iso_files
        
        for iso_file in self.iso_dir.glob("*.iso"):
            info = self.get_iso_info(iso_file.name)
            if info:
                iso_files.append(info)
        
        return iso_files
    
    def add_custom_iso(self, iso_path: str, name: str, description: str = "") -> Dict:
        """Добавить пользовательский ISO образ"""
        source_path = Path(iso_path)
        
        if not source_path.exists():
            return {"success": False, "message": "Исходный файл не найден"}
        
        if not source_path.suffix.lower() == '.iso':
            return {"success": False, "message": "Файл должен иметь расширение .iso"}
        
        # Копируем файл в директорию образов
        destination = self.iso_dir / source_path.name
        
        try:
            import shutil
            shutil.copy2(source_path, destination)
            
            return {
                "success": True, 
                "message": f"ISO образ '{name}' добавлен",
                "filename": source_path.name
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка копирования: {str(e)}"}


# Глобальный экземпляр сервиса
os_image_service = OSImageService()

# Функции-обертки для удобного использования в API
def get_available_os_images():
    """Получить каталог доступных ОС"""
    return os_image_service.get_os_catalog()

def get_local_iso_files():
    """Получить список локальных ISO файлов"""
    return os_image_service.scan_iso_directory()

def scan_iso_directory():
    """Сканировать директорию с ISO образами"""
    files = os_image_service.scan_iso_directory()
    total_size = sum(f.get('size', 0) for f in files)
    
    return {
        "found": len(files),
        "files": files,
        "total_size": total_size,
        "directory": str(os_image_service.iso_dir)
    }

def download_os_image(os_id: str):
    """Скачать образ ОС"""
    return os_image_service.download_iso(os_id)

def add_iso_file(source_path: str, name: str = "Custom ISO"):
    """Добавить ISO файл"""
    return os_image_service.add_custom_iso(source_path, name)
