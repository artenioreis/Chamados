// Exemplo de script para dashboard com Chart.js (você precisaria importar a biblioteca)
// Adicione <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> em seu base.html
document.addEventListener('DOMContentLoaded', function() {
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusData = JSON.parse(statusCtx.dataset.chartdata);
        new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: statusData.map(d => d.status),
                datasets: [{
                    data: statusData.map(d => d.count),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Chamados por Status'
                    }
                }
            }
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
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Chamados por Setor de Destino'
                    }
                }
            }
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
                    backgroundColor: [
                        '#FFCE56', '#36A2EB', '#FF6384'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Chamados por Prioridade'
                    }
                }
            }
        });
    }
});
// app/static/js/script.js

// ... (código dos gráficos que já existe) ...

// Lógica para o Kanban Drag-and-Drop
document.addEventListener('DOMContentLoaded', function() {
    // Código dos gráficos (deve estar aqui)
    // ...

    // Ativa o Drag-and-Drop apenas na página do Kanban
    const kanbanContainer = document.querySelector('.kanban-container');
    if (kanbanContainer) {
        const kanbanColumns = document.querySelectorAll('.kanban-column-body');
        
        kanbanColumns.forEach(column => {
            new Sortable(column, {
                group: 'kanban', // Permite mover itens entre colunas do mesmo grupo
                animation: 150,
                ghostClass: 'sortable-ghost', // Classe CSS para o item "fantasma"
                dragClass: 'sortable-drag', // Classe CSS para o item sendo arrastado

                // Evento chamado quando um item é solto em uma coluna (nova ou a mesma)
                onEnd: function (evt) {
                    const itemEl = evt.item;      // O card que foi movido
                    const toColumn = evt.to;        // A coluna de destino
                    const fromColumn = evt.from;    // A coluna de origem
                    
                    const ticketId = itemEl.dataset.ticketId;
                    const newStatus = toColumn.dataset.status;
                    const oldStatus = fromColumn.dataset.status;

                    // Só envia a requisição se a coluna for diferente
                    if (newStatus !== oldStatus) {
                        console.log(`Movendo ticket ${ticketId} do status '${oldStatus}' para '${newStatus}'`);

                        // Envia a atualização para o servidor
                        fetch(`/update_ticket_status/${ticketId}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ new_status: newStatus })
                        })
                        .then(response => {
                            if (!response.ok) {
                                // Se a resposta não for OK (ex: 403, 404, 500), lança um erro
                                return response.json().then(err => { throw new Error(err.message || 'Erro no servidor') });
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.success) {
                                console.log('Status atualizado com sucesso!');
                                // Opcional: exibir uma notificação de sucesso (Toast)
                            } else {
                                // Se a API retornar sucesso=false, reverte a ação
                                console.error('Falha ao atualizar o status:', data.message);
                                fromColumn.appendChild(itemEl); 
                                alert('Erro ao atualizar o chamado: ' + data.message);
                            }
                        })
                        .catch(error => {
                            // Se ocorrer um erro de rede ou na resposta, reverte a ação
                            console.error('Erro:', error);
                            fromColumn.appendChild(itemEl);
                            alert('Não foi possível atualizar o chamado. ' + error.message);
                        });
                    }
                }
            });
        });
    }
});
// ... (código existente dos gráficos e do kanban) ...

// Lógica para Modais de Gerenciamento de Usuário
document.addEventListener('DOMContentLoaded', function() {
    // Modal de Alterar Senha
    var changePasswordModal = document.getElementById('changePasswordModal');
    if (changePasswordModal) {
        changePasswordModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');

            var modalTitle = changePasswordModal.querySelector('#userNamePassword');
            var modalInputUserId = changePasswordModal.querySelector('#userIdPassword');
            
            modalTitle.textContent = userName;
            modalInputUserId.value = userId;
        });
    }

    // Modal de Excluir Usuário
    var deleteUserModal = document.getElementById('deleteUserModal');
    if (deleteUserModal) {
        deleteUserModal.addEventListener('show.bs.modal', function (event) {
            var button = event.relatedTarget;
            var userId = button.getAttribute('data-user-id');
            var userName = button.getAttribute('data-user-name');
            
            var modalText = deleteUserModal.querySelector('#userNameDelete');
            var deleteForm = deleteUserModal.querySelector('#deleteUserForm');
            
            modalText.textContent = userName;
            deleteForm.action = '/delete_user/' + userId;
        });
    }
});