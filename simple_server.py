#!/usr/bin/env python3
"""
Простой HTTP сервер для демонстрации KVM Web Platform
Работает без внешних зависимостей
"""

import sys
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

from app.services.kvm_service import kvm_service
from app.core.config import settings


class KVMWebHandler(SimpleHTTPRequestHandler):
    """Обработчик HTTP запросов для KVM Web Platform"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="static", **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        print(f"📨 GET {path}")
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_get(path)
        elif path == '/':
            # Главная страница
            self.serve_index()
        else:
            # Статические файлы
            super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        print(f"📨 POST {path}")
        
        if path.startswith('/api/'):
            self.handle_api_post(path)
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_DELETE(self):
        """Обработка DELETE запросов"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        print(f"📨 DELETE {path}")
        
        if path.startswith('/api/'):
            self.handle_api_delete(path)
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_api_get(self, path):
        """Обработка GET API запросов"""
        try:
            if path == '/api/vms':
                # Список ВМ
                vms = kvm_service.get_all_vms()
                self.send_json_response(vms)
            
            elif path.startswith('/api/vms/') and path.endswith('/console/viewer'):
                # VNC консоль
                vm_name = path.split('/')[3]
                html_content = self.get_console_html(vm_name)
                self.send_html_response(html_content)
            
            elif path.startswith('/api/vms/') and not '/' in path[10:]:
                # Информация о конкретной ВМ
                vm_name = path.split('/')[3]
                vm = kvm_service.get_vm_info(vm_name)
                if vm:
                    self.send_json_response(vm)
                else:
                    self.send_error(404, "VM not found")
            
            elif path == '/api/host/stats':
                # Статистика хоста
                stats = self.get_host_stats()
                self.send_json_response(stats)
            
            elif path == '/api/':
                # API информация
                info = {
                    "name": "KVM Web Platform API",
                    "version": "1.0.0",
                    "demo_mode": kvm_service.demo_mode,
                    "endpoints": {
                        "vms": "/api/vms",
                        "host_stats": "/api/host/stats"
                    }
                }
                self.send_json_response(info)
            
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_api_post(self, path):
        """Обработка POST API запросов"""
        try:
            if '/start' in path:
                vm_name = path.split('/')[3]
                result = kvm_service.start_vm(vm_name)
                self.send_json_response(result)
            
            elif '/stop' in path:
                vm_name = path.split('/')[3]
                result = kvm_service.stop_vm(vm_name)
                self.send_json_response(result)
            
            elif '/restart' in path:
                vm_name = path.split('/')[3]
                result = kvm_service.restart_vm(vm_name)
                self.send_json_response(result)
            
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_api_delete(self, path):
        """Обработка DELETE API запросов"""
        try:
            if path.startswith('/api/vms/'):
                vm_name = path.split('/')[3]
                result = kvm_service.delete_vm(vm_name)
                self.send_json_response(result)
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        """Отправка JSON ответа"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_html_response(self, html):
        """Отправка HTML ответа"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_index(self):
        """Отправка главной страницы"""
        try:
            with open('static/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_html_response(content)
        except FileNotFoundError:
            error_html = """
            <html>
            <head><title>KVM Web Platform</title></head>
            <body>
                <h1>🚀 KVM Web Platform</h1>
                <p>Файл static/index.html не найден</p>
                <p><a href="/api/">API Documentation</a></p>
            </body>
            </html>
            """
            self.send_html_response(error_html)
    
    def get_console_html(self, vm_name):
        """Генерация HTML для консоли ВМ"""
        return f"""
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
                    font-family: 'Courier New', monospace;
                }}
                .console {{ 
                    background: black; 
                    padding: 20px; 
                    border-radius: 5px;
                    border: 2px solid #34495e;
                    min-height: 400px;
                }}
                .status {{
                    background: #34495e;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="status">
                <h2>🖥️ Консоль ВМ: {vm_name}</h2>
                <p>📺 Демо-консоль для виртуальной машины</p>
            </div>
            
            <div class="console">
                <p style="color: #2ecc71;">KVM Web Platform - Демо консоль</p>
                <p style="color: #3498db;">Подключение к виртуальной машине: {vm_name}</p>
                <p style="color: #e74c3c;">⚠️  В реальном режиме здесь будет VNC подключение</p>
                <br>
                <p style="color: #f39c12;">Ubuntu 22.04.3 LTS {vm_name} tty1</p>
                <br>
                <p style="color: #2ecc71;">{vm_name} login: <span style="animation: blink 1s infinite;">_</span></p>
            </div>
            
            <style>
                @keyframes blink {{
                    0%, 50% {{ opacity: 1; }}
                    51%, 100% {{ opacity: 0; }}
                }}
            </style>
        </body>
        </html>
        """
    
    def get_host_stats(self):
        """Получение статистики хоста"""
        try:
            import psutil
            from datetime import datetime
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": dict(psutil.virtual_memory()._asdict()),
                "disk": dict(psutil.disk_usage('/')._asdict()),
                "network": dict(psutil.net_io_counters()._asdict()),
                "timestamp": datetime.now().isoformat(),
                "demo_mode": kvm_service.demo_mode
            }
        except ImportError:
            from datetime import datetime
            # Fallback данные если psutil недоступен
            return {
                "cpu_percent": 25.5,
                "memory": {"total": 8589934592, "used": 4294967296, "percent": 50.0},
                "disk": {"total": 1000000000000, "used": 500000000000, "percent": 50.0},
                "network": {"bytes_sent": 1024000, "bytes_recv": 2048000},
                "timestamp": datetime.now().isoformat(),
                "demo_mode": True,
                "note": "Статистика недоступна - демо-данные"
            }
    
    def do_OPTIONS(self):
        """Обработка OPTIONS запросов для CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def main():
    """Главная функция запуска"""
    print("🚀 Запуск KVM Web Platform (простой HTTP сервер)")
    print(f"🖥️  Платформа: {os.uname().sysname} {os.uname().machine}")
    print(f"🎭 Демо-режим: {kvm_service.demo_mode}")
    print(f"📁 Данные: {settings.DATA_DIR}")
    
    # Порт и хост
    host = "localhost"
    port = 8000
    
    # Создаем сервер
    server = HTTPServer((host, port), KVMWebHandler)
    
    print(f"\n🌐 Сервер запущен на http://{host}:{port}")
    print("📖 API доступно по адресу: http://localhost:8000/api/")
    print("🔧 Управление ВМ: http://localhost:8000/")
    
    # Открываем браузер через 2 секунды
    def open_browser():
        import time
        time.sleep(2)
        try:
            webbrowser.open(f"http://{host}:{port}")
            print("🌍 Браузер открыт автоматически")
        except:
            print("⚠️  Не удалось открыть браузер автоматически")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        print("\n🔥 Сервер работает... Нажмите Ctrl+C для остановки")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        server.shutdown()
        print("✅ Сервер остановлен")


if __name__ == "__main__":
    main()
