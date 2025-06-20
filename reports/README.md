# Sistema de Irrigação Inteligente - Modelo Expandido

Este projeto implementa um sistema de irrigação inteligente que evoluiu de um modelo simples para uma solução completa de gerenciamento agrícola, capaz de monitorar múltiplas fazendas e áreas de cultivo.

## Evolução do Modelo de Dados

O sistema foi expandido para atender às necessidades de uma operação agrícola em escala comercial, incorporando:

- Gerenciamento de múltiplas fazendas
- Monitoramento de diversas áreas de cultivo
- Configuração flexível de sensores
- Rastreamento de manutenções e técnicos
- Histórico detalhado de irrigação e alertas

## Estrutura do Banco de Dados

### Modelo Entidade-Relacionamento (MER)

O sistema utiliza um modelo relacional com as seguintes entidades principais:

1. **Fazenda**: Propriedades agrícolas onde o sistema está instalado
2. **Área Monitorada**: Setores específicos dentro de cada fazenda
3. **Sensor**: Dispositivos que coletam dados do ambiente
4. **Sensor_Area**: Associação entre sensores e áreas (N:N)
5. **Leitura**: Dados coletados pelos sensores
6. **Técnico**: Profissionais responsáveis pela manutenção
7. **Manutenção**: Registros de intervenções nos sensores
8. **Irrigação**: Ciclos de irrigação realizados
9. **Alerta**: Condições críticas detectadas

### Relacionamentos

- Fazenda 1:N Área Monitorada
- Área Monitorada N:N Sensor (via Sensor_Area)
- Sensor 1:N Leitura
- Área Monitorada 1:N Leitura
- Sensor 1:N Manutenção
- Técnico 1:N Manutenção
- Área Monitorada 1:N Irrigação
- Área Monitorada 1:N Alerta
- Sensor 1:N Alerta

## Componentes do Sistema

### Hardware Simulado

- **ESP32**: Microcontrolador responsável pelo controle geral do sistema
- **Sensores**: Umidade do solo, pH, fósforo, potássio, temperatura, luminosidade
- **Relé**: Controla a bomba d'água para irrigação
- **LEDs**: Indicam o status da irrigação e alertas

### Software

- **Firmware ESP32**: Código para leitura de sensores e controle de irrigação
- **Interface Web**: Dashboard para monitoramento e controle
- **API MQTT**: Comunicação IoT para acesso remoto
- **Banco de Dados**: Armazenamento e análise de dados
- **Simulador Python**: Teste do sistema sem hardware

## Interfaces de Usuário

O sistema oferece três interfaces diferentes para monitoramento e controle:

1. **Interface Web Local**: Acessível diretamente do ESP32
2. **Dashboard MQTT**: Acessível de qualquer lugar via internet
3. **Simulador Python**: Para testes e desenvolvimento

## Lógica de Funcionamento

O sistema toma decisões de irrigação com base nas seguintes regras:

1. **Ativação da Irrigação**:
   - A irrigação é ativada quando a umidade do solo está abaixo de 30%
   - A irrigação só é ativada se não houver condições críticas

2. **Condições Críticas** (impedem a irrigação):
   - Umidade do solo acima de 70% (solo encharcado)
   - pH fora da faixa ideal (5.5 a 7.0)
   - Níveis baixos de fósforo ou potássio

## Operações CRUD

O sistema implementa operações CRUD (Create, Read, Update, Delete) completas para todas as entidades através da classe `SistemaIrrigacaoDB`:

```python
# Exemplo de uso
db = SistemaIrrigacaoDB()

# Criar (Create)
id_fazenda = db.adicionar_fazenda("Fazenda Modelo", "Localização", 150.5)
id_area = db.adicionar_area(id_fazenda, "Setor A", "Coordenadas")
id_sensor = db.adicionar_sensor("umidade", "DHT22", "%")

# Ler (Read)
fazendas = db.listar_fazendas()
area = db.obter_area(id_area)
leituras = db.listar_leituras(id_area=id_area, limite=10)

# Atualizar (Update)
db.atualizar_fazenda(id_fazenda, nome="Novo Nome")
db.resolver_alerta(id_alerta)

# Excluir (Delete)
db.excluir_sensor(id_sensor)
db.excluir_leitura(id_leitura)
```

## Compatibilidade com o Modelo Anterior

Para garantir compatibilidade com aplicações existentes, o sistema inclui visões SQL que simulam as tabelas do modelo anterior:

- `leituras_compat`: Simula a tabela `leituras` original
- `historico_irrigacao_compat`: Simula a tabela `historico_irrigacao` original
- `alertas_compat`: Simula a tabela `alertas` original

## Como Usar o Sistema

### Configuração Inicial
1. Execute o script `schema_expandido.sql` para criar as tabelas
2. Use a classe `SistemaIrrigacaoDB` para interagir com o banco de dados

### Exemplos
- Veja o arquivo `exemplo_uso.py` para um exemplo completo de uso do sistema
- Consulte `modelo_er_expandido.md` para detalhes sobre o modelo de dados

## Requisitos

### Para o Simulador Python
- Python 3.x
- SQLite3
- Biblioteca PySerial (para leitura da porta serial)
- Biblioteca Paho MQTT (para comunicação MQTT)

### Para o ESP32
- Arduino IDE ou PlatformIO
- Bibliotecas:
  - WiFi
  - WebServer
  - DHT sensor library
  - ArduinoJson
  - SPIFFS
  - PubSubClient (para MQTT)

## Implementação Real

Em uma implementação real, o sistema pode ser expandido com:

- Integração com estações meteorológicas
- Análise preditiva para otimização da irrigação
- Integração com sistemas de gestão agrícola
- Alertas por e-mail ou SMS
- Aplicativo móvel para monitoramento em campo