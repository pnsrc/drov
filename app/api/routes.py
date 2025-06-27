"""
Упрощенные API роуты для демо-режима
"""

try:
    from fastapi import APIRouter, HTTPException
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from app.services.kvm_service import kvm_service


if FASTAPI_AVAILABLE:
    router = APIRouter()

    @router.get("/vms")
    async def list_vms():
        """Получить список всех виртуальных машин"""
        try:
            vms = kvm_service.get_all_vms()
            return vms
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/vms/{vm_name}")
    async def get_vm(vm_name: str):
        """Получить информацию о конкретной ВМ"""
        try:
            vm = kvm_service.get_vm_info(vm_name)
            if vm is None:
                raise HTTPException(status_code=404, detail="ВМ не найдена")
            return vm
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/vms")
    async def create_vm(vm_data: dict):
        """Создать новую виртуальную машину"""
        try:
            result = kvm_service.create_vm(vm_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/vms/{vm_name}/start")
    async def start_vm(vm_name: str):
        """Запустить виртуальную машину"""
        try:
            result = kvm_service.start_vm(vm_name)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/vms/{vm_name}/stop")
    async def stop_vm(vm_name: str, force: bool = False):
        """Остановить виртуальную машину"""
        try:
            if force:
                result = kvm_service.force_stop_vm(vm_name)
            else:
                result = kvm_service.stop_vm(vm_name)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/vms/{vm_name}/restart")
    async def restart_vm(vm_name: str):
        """Перезагрузить виртуальную машину"""
        try:
            result = kvm_service.restart_vm(vm_name)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/vms/{vm_name}")
    async def delete_vm(vm_name: str):
        """Удалить виртуальную машину"""
        try:
            result = kvm_service.delete_vm(vm_name)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/vms/{vm_name}/console/viewer", response_class=HTMLResponse)
    async def vm_console_viewer(vm_name: str):
        """Веб-страница с VNC консолью"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Console - {vm_name}</title>
            <meta charset="utf-8">
            <style>
                body {{ 
                    margin: 0; 
                    padding: 20px; 
                    background: #2c3e50; 
                    color: white;
                    font-family: monospace;
                }}
                .console {{ 
                    background: black; 
                    padding: 20px; 
                    border-radius: 5px;
                    border: 2px solid #34495e;
                }}
            </style>
        </head>
        <body>
            <h2>🖥️ Консоль ВМ: {vm_name}</h2>
            <div class="console">
                <p>🎭 Демо-консоль для виртуальной машины "{vm_name}"</p>
                <p>📺 В реальном режиме здесь будет VNC подключение</p>
                <p>⌨️  Консоль готова к использованию...</p>
                <p style="color: #2ecc71;">user@{vm_name}:~$ _</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    @router.get("/host/stats")
    async def get_host_stats():
        """Получить статистику хост-системы"""
        try:
            import psutil
            from datetime import datetime
            
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": dict(psutil.virtual_memory()._asdict()),
                "disk": dict(psutil.disk_usage('/')._asdict()),
                "network": dict(psutil.net_io_counters()._asdict()),
                "timestamp": datetime.now().isoformat(),
                "demo_mode": kvm_service.demo_mode
            }
            return stats
        except ImportError:
            # Fallback данные если psutil недоступен
            from datetime import datetime
            return {
                "cpu_percent": 25.5,
                "memory": {"total": 8589934592, "used": 4294967296, "percent": 50.0},
                "disk": {"total": 1000000000000, "used": 500000000000, "percent": 50.0},
                "network": {"bytes_sent": 1024000, "bytes_recv": 2048000},
                "timestamp": datetime.now().isoformat(),
                "demo_mode": True,
                "note": "Статистика недоступна - демо-данные (psutil не установлен)"
            }
        except Exception as e:
            from datetime import datetime
            return {
                "cpu_percent": 0.0,
                "memory": {"total": 0, "used": 0, "percent": 0.0},
                "disk": {"total": 0, "used": 0, "percent": 0.0},
                "network": {"bytes_sent": 0, "bytes_recv": 0},
                "timestamp": datetime.now().isoformat(),
                "demo_mode": True,
                "error": f"Ошибка получения статистики: {str(e)}"
            }

    @router.get("/")
    async def api_root():
        """API информация"""
        return {
            "name": "KVM Web Platform API",
            "version": "1.0.0",
            "demo_mode": kvm_service.demo_mode,
            "endpoints": {
                "vms": "/api/vms",
                "host_stats": "/api/host/stats",
                "iso": "/api/iso",
                "docs": "/docs"
            }
        }

    # ISO и образы ОС
    @router.get("/iso")
    async def list_iso():
        """Получить список доступных ISO образов"""
        try:
            from app.services.os_image_service import get_available_os_images, get_local_iso_files
            
            # Получаем каталог ОС
            os_catalog = get_available_os_images()
            
            # Получаем локальные ISO файлы
            local_isos = get_local_iso_files()
            
            return {
                "os_catalog": os_catalog,
                "local_files": local_isos,
                "total": len(os_catalog) + len(local_isos)
            }
        except Exception as e:
            return {"error": str(e), "os_catalog": [], "local_files": []}

    @router.get("/iso/scan")
    async def get_scan_info():
        """Получить информацию о сканировании ISO образов"""
        try:
            from app.services.os_image_service import scan_iso_directory
            
            result = scan_iso_directory()
            return {
                "success": True,
                "message": "Информация о ISO образах",
                "found": result["found"],
                "total_size": result["total_size"],
                "files": result.get("files", [])
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка получения информации: {str(e)}",
                "found": 0,
                "total_size": 0,
                "files": []
            }

    @router.post("/iso/scan")
    async def scan_iso():
        """Сканировать папку с ISO образами"""
        try:
            from app.services.os_image_service import scan_iso_directory
            
            result = scan_iso_directory()
            return {
                "success": True,
                "message": "Сканирование завершено",
                "found": result["found"],
                "total_size": result["total_size"]
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка сканирования: {str(e)}",
                "found": 0,
                "total_size": 0
            }

else:
    # Заглушка если FastAPI недоступен
    class MockRouter:
        def __init__(self):
            pass
    
    router = MockRouter()
