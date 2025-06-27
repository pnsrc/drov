// KVM Web Platform Frontend JavaScript

class KVMPlatform {
    constructor() {
        this.apiUrl = '/api';
        this.currentPage = 'dashboard';
        this.vms = [];
        this.availableISOs = [];
        this.downloadedISOs = [];
        this.osCatalog = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupForms();
        this.loadDashboard();
        this.startStatsUpdate();
    }

    setupForms() {
        // Форма создания ВМ
        const createVMForm = document.getElementById('create-vm-form');
        if (createVMForm) {
            createVMForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createVM();
            });
        }

        // Форма скачивания ISO
        const downloadISOForm = document.getElementById('download-iso-form');
        if (downloadISOForm) {
            downloadISOForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.downloadISO();
            });
        }
    }

    setupNavigation() {
        // Навигация по страницам
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('a').dataset.page;
                this.showPage(page);
            });
        });

        // Форма создания ВМ
        const createVMForm = document.getElementById('create-vm-form');
        if (createVMForm) {
            createVMForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createVM();
            });
        }
    }

    showPage(pageName) {
        // Скрыть все страницы
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
        });

        // Показать выбранную страницу
        const targetPage = document.getElementById(`${pageName}-page`);
        if (targetPage) {
            targetPage.style.display = 'block';
        }

        // Обновить активную ссылку в навигации
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');

        this.currentPage = pageName;

        // Загрузить данные для страницы
        switch (pageName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'vms':
                this.loadVMs();
                break;
            case 'create-vm':
                this.loadCreateVMData();
                break;
            case 'images':
                this.loadImagesData();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Загрузить статистику хоста
            await this.updateHostStats();
            
            // Загрузить активные ВМ
            await this.loadActiveVMs();
        } catch (error) {
            this.showError('Ошибка загрузки дашборда: ' + error.message);
        }
    }

    async updateHostStats() {
        try {
            const response = await fetch(`${this.apiUrl}/host/stats`);
            const stats = await response.json();

            // Обновить статистику
            document.getElementById('cpu-usage').textContent = `${stats.cpu_percent.toFixed(1)}%`;
            
            const memoryPercent = (stats.memory.used / stats.memory.total * 100).toFixed(1);
            document.getElementById('memory-usage').textContent = `${memoryPercent}%`;
            
            const diskPercent = (stats.disk.used / stats.disk.total * 100).toFixed(1);
            document.getElementById('disk-usage').textContent = `${diskPercent}%`;

        } catch (error) {
            console.error('Ошибка обновления статистики:', error);
        }
    }

    async loadActiveVMs() {
        try {
            const response = await fetch(`${this.apiUrl}/vms`);
            const vms = await response.json();
            
            this.vms = vms;
            
            // Обновить счетчик ВМ
            document.getElementById('total-vms').textContent = vms.length;
            
            // Показать активные ВМ
            const activeVMs = vms.filter(vm => vm.is_active);
            const container = document.getElementById('active-vms-list');
            
            container.innerHTML = '';
            
            if (activeVMs.length === 0) {
                container.innerHTML = '<div class="col-12"><p class="text-muted">Нет активных виртуальных машин</p></div>';
                return;
            }

            activeVMs.forEach(vm => {
                const vmCard = this.createVMCard(vm, true);
                container.appendChild(vmCard);
            });

        } catch (error) {
            this.showError('Ошибка загрузки ВМ: ' + error.message);
        }
    }

    async loadVMs() {
        try {
            const response = await fetch(`${this.apiUrl}/vms`);
            const vms = await response.json();
            
            this.vms = vms;
            
            const tbody = document.getElementById('vms-table');
            tbody.innerHTML = '';

            vms.forEach(vm => {
                const row = this.createVMTableRow(vm);
                tbody.appendChild(row);
            });

        } catch (error) {
            this.showError('Ошибка загрузки ВМ: ' + error.message);
        }
    }

    createVMCard(vm, compact = false) {
        const div = document.createElement('div');
        div.className = compact ? 'col-md-4 mb-3' : 'col-md-6 mb-3';
        
        const statusClass = vm.is_active ? 'status-running' : 'status-stopped';
        const statusIcon = vm.is_active ? 'fa-play-circle' : 'fa-stop-circle';
        const statusText = vm.is_active ? 'Запущена' : 'Остановлена';
        
        const memoryMB = Math.round(vm.memory.max / 1024 / 1024);
        
        div.innerHTML = `
            <div class="card vm-card h-100">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-desktop"></i> ${vm.name}
                    </h6>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="fas ${statusIcon} ${statusClass}"></i> ${statusText}<br>
                            <i class="fas fa-memory"></i> ${memoryMB} МБ | 
                            <i class="fas fa-microchip"></i> ${vm.vcpus} vCPU
                        </small>
                    </p>
                    <div class="vm-actions d-flex">
                        ${this.createVMActionButtons(vm)}
                    </div>
                </div>
            </div>
        `;
        
        return div;
    }

    createVMTableRow(vm) {
        const tr = document.createElement('tr');
        
        const statusClass = vm.is_active ? 'status-running' : 'status-stopped';
        const statusIcon = vm.is_active ? 'fa-play-circle' : 'fa-stop-circle';
        const statusText = vm.is_active ? 'Запущена' : 'Остановлена';
        
        const memoryMB = Math.round(vm.memory.max / 1024 / 1024);
        
        tr.innerHTML = `
            <td>
                <i class="fas fa-desktop"></i> ${vm.name}
                <small class="d-block text-muted">${vm.uuid}</small>
            </td>
            <td>
                <i class="fas ${statusIcon} ${statusClass}"></i> ${statusText}
            </td>
            <td>${memoryMB} МБ</td>
            <td>${vm.vcpus}</td>
            <td>
                <div class="vm-actions d-flex">
                    ${this.createVMActionButtons(vm)}
                </div>
            </td>
        `;
        
        return tr;
    }

    createVMActionButtons(vm) {
        let buttons = '';
        
        if (vm.is_active) {
            buttons += `
                <button class="btn btn-sm btn-outline-primary" onclick="kvmPlatform.openConsole('${vm.name}')" title="Консоль">
                    <i class="fas fa-terminal"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="kvmPlatform.stopVM('${vm.name}')" title="Остановить">
                    <i class="fas fa-stop"></i>
                </button>
                <button class="btn btn-sm btn-outline-info" onclick="kvmPlatform.restartVM('${vm.name}')" title="Перезагрузить">
                    <i class="fas fa-redo"></i>
                </button>
            `;
        } else {
            buttons += `
                <button class="btn btn-sm btn-outline-success" onclick="kvmPlatform.startVM('${vm.name}')" title="Запустить">
                    <i class="fas fa-play"></i>
                </button>
            `;
        }
        
        buttons += `
            <button class="btn btn-sm btn-outline-danger" onclick="kvmPlatform.deleteVM('${vm.name}')" title="Удалить">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        return buttons;
    }

    async startVM(vmName) {
        try {
            const response = await fetch(`${this.apiUrl}/vms/${vmName}/start`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess(`ВМ '${vmName}' запущена`);
                this.refreshCurrentPage();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка запуска ВМ: ' + error.message);
        }
    }

    async stopVM(vmName) {
        if (!confirm(`Остановить ВМ '${vmName}'?`)) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/vms/${vmName}/stop`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess(`ВМ '${vmName}' остановлена`);
                this.refreshCurrentPage();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка остановки ВМ: ' + error.message);
        }
    }

    async restartVM(vmName) {
        if (!confirm(`Перезагрузить ВМ '${vmName}'?`)) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/vms/${vmName}/restart`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess(`ВМ '${vmName}' перезагружена`);
                this.refreshCurrentPage();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка перезагрузки ВМ: ' + error.message);
        }
    }

    async deleteVM(vmName) {
        if (!confirm(`Удалить ВМ '${vmName}'? Это действие нельзя отменить!`)) return;
        
        const deleteDisk = confirm('Также удалить диски ВМ?');
        
        try {
            const response = await fetch(`${this.apiUrl}/vms/${vmName}?delete_disks=${deleteDisk}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showSuccess(`ВМ '${vmName}' удалена`);
                this.refreshCurrentPage();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка удаления ВМ: ' + error.message);
        }
    }

    openConsole(vmName) {
        const modal = new bootstrap.Modal(document.getElementById('consoleModal'));
        document.getElementById('console-vm-name').textContent = vmName;
        document.getElementById('console-frame').src = `/api/vms/${vmName}/console/viewer`;
        modal.show();
    }

    async loadCreateVMData() {
        try {
            // Загрузить доступные ISO образы
            await this.loadAvailableISOs();
            this.populateISOSelect();
        } catch (error) {
            console.error('Ошибка загрузки данных для создания ВМ:', error);
        }
    }

    async loadAvailableISOs() {
        try {
            const response = await fetch(`${this.apiUrl}/iso/scan`);
            const data = await response.json();
            this.availableISOs = data.available_isos || [];
        } catch (error) {
            console.error('Ошибка загрузки ISO образов:', error);
            this.availableISOs = [];
        }
    }

    populateISOSelect() {
        const select = document.getElementById('vm-iso');
        if (!select) return;

        // Очистить текущие опции (кроме первой)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }

        // Добавить доступные ISO
        this.availableISOs.forEach(iso => {
            const option = document.createElement('option');
            option.value = iso.path;
            option.textContent = `${iso.name} (${this.formatFileSize(iso.size)})`;
            select.appendChild(option);
        });
    }

    async loadImagesData() {
        try {
            // Загрузить каталог ОС
            await this.loadOSCatalog();
            
            // Загрузить скачанные ISO
            await this.loadDownloadedISOs();
            
            // Отобразить данные
            this.displayOSCatalog();
            this.displayDownloadedISOs();
        } catch (error) {
            this.showError('Ошибка загрузки данных ISO: ' + error.message);
        }
    }

    async loadOSCatalog() {
        try {
            const response = await fetch(`${this.apiUrl}/iso/catalog`);
            const data = await response.json();
            this.osCatalog = data.catalog || [];
        } catch (error) {
            console.error('Ошибка загрузки каталога ОС:', error);
            this.osCatalog = [];
        }
    }

    async loadDownloadedISOs() {
        try {
            const response = await fetch(`${this.apiUrl}/iso/scan`);
            const data = await response.json();
            this.downloadedISOs = data.available_isos || [];
        } catch (error) {
            console.error('Ошибка загрузки скачанных ISO:', error);
            this.downloadedISOs = [];
        }
    }

    displayOSCatalog() {
        const container = document.getElementById('os-catalog-list');
        if (!container) return;

        container.innerHTML = '';

        if (this.osCatalog.length === 0) {
            container.innerHTML = '<div class="col-12"><p class="text-muted">Каталог ОС недоступен</p></div>';
            return;
        }

        this.osCatalog.forEach(os => {
            const div = document.createElement('div');
            div.className = 'col-md-4 mb-3';
            
            const isDownloaded = this.downloadedISOs.some(iso => 
                iso.name.toLowerCase().includes(os.name.toLowerCase()) ||
                iso.path.includes(os.filename)
            );

            div.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fab fa-${this.getOSIcon(os.name)}"></i> ${os.name}
                        </h6>
                        <p class="card-text">
                            <small class="text-muted">
                                ${os.description}<br>
                                Размер: ${this.formatFileSize(os.size)}
                            </small>
                        </p>
                        <div class="mt-auto">
                            ${isDownloaded ? 
                                '<span class="badge bg-success"><i class="fas fa-check"></i> Скачан</span>' :
                                `<button class="btn btn-sm btn-primary" onclick="kvmPlatform.downloadOSFromCatalog('${os.url}', '${os.filename}')">
                                    <i class="fas fa-download"></i> Скачать
                                </button>`
                            }
                        </div>
                    </div>
                </div>
            `;
            
            container.appendChild(div);
        });
    }

    displayDownloadedISOs() {
        const tbody = document.getElementById('downloaded-isos-table');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.downloadedISOs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Нет скачанных ISO образов</td></tr>';
            return;
        }

        this.downloadedISOs.forEach(iso => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <i class="fas fa-compact-disc"></i> ${iso.name}
                    <small class="d-block text-muted">${iso.path}</small>
                </td>
                <td>${this.formatFileSize(iso.size)}</td>
                <td>${new Date(iso.modified).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="kvmPlatform.deleteISO('${iso.path}')" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    getOSIcon(osName) {
        const name = osName.toLowerCase();
        if (name.includes('ubuntu')) return 'ubuntu';
        if (name.includes('debian')) return 'debian';
        if (name.includes('centos') || name.includes('rhel') || name.includes('fedora')) return 'redhat';
        if (name.includes('windows')) return 'windows';
        if (name.includes('arch')) return 'arch-linux';
        return 'linux';
    }

    async scanISOs() {
        try {
            const response = await fetch(`${this.apiUrl}/iso/scan`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('Сканирование ISO завершено');
                await this.loadImagesData();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка сканирования ISO: ' + error.message);
        }
    }

    showDownloadModal() {
        const modal = new bootstrap.Modal(document.getElementById('downloadModal'));
        modal.show();
    }

    async downloadISO() {
        const url = document.getElementById('download-url').value;
        const filename = document.getElementById('download-filename').value;
        
        if (!url) {
            this.showError('Введите URL для скачивания');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/iso/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    filename: filename || null
                })
            });

            if (response.ok) {
                this.showSuccess('Загрузка ISO начата');
                bootstrap.Modal.getInstance(document.getElementById('downloadModal')).hide();
                document.getElementById('download-iso-form').reset();
                
                // Обновить данные через некоторое время
                setTimeout(() => this.loadImagesData(), 2000);
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка скачивания ISO: ' + error.message);
        }
    }

    async downloadOSFromCatalog(url, filename) {
        try {
            const response = await fetch(`${this.apiUrl}/iso/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    filename: filename
                })
            });

            if (response.ok) {
                this.showSuccess(`Загрузка ${filename} начата`);
                
                // Обновить отображение
                setTimeout(() => this.loadImagesData(), 2000);
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка скачивания ISO: ' + error.message);
        }
    }

    async deleteISO(isoPath) {
        if (!confirm('Удалить ISO образ? Это действие нельзя отменить!')) return;

        try {
            const response = await fetch(`${this.apiUrl}/iso/delete`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    iso_path: isoPath
                })
            });

            if (response.ok) {
                this.showSuccess('ISO образ удален');
                await this.loadImagesData();
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка удаления ISO: ' + error.message);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async createVM() {
        const formData = {
            name: document.getElementById('vm-name').value,
            memory: parseInt(document.getElementById('vm-memory').value),
            vcpus: parseInt(document.getElementById('vm-vcpus').value),
            disk_size: parseInt(document.getElementById('vm-disk-size').value),
            iso_path: document.getElementById('vm-iso').value || null,
            network: document.getElementById('vm-network').value
        };

        try {
            const response = await fetch(`${this.apiUrl}/vms`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showSuccess(`ВМ '${formData.name}' создана`);
                document.getElementById('create-vm-form').reset();
                this.showPage('vms');
            } else {
                const error = await response.json();
                this.showError(error.detail);
            }
        } catch (error) {
            this.showError('Ошибка создания ВМ: ' + error.message);
        }
    }

    refreshCurrentPage() {
        this.showPage(this.currentPage);
    }

    startStatsUpdate() {
        // Обновляем статистику каждые 5 секунд
        if (this.currentPage === 'dashboard') {
            this.updateHostStats();
        }
        
        setTimeout(() => this.startStatsUpdate(), 5000);
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Автоматически скрыть через 5 секунд
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
}

// Инициализация приложения
const kvmPlatform = new KVMPlatform();
