#!/usr/bin/env python3
"""
KVM Web Platform - Главный файл запуска
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    print("❌ FastAPI не установлен. Запустите: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False
    sys.exit(1)

from app.core.config import settings


def create_app() -> FastAPI:
    """Создание FastAPI приложения"""
    app = FastAPI(
        title="KVM Web Platform",
        description="Веб-платформа для управления KVM виртуальными машинами",
        version="1.0.0"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене указать конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files (для фронтенда)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Подключение API роутов
    try:
        from app.api.routes import router as api_router
        app.include_router(api_router, prefix="/api")
    except ImportError as e:
        print(f"⚠️  API роуты не загружены: {e}")

    @app.get("/")
    async def root():
        """Главная страница"""
        try:
            with open("static/index.html", "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        except FileNotFoundError:
            return {"message": "KVM Web Platform API", "version": "1.0.0"}

    @app.get("/health")
    async def health():
        """Проверка здоровья сервиса"""
        return {"status": "ok", "platform": "KVM Web Platform"}

    return app


def main():
    """Главная функция запуска"""
    print("🚀 Запуск KVM Web Platform...")
    print(f"🖥️  Платформа: {os.uname().sysname} {os.uname().machine}")
    
    print(f"🌐 Сервер будет запущен на http://{settings.HOST}:{settings.PORT}")
    print("📁 Статические файлы:", Path("static").absolute())
    print("💾 Данные:", settings.DATA_DIR)
    
    # Запуск сервера с import string для поддержки reload
    if settings.DEBUG:
        uvicorn.run(
            "main:create_app",  # Import string instead of app object
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            factory=True  # Indicates that create_app is a factory function
        )
    else:
        # В продакшене создаем приложение напрямую
        app = create_app()
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            reload=False
        )


if __name__ == "__main__":
    main()
