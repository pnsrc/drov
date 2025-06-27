import platform
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Условный импорт libvirt только для Linux
try:
    import libvirt  # type: ignore
    import xml.etree.ElementTree as ET
    LIBVIRT_AVAILABLE = True
except ImportError:
    LIBVIRT_AVAILABLE = False
    libvirt = None  # type: ignore

from app.core.config import settings


class KVMService:
    """Сервис для работы с KVM через libvirt или в демо-режиме"""
    
    def __init__(self):
        self.conn = None
        self.demo_mode = not LIBVIRT_AVAILABLE or platform.system() != "Linux"
        
        if not self.demo_mode:
            self.connect()
        else:
            print("🎭 Запуск в демо-режиме (libvirt недоступен)")
    
    def connect(self):
        """Подключение к libvirt"""
        if self.demo_mode:
            return
            
        try:
            self.conn = libvirt.open(settings.LIBVIRT_URI)
            if self.conn is None:
                raise Exception("Не удалось подключиться к libvirt")
        except Exception as e:
            print(f"⚠️  Переключение в демо-режим: {e}")
            self.demo_mode = True

    def get_all_vms(self) -> List[Dict]:
        """Получить список всех ВМ"""
        if self.demo_mode:
            return self._get_demo_vms()
            
        try:
            vms = []
            # Запущенные домены
            for vm_id in self.conn.listDomainsID():
                domain = self.conn.lookupByID(vm_id)
                vms.append(self._domain_to_dict(domain))
            
            # Остановленные домены
            for vm_name in self.conn.listDefinedDomains():
                domain = self.conn.lookupByName(vm_name)
                vms.append(self._domain_to_dict(domain))
            
            return vms
        except Exception as e:
            return []

    def get_vm_info(self, vm_name: str) -> Optional[Dict]:
        """Получить информацию о ВМ"""
        if self.demo_mode:
            vms = self._get_demo_vms()
            for vm in vms:
                if vm["name"] == vm_name:
                    return vm
            return None
            
        try:
            domain = self.conn.lookupByName(vm_name)
            return self._domain_to_dict(domain)
        except Exception as e:
            return None

    def start_vm(self, vm_name: str) -> Dict:
        """Запустить ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_name, "start")
            
        try:
            domain = self.conn.lookupByName(vm_name)
            if domain.isActive():
                return {"success": False, "message": "ВМ уже запущена"}
            
            domain.create()
            return {"success": True, "message": f"ВМ {vm_name} запущена"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка запуска ВМ: {e}"}

    def stop_vm(self, vm_name: str) -> Dict:
        """Остановить ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_name, "stop")
            
        try:
            domain = self.conn.lookupByName(vm_name)
            if not domain.isActive():
                return {"success": False, "message": "ВМ уже остановлена"}
            
            domain.shutdown()
            return {"success": True, "message": f"ВМ {vm_name} остановлена"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка остановки ВМ: {e}"}

    def force_stop_vm(self, vm_name: str) -> Dict:
        """Принудительно остановить ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_name, "force_stop")
            
        try:
            domain = self.conn.lookupByName(vm_name)
            domain.destroy()
            return {"success": True, "message": f"ВМ {vm_name} принудительно остановлена"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка принудительной остановки ВМ: {e}"}

    def restart_vm(self, vm_name: str) -> Dict:
        """Перезагрузить ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_name, "restart")
            
        try:
            domain = self.conn.lookupByName(vm_name)
            domain.reboot()
            return {"success": True, "message": f"ВМ {vm_name} перезагружена"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка перезагрузки ВМ: {e}"}

    def delete_vm(self, vm_name: str) -> Dict:
        """Удалить ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_name, "delete")
            
        try:
            domain = self.conn.lookupByName(vm_name)
            
            if domain.isActive():
                domain.destroy()
            
            # Получаем пути к дискам для удаления
            xml_desc = domain.XMLDesc(0)
            root = ET.fromstring(xml_desc)
            
            disks = []
            for disk in root.findall(".//devices/disk[@type='file']"):
                source = disk.find("source")
                if source is not None and "file" in source.attrib:
                    disks.append(source.attrib["file"])
            
            # Удаляем домен
            domain.undefine()
            
            # Удаляем диски
            for disk_path in disks:
                try:
                    Path(disk_path).unlink()
                except:
                    pass
            
            return {"success": True, "message": f"ВМ {vm_name} удалена"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка удаления ВМ: {e}"}

    def create_vm(self, vm_config: Dict) -> Dict:
        """Создать новую ВМ"""
        if self.demo_mode:
            return self._demo_vm_action(vm_config.get("name", "demo-vm"), "create")
        
        try:
            # Проверяем обязательные параметры
            required_fields = ['name', 'memory', 'vcpus', 'disk_size']
            for field in required_fields:
                if field not in vm_config:
                    return {"success": False, "message": f"Отсутствует обязательное поле: {field}"}
            
            vm_name = vm_config['name']
            
            # Проверяем, что ВМ с таким именем не существует
            try:
                existing = self.conn.lookupByName(vm_name)
                return {"success": False, "message": f"ВМ с именем '{vm_name}' уже существует"}
            except libvirt.libvirtError:
                pass  # ВМ не существует, это хорошо
            
            # Создаем диск для ВМ
            disk_path = Path(settings.VM_STORAGE_PATH) / f"{vm_name}.qcow2"
            disk_size = vm_config['disk_size']
            
            # Создаем qcow2 диск
            create_disk_cmd = f"qemu-img create -f qcow2 {disk_path} {disk_size}G"
            import subprocess
            result = subprocess.run(create_disk_cmd.split(), capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "message": f"Ошибка создания диска: {result.stderr}"}
            
            # Генерируем XML конфигурацию
            xml_config = self._generate_vm_xml_with_iso(vm_config, str(disk_path))
            
            # Создаем домен в libvirt
            domain = self.conn.defineXML(xml_config)
            
            return {
                "success": True, 
                "message": f"ВМ '{vm_name}' создана успешно",
                "vm_name": vm_name,
                "disk_path": str(disk_path)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Ошибка создания ВМ: {str(e)}"}
    
    def _generate_vm_xml_with_iso(self, config: Dict, disk_path: str) -> str:
        """Генерация полной XML конфигурации для ВМ с ISO"""
        vm_name = config['name']
        memory_mb = config['memory']
        vcpus = config['vcpus']
        iso_path = config.get('iso_path', '')
        
        # Определяем архитектуру
        arch = "x86_64"
        machine = "pc-i440fx-2.12" if platform.machine() == "x86_64" else "q35"
        
        # Базовая XML конфигурация
        xml = f"""<domain type='kvm'>
  <name>{vm_name}</name>
  <uuid>{self._generate_uuid()}</uuid>
  <memory unit='MiB'>{memory_mb}</memory>
  <currentMemory unit='MiB'>{memory_mb}</currentMemory>
  <vcpu placement='static'>{vcpus}</vcpu>
  <os>
    <type arch='{arch}' machine='{machine}'>hvm</type>
    <boot dev='cdrom'/>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <cpu mode='host-passthrough' check='none'/>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    
    <!-- Главный диск -->
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk_path}'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </disk>"""
        
        # Добавляем CD-ROM с ISO если указан
        if iso_path and Path(iso_path).exists():
            xml += f"""
    
    <!-- CD-ROM с ISO образом -->
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='{iso_path}'/>
      <target dev='hdb' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='1'/>
    </disk>"""
        
        xml += f"""
    
    <!-- IDE контроллер для CD-ROM -->
    <controller type='ide' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    
    <!-- PCI контроллеры -->
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </controller>
    
    <!-- Сетевой интерфейс -->
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    
    <!-- VNC консоль -->
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    
    <!-- Видеокарта -->
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    
    <!-- Клавиатура и мышь -->
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    
    <!-- USB контроллер -->
    <controller type='usb' index='0' model='ich9-ehci1'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x7'/>
    </controller>
    
    <!-- Консольный порт для отладки -->
    <serial type='pty'>
      <target type='isa-serial' port='0'>
        <model name='isa-serial'/>
      </target>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    
    <!-- Канал для QEMU guest agent -->
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    
  </devices>
</domain>"""
        
        return xml
    
    def _generate_uuid(self) -> str:
        """Генерация UUID для ВМ"""
        import uuid
        return str(uuid.uuid4())

    def _domain_to_dict(self, domain) -> Dict:
        """Преобразовать libvirt домен в словарь"""
        if not LIBVIRT_AVAILABLE:
            return {}
            
        try:
            info = domain.info()
            return {
                "id": domain.ID() if domain.isActive() else None,
                "name": domain.name(),
                "status": "running" if domain.isActive() else "stopped",
                "memory": info[1],  # maxMemory в KB
                "vcpus": info[3],   # число CPU
                "cpu_time": info[4],  # CPU время
                "state": info[0]    # состояние домена
            }
        except Exception:
            return {}

    def _generate_vm_xml(self, config: Dict) -> str:
        """Генерация XML конфигурации для ВМ"""
        # Упрощенная XML конфигурация
        return f'''
        <domain type='kvm'>
            <name>{config["name"]}</name>
            <memory unit='MB'>{config.get("memory", 1024)}</memory>
            <vcpu>{config.get("vcpus", 1)}</vcpu>
            <os>
                <type arch='x86_64' machine='pc'>hvm</type>
                <boot dev='hd'/>
            </os>
        </domain>
        '''

    # Демо-методы для работы без libvirt
    def _get_demo_vms(self) -> List[Dict]:
        """Получить демо-список ВМ"""
        demo_file = Path("data/demo_vms.json")
        if demo_file.exists():
            try:
                with open(demo_file, encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # Базовые демо-данные если файл не найден
        return [
            {
                "id": "demo-vm-1",
                "name": "Ubuntu-Demo",
                "status": "running",
                "memory": 2048,
                "vcpus": 2,
                "disk_size": "20G",
                "ip_address": "192.168.122.100",
                "os": "Ubuntu 22.04 (демо)",
                "created": datetime.now().isoformat(),
                "uptime": "Demo mode"
            },
            {
                "id": "demo-vm-2", 
                "name": "CentOS-Demo",
                "status": "stopped",
                "memory": 1024,
                "vcpus": 1,
                "disk_size": "15G",
                "ip_address": "192.168.122.101",
                "os": "CentOS Stream 9 (демо)",
                "created": datetime.now().isoformat(),
                "uptime": "0"
            }
        ]
    
    def _demo_vm_action(self, vm_name: str, action: str) -> Dict:
        """Эмуляция действий с ВМ в демо-режиме"""
        return {
            "success": True,
            "message": f"Демо: {action} для ВМ {vm_name} выполнено успешно",
            "vm_name": vm_name,
            "action": action,
            "demo_mode": True
        }


# Создаем глобальный экземпляр сервиса
kvm_service = KVMService()
