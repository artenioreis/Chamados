document.addEventListener('DOMContentLoaded', function() {
    
    // --- LÓGICA DOS GRÁFICOS (DASHBOARD) ---
    // Alterado de PIE para BAR (Colunas)
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusData = JSON.parse(statusCtx.dataset.chartdata);
        new Chart(statusCtx, {
            type: 'bar', // Mudado para barras (colunas)
            data: {
                labels: statusData.map(d => d.status),
                datasets: [{
                    label: 'Quantidade',
                    data: statusData.map(d => d.count),
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
                    borderWidth: 1
                }]
            },
            options: { 
                responsive: true, 
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 } // Garante números inteiros no eixo Y
                    }
                },
                plugins: { 
                    legend: { display: false }, // Remove legenda pois as barras já têm labels embaixo
                    title: { display: true, text: 'Distribuição por Status' } 
                } 
            }
        });
    }

    // Mantido BAR, ajustado escalas
    const sectorCtx = document.getElementById('sectorChart');
    if (sectorCtx) {
        const sectorData = JSON.parse(sectorCtx.dataset.chartdata);
        new Chart(sectorCtx, {
            type: 'bar',
            data: {
                labels: sectorData.map(d => d.sector),
                datasets: [{
                    label: 'Chamados',
                    data: sectorData.map(d => d.count),
                    backgroundColor: '#36A2EB',
                    borderWidth: 1
                }]
            },
            options: { 
                responsive: true, 
                scales: { 
                    y: { 
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    } 
                }, 
                plugins: { 
                    legend: { display: false },
                    title: { display: true, text: 'Volume por Setor' } 
                } 
            }
        });
    }

    // Alterado de DOUGHNUT para BAR (Colunas)
    const priorityCtx = document.getElementById('priorityChart');
    if (priorityCtx) {
        const priorityData = JSON.parse(priorityCtx.dataset.chartdata);
        new Chart(priorityCtx, {
            type: 'bar', // Mudado para barras
            data: {
                labels: priorityData.map(d => d.priority),
                datasets: [{
                    label: 'Quantidade',
                    data: priorityData.map(d => d.count),
                    backgroundColor: ['#FFCE56', '#36A2EB', '#FF6384'], // Cores mantidas para identificar prioridade
                    borderWidth: 1
                }]
            },
            options: { 
                responsive: true, 
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: { 
                    legend: { display: false },
                    title: { display: true, text: 'Frequência por Prioridade' } 
                } 
            }
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

    // --- LÓGICA GLOBAL DE NOTIFICAÇÕES (TICKETS E CHAT) ---
    if (document.getElementById('navbarDropdown')) {
        // --- PREFERÊNCIAS DE SOM ---
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
            updateSoundButtonUI();
            toggleSoundBtn.addEventListener('click', function(e) {
                e.preventDefault();
                soundEnabled = !soundEnabled;
                localStorage.setItem('notificationSoundEnabled', soundEnabled);
                updateSoundButtonUI();
            });
        }

        // --- NOTIFICAÇÕES DE CHAMADOS (TICKETS) ---
        const updateToastEl = document.getElementById('updateToast');
        if (updateToastEl) {
            const updateToast = new bootstrap.Toast(updateToastEl, { delay: 10000 });
            const toastMessageEl = document.getElementById('toast-message');
            const toastLinkEl = document.getElementById('toast-link');
            const ticketNotificationSound = document.getElementById('notification-sound');

            function checkForTicketUpdates() {
                fetch('/check_updates')
                    .then(response => response.ok ? response.json() : Promise.reject('A resposta da rede não foi OK'))
                    .then(data => {
                        if (data.updates && data.updates.length > 0) {
                            data.updates.forEach(update => {
                                toastMessageEl.textContent = update.message;
                                toastLinkEl.href = update.url;
                                updateToast.show();

                                if (soundEnabled && ticketNotificationSound) {
                                    ticketNotificationSound.play().catch(error => console.log("A reprodução do som falhou:", error));
                                }
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao verificar atualizações de chamados:', error);
                    });
            }
            setInterval(checkForTicketUpdates, 15000);
        }

        // --- NOTIFICAÇÕES DE CHAT (GLOBAL) ---
        const chatNavIndicator = document.getElementById('chat-nav-indicator');
        const chatNotificationSound = document.getElementById('chat-notification-sound');
        let knownUnreadSenders = new Set();

        function checkUnreadChatMessages() {
            fetch('/api/chat/unread_info')
                .then(response => response.ok ? response.json() : Promise.reject('Resposta de rede não foi OK'))
                .then(data => {
                    const unreadSenders = new Set(data.unread_senders || []);

                    if (unreadSenders.size > 0) {
                        chatNavIndicator.style.display = 'block'; // Mostra o ponto vermelho no menu

                        // Verifica se há um novo remetente não lido
                        let newNotification = false;
                        unreadSenders.forEach(senderId => {
                            if (!knownUnreadSenders.has(senderId)) {
                                newNotification = true;
                            }
                        });

                        // Toca o som se for uma notificação de um novo remetente
                        if (newNotification && soundEnabled && chatNotificationSound) {
                            chatNotificationSound.play().catch(error => console.log("A reprodução do som do chat falhou:", error));
                        }
                    } else {
                        chatNavIndicator.style.display = 'none'; // Esconde o ponto
                    }

                    // Atualiza o conjunto de remetentes conhecidos
                    knownUnreadSenders = unreadSenders;
                })
                .catch(error => {
                    console.error('Erro ao verificar mensagens de chat não lidas:', error);
                });
        }
        
        // Verifica por novas mensagens de chat a cada 10 segundos
        checkUnreadChatMessages();
        setInterval(checkUnreadChatMessages, 10000);
    }
    
    // --- LÓGICA PARA IMPRIMIR RELATÓRIO ---
    const printButton = document.getElementById('print-report-btn');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
});