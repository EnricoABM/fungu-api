// alerts.js - Gerenciamento de alertas (criação e listagem)
// Depende de api.js (apiGet, apiPost) - carregado antes deste script

// Carrega os alertas existentes e os renderiza na lista
async function loadAlerts() {
    const list = document.getElementById('alerts-list');
    const emptyState = document.getElementById('empty-state');
    list.innerHTML = '';

    try {
        const data = await apiGet('/alerts');
        const alerts = data.alerts || [];

        if (alerts.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');
        alerts.forEach(function(alertItem) {
            const card = document.createElement('div');
            card.className = 'border rounded-lg p-4 mb-3 bg-gray-50';
            card.innerHTML =
                '<div class="text-gray-700">' +
                'Variável: <span class="font-semibold">' + escapeHtml(alertItem.variable) + '</span>, ' +
                'Condição: <span class="font-semibold">' + escapeHtml(alertItem.condition) + ' ' + escapeHtml(alertItem.threshold) + '</span>' +
                '</div>';
            list.appendChild(card);
        });
    } catch (error) {
        showMessage('Erro ao carregar alertas: ' + error.message, true);
    }
}

// Cria um novo alerta a partir do formulário
async function createAlert() {
    const variable = document.getElementById('alert-variable').value;
    const condition = document.getElementById('alert-condition').value;
    const thresholdInput = document.getElementById('alert-threshold').value;
    const threshold = parseFloat(thresholdInput);

    if (thresholdInput === '' || isNaN(threshold)) {
        showMessage('Informe um valor limite válido', true);
        return;
    }

    try {
        await apiPost('/alerts/register', {
            variable: variable,
            condition: condition,
            threshold: threshold
        });
        showMessage('Alerta criado com sucesso', false);
        document.getElementById('alert-threshold').value = '';
        loadAlerts();
    } catch (error) {
        showMessage('Erro ao criar alerta: ' + error.message, true);
    }
}

// Exibe uma mensagem na área de feedback
function showMessage(text, isError) {
    const msg = document.getElementById('alert-msg');
    msg.textContent = text;
    msg.classList.remove('hidden');
    msg.classList.toggle('text-red-500', isError);
    msg.classList.toggle('text-green-600', !isError);
}

// Escapa caracteres especiais para evitar injeção de HTML
function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value;
    return div.innerHTML;
}

// Inicialização da página
requireAuth();
renderNav('alerts');
loadAlerts();
document.getElementById('create-alert-btn').addEventListener('click', createAlert);
