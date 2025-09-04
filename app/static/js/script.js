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