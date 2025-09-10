// Função para criar e exibir um toast dinamicamente
function showToast(message, category = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        const icons = {
            success: 'fa-check-circle',
            danger: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        const icon = icons[category] || 'fa-info-circle';

        const toastHTML = `
            <div class="toast align-items-center text-white bg-${category} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${icon} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        
        const toastFragment = document.createRange().createContextualFragment(toastHTML);
        // CORREÇÃO APLICADA AQUI: Usando .firstElementChild em vez de .firstChild
        const toastEl = toastFragment.firstElementChild; 
        
        if (toastEl) {
            toastContainer.appendChild(toastEl);
            const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
            toast.show();
            toastEl.addEventListener('hidden.bs.toast', function () {
                toastEl.remove();
            });
        }
    }
}

// Armazena os IDs das notificações que já foram exibidas como toast
let displayedNotificationIds = new Set();

function fetchNotifications() {
    fetch('/notifications/unread')
        .then(response => response.json())
        .then(data => {
            const countBadge = document.getElementById('notification-count');
            const notificationList = document.getElementById('notification-list');
            
            if (!countBadge || !notificationList) return;

            notificationList.innerHTML = '';

            if (data.count > 0) {
                countBadge.textContent = data.count;
                countBadge.style.display = 'inline';
                
                data.notifications.forEach(notif => {
                    if (!displayedNotificationIds.has(notif.id)) {
                        showToast(notif.message, 'info');
                        displayedNotificationIds.add(notif.id);
                    }

                    const listItem = document.createElement('li');
                    listItem.innerHTML = `<a class="dropdown-item" href="/ticket/${notif.ticket_id}">
                        <p class="mb-0 small">${notif.message}</p>
                        <small class="text-muted">${new Date(notif.timestamp).toLocaleString()}</small>
                    </a>`;
                    notificationList.appendChild(listItem);
                });

            } else {
                countBadge.style.display = 'none';
                notificationList.innerHTML = '<li><span class="dropdown-item-text text-muted">Nenhuma nova notificação</span></li>';
            }
        })
        .catch(error => console.error('Erro ao buscar notificações:', error));
}

function markNotificationsAsRead() {
    fetch('/notifications/mark-read', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const countBadge = document.getElementById('notification-count');
                if(countBadge) countBadge.style.display = 'none';
            }
        });
}


document.addEventListener('DOMContentLoaded', function() {
    // Inicializa e exibe toasts de mensagens "flashed" do Flask
    const toastElList = [].slice.call(document.querySelectorAll('.toast-container .toast'));
    toastElList.forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', function () {
            toastEl.remove();
        });
    });

    // Gráficos, Kanban, Modais, etc.
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusData = JSON.parse(statusCtx.dataset.chartdata);
        new Chart(statusCtx, { type: 'pie', data: { labels: statusData.map(d => d.status), datasets: [{ data: statusData.map(d => d.count), backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'] }] }, options: { responsive: true, plugins: { title: { display: true, text: 'Chamados por Status' } } } });
    }
    const sectorCtx = document.getElementById('sectorChart');
    if (sectorCtx) {
        const sectorData = JSON.parse(sectorCtx.dataset.chartdata);
        new Chart(sectorCtx, { type: 'bar', data: { labels: sectorData.map(d => d.sector), datasets: [{ label: 'Chamados por Setor', data: sectorData.map(d => d.count), backgroundColor: '#36A2EB' }] }, options: { responsive: true, scales: { y: { beginAtZero: true } }, plugins: { title: { display: true, text: 'Chamados por Setor de Destino' } } } });
    }
    const priorityCtx = document.getElementById('priorityChart');
    if (priorityCtx) {
        const priorityData = JSON.parse(priorityCtx.dataset.chartdata);
        new Chart(priorityCtx, { type: 'doughnut', data: { labels: priorityData.map(d => d.priority), datasets: [{ data: priorityData.map(d => d.count), backgroundColor: ['#FFCE56', '#36A2EB', '#FF6384'] }] }, options: { responsive: true, plugins: { title: { display: true, text: 'Chamados por Prioridade' } } } });
    }
    const kanbanContainer = document.querySelector('.kanban-container');
    if (kanbanContainer) {
        document.querySelectorAll('.kanban-column-body').forEach(column => {
            new Sortable(column, { group: 'kanban', animation: 150, ghostClass: 'sortable-ghost', dragClass: 'sortable-drag', onEnd: function (evt) {
                const ticketId = evt.item.dataset.ticketId;
                const newStatus = evt.to.dataset.status;
                const oldStatus = evt.from.dataset.status;
                if (newStatus !== oldStatus) {
                    fetch(`/update_ticket_status/${ticketId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ new_status: newStatus }) })
                        .then(response => { if (!response.ok) { return response.json().then(err => { throw new Error(err.message || 'Erro no servidor') }); } return response.json(); })
                        .then(data => { if (data.success) { showToast(data.message, 'success'); } else { evt.from.appendChild(evt.item); showToast(data.message, 'danger'); } })
                        .catch(error => { evt.from.appendChild(evt.item); showToast('Não foi possível atualizar o chamado. ' + error.message, 'danger'); });
                }
            }});
        });
    }
    var changePasswordModal = document.getElementById('changePasswordModal');
    if (changePasswordModal) {
        changePasswordModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');
            changePasswordModal.querySelector('#userNamePassword').textContent = userName;
            changePasswordModal.querySelector('#userIdPassword').value = userId;
        });
    }
    var deleteUserModal = document.getElementById('deleteUserModal');
    if (deleteUserModal) {
        deleteUserModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');
            deleteUserModal.querySelector('#userNameDelete').textContent = userName;
            deleteUserModal.querySelector('#deleteUserForm').action = '/delete_user/' + userId;
        });
    }
    const printButton = document.getElementById('printReport');
    if (printButton) {
        printButton.addEventListener('click', function() { window.print(); });
    }
    
    // Lógica do sino de notificações
    const notificationBell = document.getElementById('notificationBell');
    if (notificationBell) {
        notificationBell.addEventListener('show.bs.dropdown', markNotificationsAsRead);
        fetchNotifications(); // Busca ao carregar a página
        setInterval(fetchNotifications, 30000); // Busca a cada 30 segundos
    }
});