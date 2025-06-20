# Dashboard do Sistema de Irrigação Inteligente

Este dashboard fornece uma interface visual interativa para monitorar e analisar os dados do Sistema de Irrigação Inteligente. Ele permite visualizar leituras de sensores, períodos de irrigação e alertas, além de oferecer funcionalidades de simulação para testar o sistema.

## Funcionalidades

### Visualização de Dados
- **Métricas em Tempo Real**: Exibe os valores atuais de umidade, pH, status da irrigação e alertas ativos
- **Gráficos Interativos**: Mostra a evolução dos parâmetros ao longo do tempo
- **Períodos de Irrigação**: Destaca visualmente quando o sistema de irrigação esteve ativo
- **Alertas**: Lista e categoriza os alertas gerados pelo sistema

### Filtros e Controles
- **Seleção de Fazenda e Área**: Permite filtrar os dados por fazenda e área específica
- **Período de Análise**: Ajusta o intervalo de tempo para visualização (1-30 dias)
- **Atualização de Dados**: Botão para atualizar os dados em tempo real

### Simulação
- **Leituras Simuladas**: Adiciona novas leituras de sensores para testar o comportamento do sistema
- **Geração Automática de Alertas**: Cria alertas quando os valores simulados estão fora dos limites aceitáveis
- **Ativação de Irrigação**: Inicia automaticamente a irrigação quando a umidade está baixa

## Como Usar

### Instalação

1. Instale as dependências necessárias:
   ```
   pip install -r requirements.txt
   ```

2. Execute o dashboard:
   ```
   streamlit run dashboard.py
   ```

3. Acesse o dashboard no navegador (geralmente em http://localhost:8501)

### Navegação

- **Painel Principal**: Exibe métricas e gráficos para a área selecionada
- **Abas**: Alterne entre diferentes visualizações (Umidade e Irrigação, Nutrientes e pH, Alertas)
- **Barra Lateral**: Contém filtros e controles para personalizar a visualização
- **Seção de Simulação**: Permite adicionar leituras simuladas para testar o sistema

## Interpretação dos Dados

### Umidade do Solo
- **Ideal**: Entre 30% e 70%
- **Baixa**: Abaixo de 30% (ativa irrigação)
- **Alta**: Acima de 70% (condição crítica)

### pH do Solo
- **Ideal**: Entre 5.5 e 7.0
- **Fora da faixa**: Gera alerta de condição crítica

### Nutrientes
- **Fósforo e Potássio**: Valores acima de 0.5 mg/kg são considerados adequados
- **Valores baixos**: Geram alertas de deficiência de nutrientes

## Geração de Dados Simulados

Se o banco de dados estiver vazio, o dashboard gerará automaticamente dados simulados para demonstração, incluindo:

- 7 dias de leituras de sensores (uma por hora)
- Ciclos de irrigação quando a umidade está baixa
- Alertas para condições críticas

## Requisitos Técnicos

- Python 3.7+
- Streamlit 1.24.0+
- Pandas 2.0.3+
- Plotly 5.15.0+
- SQLite3
- Banco de dados configurado conforme o schema do Sistema de Irrigação Inteligente

## Integração com o Sistema Completo

Este dashboard se integra ao Sistema de Irrigação Inteligente, utilizando o mesmo banco de dados e modelo de dados. Ele pode ser usado em conjunto com:

- O firmware ESP32 para monitoramento em tempo real
- O simulador Python para testes sem hardware
- A interface MQTT para acesso remoto

## Personalização

O dashboard pode ser personalizado editando o arquivo `dashboard.py`:

- Ajuste os limites para alertas e irrigação
- Adicione novos tipos de gráficos e visualizações
- Modifique o layout e as cores
- Integre com fontes de dados adicionais