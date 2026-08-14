// dashboard.js - Dashboard de monitoramento de medições
// Depende de api.js (apiGet) e auth.js (requireAuth) - carregados antes deste script

// Mapeia nomes de variáveis (português/inglês) para rótulos de exibição
const VARIABLE_LABELS = {
    temperatura: "Temperatura",
    umidade: "Umidade",
    temp: "Temperatura",
    hum: "Umidade",
    co2: "CO2",
    tvoc: "TVOC",
    aqi: "AQI",
    lux: "Luminosidade",
    luminosidade: "Luminosidade"
};

const POLLING_INTERVAL_MS = 10000;
const DEFAULT_VARIABLE = 'temperatura';

let measurementChart = null;
let pollingIntervalId = null;

// Carrega as medições mais recentes e atualiza os cards
async function loadLatestMeasurements() {
    try {
        const data = await apiGet('/measurements/latest');
        const values = { temperatura: null, umidade: null, co2: null, tvoc: null, aqi: null, lux: null };

        data.forEach(function(item) {
            const key = (item.variable || '').toLowerCase();
            // Aceita nomes em português (temperatura/umidade/luminosidade) e inglês (temp/hum/lux)
            let cardKey = key;
            if (key === 'temp') cardKey = 'temperatura';
            if (key === 'hum') cardKey = 'umidade';
            if (key === 'luminosidade') cardKey = 'lux';
            if (key in values) {
                values[cardKey] = parseFloat(item.value);
            }
        });

        Object.keys(values).forEach(function(key) {
            const el = document.getElementById('value-' + key);
            if (el) {
                const value = values[key];
                el.textContent = value !== null && !isNaN(value) ? formatValue(key, value) : '--';
            }
        });

        updateLastUpdated();
    } catch (error) {
        showError('Erro ao carregar dados');
    }
}

// Carrega o histórico da variável selecionada e atualiza o gráfico
async function loadMeasurementHistory(variable) {
    try {
        const data = await apiGet('/measurements?variable=' + variable + '&page_size=100');
        const measurements = data.measurements || [];
        const labels = measurements.map(function(m) { return m.measured_at; });
        const values = measurements.map(function(m) { return parseFloat(m.value); });

        if (measurementChart) {
            measurementChart.data.labels = labels;
            measurementChart.data.datasets[0].data = values;
            measurementChart.options.scales.y.title.text = VARIABLE_LABELS[variable] || variable;
            measurementChart.update();
        }

        toggleEmptyState(measurements.length === 0);
    } catch (error) {
        showError('Erro ao carregar dados');
    }
}

// Inicializa o gráfico de linhas com dados vazios
function initChart() {
    const ctx = document.getElementById('measurement-chart');
    if (!ctx) return;
    measurementChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Valor',
                data: [],
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: VARIABLE_LABELS[DEFAULT_VARIABLE] }
                }
            }
        }
    });
}

// Inicia o polling de atualização a cada 10 segundos
function startPolling() {
    stopPolling();
    pollingIntervalId = setInterval(function() {
        loadLatestMeasurements();
        const variable = getSelectedVariable();
        loadMeasurementHistory(variable);
    }, POLLING_INTERVAL_MS);
}

// Para o polling de atualização
function stopPolling() {
    if (pollingIntervalId !== null) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
    }
}

// Atualiza o horário da última atualização
function updateLastUpdated() {
    const el = document.getElementById('last-updated');
    if (el) {
        el.textContent = new Date().toLocaleTimeString('pt-BR');
    }
}

// Formata o valor para exibição no card
function formatValue(key, value) {
    if (key === 'temperatura') return value.toFixed(1) + ' °C';
    if (key === 'umidade') return value.toFixed(1) + ' %';
    if (key === 'lux') return Math.round(value) + ' lux';
    return String(Math.round(value));
}

// Exibe/esconde o estado vazio do gráfico
function toggleEmptyState(show) {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.classList.toggle('hidden', !show);
    }
}

// Retorna a variável selecionada no dropdown
function getSelectedVariable() {
    const select = document.getElementById('variable-select');
    return select ? select.value : DEFAULT_VARIABLE;
}

// Exibe mensagem de erro temporária
function showError(message) {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.textContent = message;
        emptyState.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    requireAuth();
    renderNav('dashboard');
    initChart();
    loadLatestMeasurements();
    loadMeasurementHistory(DEFAULT_VARIABLE);
    startPolling();

    const select = document.getElementById('variable-select');
    if (select) {
        select.addEventListener('change', function() {
            loadMeasurementHistory(select.value);
        });
    }
});
