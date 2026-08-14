// devices.js - Gerenciamento de dispositivos (mestres e escravos)
// Depende de api.js (apiGet, apiPost) e auth.js (requireAuth) - carregados antes deste script

function showMessage(elementId, message) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.classList.remove('hidden');
}

function clearMessages() {
    document.getElementById('error-msg').classList.add('hidden');
    document.getElementById('success-msg').classList.add('hidden');
}

function showError(message) {
    document.getElementById('success-msg').classList.add('hidden');
    showMessage('error-msg', message);
}

function showSuccess(message) {
    document.getElementById('error-msg').classList.add('hidden');
    showMessage('success-msg', message);
}

function formatMac(mac) {
    return mac.toUpperCase();
}

// Carrega e renderiza a lista de mestres
async function loadMasters() {
    const container = document.getElementById('masters-list');
    container.innerHTML = '<p class="text-gray-500">Carregando dispositivos...</p>';

    try {
        const masters = await apiGet('/device/masters');
        if (!masters.length) {
            container.innerHTML = '<p class="text-gray-500">Nenhum dispositivo cadastrado.</p>';
            return;
        }

        container.innerHTML = '';
        masters.forEach(function(master) {
            container.appendChild(createMasterCard(master));
        });
    } catch (error) {
        container.innerHTML = '';
        showError(error.message);
    }
}

// Cria o card de um mestre com botão de expandir escravos
function createMasterCard(master) {
    const card = document.createElement('div');
    card.className = 'border rounded-lg p-4 mb-3';
    card.id = 'master-card-' + master.mac;

    const header = document.createElement('div');
    header.className = 'flex items-center justify-between';

    const macLabel = document.createElement('span');
    macLabel.className = 'font-mono font-medium';
    macLabel.textContent = formatMac(master.mac);

    const expandBtn = document.createElement('button');
    expandBtn.textContent = 'Ver escravos';
    expandBtn.className = 'bg-gray-200 text-gray-700 px-3 py-1 rounded-lg hover:bg-gray-300 text-sm';
    expandBtn.addEventListener('click', function() {
        toggleSlaves(master.mac, expandBtn, card);
    });

    header.appendChild(macLabel);
    header.appendChild(expandBtn);
    card.appendChild(header);

    return card;
}

// Alterna a exibição da lista de escravos do mestre
async function toggleSlaves(mac, button, card) {
    const existing = document.getElementById('slaves-' + mac);
    if (existing) {
        existing.remove();
        button.textContent = 'Ver escravos';
        return;
    }

    button.textContent = 'Carregando...';
    const container = document.createElement('div');
    container.id = 'slaves-' + mac;
    container.className = 'mt-3 pl-4 border-l-2 border-gray-200';

    try {
        const slaves = await apiGet('/device/masters/' + encodeURIComponent(mac) + '/slaves');
        if (!slaves.length) {
            container.innerHTML = '<p class="text-gray-500 text-sm">Nenhum escravo vinculado.</p>';
        } else {
            const list = document.createElement('ul');
            list.className = 'space-y-1';
            slaves.forEach(function(slave) {
                const item = document.createElement('li');
                item.className = 'text-sm flex items-center gap-2';
                item.innerHTML = '<span class="text-gray-400">&#9679;</span>';
                item.appendChild(document.createTextNode(formatMac(slave.mac)));
                list.appendChild(item);
            });
            container.appendChild(list);
        }
    } catch (error) {
        container.innerHTML = '<p class="text-red-500 text-sm">' + error.message + '</p>';
    }

    card.appendChild(container);
    button.textContent = 'Ocultar escravos';
}

// Cadastra um novo mestre
async function registerMaster() {
    clearMessages();
    const macInput = document.getElementById('master-mac');
    const mac = macInput.value.trim();

    if (!mac) {
        showError('Informe o MAC do mestre.');
        return;
    }

    try {
        await apiPost('/device/master/register', { mac: mac });
        showSuccess('Mestre cadastrado com sucesso');
        macInput.value = '';
        loadMasters();
    } catch (error) {
        showError(error.message);
    }
}

// Cadastra um novo escravo
async function registerSlave() {
    clearMessages();
    const masterMacInput = document.getElementById('slave-mac-master');
    const slaveMacInput = document.getElementById('slave-mac');
    const masterMac = masterMacInput.value.trim();
    const slaveMac = slaveMacInput.value.trim();

    if (!masterMac || !slaveMac) {
        showError('Informe o MAC do mestre e o MAC do escravo.');
        return;
    }

    try {
        await apiPost('/device/register', { mac_master: masterMac, mac_slave: slaveMac });
        showSuccess('Escravo cadastrado com sucesso');
        masterMacInput.value = '';
        slaveMacInput.value = '';
        loadMasters();
    } catch (error) {
        showError(error.message);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    requireAuth();
    renderNav('devices');
    loadMasters();

    document.getElementById('register-master-btn').addEventListener('click', registerMaster);
    document.getElementById('register-slave-btn').addEventListener('click', registerSlave);
});
