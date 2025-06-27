#!/usr/bin/env python3
"""
Простой тест KVM Web Platform
"""

import sys
import json
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

def test_kvm_service():
    """Тест KVM сервиса"""
    print("🧪 Тестирование KVM сервиса...")
    
    try:
        from app.services.kvm_service import KVMService
        
        # Создаем экземпляр сервиса
        kvm = KVMService()
        
        print(f"✅ KVM сервис создан (демо-режим: {kvm.demo_mode})")
        
        # Тестируем получение списка ВМ
        vms = kvm.get_all_vms()
        print(f"✅ Получен список ВМ: {len(vms)} шт.")
        
        for vm in vms:
            print(f"   📦 {vm['name']} - {vm['status']}")
        
        # Тестируем действия с ВМ
        if vms:
            vm_name = vms[0]["name"]
            print(f"\n🔧 Тестирование действий с ВМ '{vm_name}'...")
            
            # Тест запуска
            result = kvm.start_vm(vm_name)
            print(f"   ▶️  Запуск: {result['message']}")
            
            # Тест остановки
            result = kvm.stop_vm(vm_name)
            print(f"   ⏹️  Остановка: {result['message']}")
            
            # Тест перезагрузки
            result = kvm.restart_vm(vm_name)
            print(f"   🔄 Перезагрузка: {result['message']}")
        
        print("\n✅ Все тесты KVM сервиса прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования KVM сервиса: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n🧪 Тестирование конфигурации...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ Конфигурация загружена")
        print(f"   📂 Базовая директория: {settings.BASE_DIR}")
        print(f"   💾 Директория данных: {settings.DATA_DIR}")
        print(f"   💿 Директория ISO: {settings.ISO_STORAGE_PATH}")
        print(f"   🖥️  Директория ВМ: {settings.VM_STORAGE_PATH}")
        
        # Проверяем что директории созданы
        if Path(settings.DATA_DIR).exists():
            print("✅ Директории данных созданы")
        else:
            print("⚠️  Директории данных не найдены")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования конфигурации: {e}")
        return False

def test_demo_data():
    """Тест демо-данных"""
    print("\n🧪 Тестирование демо-данных...")
    
    try:
        demo_file = Path("data/demo_vms.json")
        if demo_file.exists():
            with open(demo_file, encoding="utf-8") as f:
                demo_vms = json.load(f)
            
            print(f"✅ Демо-данные загружены: {len(demo_vms)} ВМ")
            for vm in demo_vms:
                print(f"   📦 {vm['name']} - {vm['status']}")
        else:
            print("⚠️  Демо-данные не найдены")
        
        # Проверяем ISO файлы
        iso_dir = Path("data/images/iso")
        if iso_dir.exists():
            iso_files = list(iso_dir.glob("*.iso"))
            print(f"✅ ISO файлы: {len(iso_files)} шт.")
            for iso in iso_files:
                print(f"   💿 {iso.name}")
        else:
            print("⚠️  Директория ISO не найдена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования демо-данных: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов KVM Web Platform\n")
    
    tests = [
        test_config,
        test_demo_data,
        test_kvm_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Результат тестов: {passed}/{total} прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли! Платформа готова к работе.")
        print("\nДля запуска:")
        print("  python3 main.py")
        print("  или")
        print("  ./start.sh")
    else:
        print("❌ Некоторые тесты не прошли. Проверьте ошибки выше.")

if __name__ == "__main__":
    main()
