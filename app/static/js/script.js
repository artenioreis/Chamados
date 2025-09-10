document.addEventListener('DOMContentLoaded', function() {
    // --- LÓGICA DOS GRÁFICOS (DASHBOARD) ---
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusData = JSON.parse(statusCtx.dataset.chartdata);
        new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: statusData.map(d => d.status),
                datasets: [{
                    data: statusData.map(d => d.count),
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Chamados por Status' } } }
        });
    }

    const sectorCtx = document.getElementById('sectorChart');
    if (sectorCtx) {
        const sectorData = JSON.parse(sectorCtx.dataset.chartdata);
        new Chart(sectorCtx, {
            type: 'bar',
            data: {
                labels: sectorData.map(d => d.sector),
                datasets: [{
                    label: 'Chamados por Setor',
                    data: sectorData.map(d => d.count),
                    backgroundColor: '#36A2EB'
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } }, plugins: { title: { display: true, text: 'Chamados por Setor de Destino' } } }
        });
    }

    const priorityCtx = document.getElementById('priorityChart');
    if (priorityCtx) {
        const priorityData = JSON.parse(priorityCtx.dataset.chartdata);
        new Chart(priorityCtx, {
            type: 'doughnut',
            data: {
                labels: priorityData.map(d => d.priority),
                datasets: [{
                    data: priorityData.map(d => d.count),
                    backgroundColor: ['#FFCE56', '#36A2EB', '#FF6384']
                }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Chamados por Prioridade' } } }
        });
    }

    // --- LÓGICA DO KANBAN DRAG-AND-DROP ---
    const kanbanContainer = document.querySelector('.kanban-container');
    if (kanbanContainer) {
        const kanbanColumns = document.querySelectorAll('.kanban-column-body');
        kanbanColumns.forEach(column => {
            new Sortable(column, {
                group: 'kanban',
                animation: 150,
                ghostClass: 'sortable-ghost',
                dragClass: 'sortable-drag',
                onEnd: function (evt) {
                    const itemEl = evt.item;
                    const toColumn = evt.to;
                    const fromColumn = evt.from;
                    const ticketId = itemEl.dataset.ticketId;
                    const newStatus = toColumn.dataset.status;
                    const oldStatus = fromColumn.dataset.status;

                    if (newStatus !== oldStatus) {
                        fetch(`/update_ticket_status/${ticketId}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ new_status: newStatus })
                        })
                        .then(response => {
                            if (!response.ok) {
                                return response.json().then(err => { throw new Error(err.message || 'Erro no servidor') });
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (!data.success) {
                                fromColumn.appendChild(itemEl); 
                                alert('Erro ao atualizar o chamado: ' + data.message);
                            }
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                            fromColumn.appendChild(itemEl);
                            alert('Não foi possível atualizar o chamado. ' + error.message);
                        });
                    }
                }
            });
        });
    }

    // --- LÓGICA DOS MODAIS DE GERENCIAMENTO ---
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

    // --- LÓGICA PARA NOTIFICAÇÕES DE ATUALIZAÇÃO ---
    if (document.getElementById('navbarDropdown')) {
        const updateToastEl = document.getElementById('updateToast');
        if (!updateToastEl) return; 

        const updateToast = new bootstrap.Toast(updateToastEl, { delay: 10000 });
        const toastMessageEl = document.getElementById('toast-message');
        const toastLinkEl = document.getElementById('toast-link');
        const notificationSound = document.getElementById('notification-sound');

        // Preferência de Som
        const toggleSoundBtn = document.getElementById('toggle-sound');
        const soundIconOn = document.getElementById('sound-icon-on');
        const soundIconOff = document.getElementById('sound-icon-off');
        const soundText = document.getElementById('sound-text');
        
        let soundEnabled = localStorage.getItem('notificationSoundEnabled') !== 'false';

        function updateSoundButtonUI() {
            if (soundEnabled) {
                soundIconOn.style.display = 'inline-block';
                soundIconOff.style.display = 'none';
                soundText.textContent = 'Desativar Som';
            } else {
                soundIconOn.style.display = 'none';
                soundIconOff.style.display = 'inline-block';
                soundText.textContent = 'Ativar Som';
            }
        }

        if (toggleSoundBtn) {
            toggleSoundBtn.addEventListener('click', function(e) {
                e.preventDefault();
                soundEnabled = !soundEnabled;
                localStorage.setItem('notificationSoundEnabled', soundEnabled);
                updateSoundButtonUI();
            });
        }

        // Verificação de Atualizações
        function checkForUpdates() {
            fetch('/check_updates')
                .then(response => response.ok ? response.json() : Promise.reject('A resposta da rede não foi OK'))
                .then(data => {
                    if (data.updates && data.updates.length > 0) {
                        data.updates.forEach(update => {
                            toastMessageEl.textContent = update.message;
                            toastLinkEl.href = update.url;
                            updateToast.show();

                            if (soundEnabled && notificationSound) {
                                notificationSound.play().catch(error => console.log("A reprodução do som falhou:", error));
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Erro ao verificar atualizações:', error);
                    clearInterval(updateInterval); 
                });
        }

        updateSoundButtonUI();
        const updateInterval = setInterval(checkForUpdates, 15000);
    }
});