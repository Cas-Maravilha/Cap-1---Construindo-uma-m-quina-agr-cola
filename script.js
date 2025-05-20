// Configurações e constantes
const LIMITE_UMIDADE_BAIXA = 30.0;
const LIMITE_UMIDADE_ALTA = 70.0;
const PH_IDEAL_MIN = 5.5;
const PH_IDEAL_MAX = 7.0;

// Elementos do DOM
const umidadeValor = document.getElementById('umidade-valor');
const umidadeStatus = document.getElementById('umidade-status');
const phValor = document.getElementById('ph-valor');
const phStatus = document.getElementById('ph-status');
const fosforoStatus = document.getElementById('fosforo-status');
const fosforoInfo = document.getElementById('fosforo-info');
const potassioStatus = document.getElementById('potassio-status');
const potassioInfo = document.getElementById('potassio-info');
const irrigacaoIndicator = document.getElementById('irrigacao-indicator');
const irrigacaoStatus = document.getElementById('irrigacao-status');
const alertaIndicator = document.getElementById('alerta-indicator');
const alertaStatus = document.getElementById('alerta-status');
const btnIrrigar = document.getElementById('btn-irrigar');
const btnParar = document.getElementById('btn-parar');
const tableBody = document.getElementById('table-body');

// Estado do sistema
let sistemaDados = {
    umidade: 0,
    ph: 0,
    fosforo: false,
    potassio: false,
    irrigacaoAtiva: false,
    condicaoCritica: false,
    historicoLeituras: []
};

// Inicialização do gráfico
const ctx = document.getElementById('history-chart').getContext('2d');
const historicoChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Umidade (%)',
                data: [],
                borderColor: '#2196F3',
                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'pH',
                data: [],
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y1'
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Tempo'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Umidade (%)'
                },
                min: 0,
                max: 100,
                position: 'left'
            },
            y1: {
                title: {
                    display: true,
                    text: 'pH'
                },
                min: 0,
                max: 14,
                position: 'right',
                grid: {
                    drawOnChartArea: false
                }
            }
        },
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    }
});

// Funções para atualizar a interface
function atualizarSensores(dados) {
    // Atualiza umidade
    umidadeValor.textContent = dados.umidade.toFixed(1);
    if (dados.umidade < LIMITE_UMIDADE_BAIXA) {
        umidadeStatus.textContent = 'BAIXA';
        umidadeStatus.className = 'sensor-status status-warning';
    } else if (dados.umidade > LIMITE_UMIDADE_ALTA) {
        umidadeStatus.textContent = 'ALTA';
        umidadeStatus.className = 'sensor-status status-critical';
    } else {
        umidadeStatus.textContent = 'IDEAL';
        umidadeStatus.className = 'sensor-status status-ok';
    }

    // Atualiza pH
    phValor.textContent = dados.ph.toFixed(1);
    if (dados.ph < PH_IDEAL_MIN || dados.ph > PH_IDEAL_MAX) {
        phStatus.textContent = 'FORA DA FAIXA IDEAL';
        phStatus.className = 'sensor-status status-critical';
    } else {
        phStatus.textContent = 'IDEAL';
        phStatus.className = 'sensor-status status-ok';
    }

    // Atualiza fósforo
    fosforoStatus.textContent = dados.fosforo ? 'ADEQUADO' : 'BAIXO';
    fosforoInfo.className = 'sensor-status ' + (dados.fosforo ? 'status-ok' : 'status-critical');
    fosforoInfo.textContent = dados.fosforo ? 'Nível adequado' : 'Necessita correção';

    // Atualiza potássio
    potassioStatus.textContent = dados.potassio ? 'ADEQUADO' : 'BAIXO';
    potassioInfo.className = 'sensor-status ' + (dados.potassio ? 'status-ok' : 'status-critical');
    potassioInfo.textContent = dados.potassio ? 'Nível adequado' : 'Necessita correção';

    // Atualiza status de irrigação
    irrigacaoIndicator.className = 'indicator ' + (dados.irrigacaoAtiva ? 'active-green' : '');
    irrigacaoStatus.textContent = dados.irrigacaoAtiva ? 'Ativa' : 'Desativada';

    // Atualiza status de alerta
    alertaIndicator.className = 'indicator ' + (dados.condicaoCritica ? 'active-red' : '');
    alertaStatus.textContent = dados.condicaoCritica ? 'Condição crítica' : 'Nenhum alerta';
}

function adicionarLeitura(dados) {
    // Adiciona ao histórico
    const agora = new Date();
    const dataFormatada = agora.toLocaleString();
    
    const leitura = {
        timestamp: dataFormatada,
        umidade: dados.umidade,
        ph: dados.ph,
        fosforo: dados.fosforo,
        potassio: dados.potassio,
        irrigacaoAtiva: dados.irrigacaoAtiva,
        condicaoCritica: dados.condicaoCritica
    };
    
    sistemaDados.historicoLeituras.push(leitura);
    
    // Limita o histórico a 20 entradas
    if (sistemaDados.historicoLeituras.length > 20) {
        sistemaDados.historicoLeituras.shift();
    }
    
    // Atualiza a tabela
    atualizarTabelaHistorico();
    
    // Atualiza o gráfico
    atualizarGrafico();
}

function atualizarTabelaHistorico() {
    tableBody.innerHTML = '';
    
    sistemaDados.historicoLeituras.forEach(leitura => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${leitura.timestamp}</td>
            <td>${leitura.umidade.toFixed(1)}%</td>
            <td>${leitura.ph.toFixed(1)}</td>
            <td>${leitura.fosforo ? 'Adequado' : 'Baixo'}</td>
            <td>${leitura.potassio ? 'Adequado' : 'Baixo'}</td>
            <td>${leitura.irrigacaoAtiva ? 'Ativa' : 'Desativada'}</td>
            <td>${leitura.condicaoCritica ? 'Sim' : 'Não'}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

function atualizarGrafico() {
    // Limpa os dados antigos
    historicoChart.data.labels = [];
    historicoChart.data.datasets[0].data = [];
    historicoChart.data.datasets[1].data = [];
    
    // Adiciona os novos dados
    sistemaDados.historicoLeituras.forEach(leitura => {
        historicoChart.data.labels.push(leitura.timestamp);
        historicoChart.data.datasets[0].data.push(leitura.umidade);
        historicoChart.data.datasets[1].data.push(leitura.ph);
    });
    
    // Atualiza o gráfico
    historicoChart.update();
}

// Função para simular leituras de sensores
function simularLeitura() {
    // Gera valores aleatórios para simular os sensores
    const umidade = Math.random() * 100;
    const ph = 4 + Math.random() * 6; // pH entre 4 e 10
    const fosforo = Math.random() > 0.3; // 70% de chance de estar adequado
    const potassio = Math.random() > 0.3; // 70% de chance de estar adequado
    
    // Determina o estado do sistema
    const necessitaIrrigacao = umidade < LIMITE_UMIDADE_BAIXA;
    const condicaoCritica = umidade > LIMITE_UMIDADE_ALTA || 
                           ph < PH_IDEAL_MIN || 
                           ph > PH_IDEAL_MAX || 
                           !fosforo || 
                           !potassio;
    
    const irrigacaoAtiva = necessitaIrrigacao && !condicaoCritica;
    
    // Atualiza o estado do sistema
    sistemaDados = {
        ...sistemaDados,
        umidade,
        ph,
        fosforo,
        potassio,
        irrigacaoAtiva,
        condicaoCritica
    };
    
    // Atualiza a interface
    atualizarSensores(sistemaDados);
    
    // Adiciona ao histórico
    adicionarLeitura(sistemaDados);
}

// Event listeners para os botões
btnIrrigar.addEventListener('click', () => {
    sistemaDados.irrigacaoAtiva = true;
    atualizarSensores(sistemaDados);
    alert('Irrigação ativada manualmente!');
});

btnParar.addEventListener('click', () => {
    sistemaDados.irrigacaoAtiva = false;
    atualizarSensores(sistemaDados);
    alert('Irrigação desativada manualmente!');
});

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Simula uma leitura inicial
    simularLeitura();
    
    // Configura simulação periódica (a cada 10 segundos)
    setInterval(simularLeitura, 10000);
});

// Função para conectar com o ESP32 (simulada)
function conectarESP32() {
    console.log('Tentando conectar ao ESP32...');
    // Em uma implementação real, aqui seria feita a conexão via WebSocket ou API
    setTimeout(() => {
        console.log('ESP32 conectado com sucesso (simulado)');
    }, 1500);
}

// Chama a função de conexão
conectarESP32();