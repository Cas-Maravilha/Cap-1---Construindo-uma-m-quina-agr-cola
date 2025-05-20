# Modelo Entidade-Relacionamento Expandido - Sistema de Irrigação Inteligente

## Entidades

### 1. Fazenda
Representa a propriedade agrícola onde o sistema está instalado.

**Atributos:**
- `id_fazenda` (PK): Identificador único da fazenda
- `nome`: Nome da fazenda
- `localizacao`: Endereço ou coordenadas geográficas da fazenda
- `tamanho_hectares`: Tamanho total da fazenda em hectares

### 2. Área Monitorada
Representa uma área específica dentro da fazenda que é monitorada pelo sistema.

**Atributos:**
- `id_area` (PK): Identificador único da área
- `id_fazenda` (FK): Referência à fazenda a que pertence
- `nome_area`: Nome ou identificação da área
- `coordenadas`: Coordenadas geográficas que delimitam a área

### 3. Sensor
Representa os diferentes tipos de sensores utilizados no sistema.

**Atributos:**
- `id_sensor` (PK): Identificador único do sensor
- `tipo_sensor`: Tipo de sensor (umidade, pH, fósforo, potássio, etc.)
- `modelo`: Modelo ou fabricante do sensor
- `unidade_medida`: Unidade de medida utilizada pelo sensor

### 4. Sensor_Area (associativa)
Associa sensores a áreas monitoradas, permitindo que um sensor seja utilizado em várias áreas e uma área tenha vários sensores.

**Atributos:**
- `id_sensor_area` (PK): Identificador único da associação
- `id_sensor` (FK): Referência ao sensor
- `id_area` (FK): Referência à área monitorada
- `data_instalacao`: Data em que o sensor foi instalado na área
- `data_remocao`: Data em que o sensor foi removido da área (NULL se ainda estiver ativo)

### 5. Leitura
Armazena os dados coletados pelos sensores.

**Atributos:**
- `id_leitura` (PK): Identificador único da leitura
- `id_sensor` (FK): Referência ao sensor que realizou a leitura
- `id_area` (FK): Referência à área onde a leitura foi realizada
- `valor`: Valor registrado pelo sensor
- `data_hora`: Data e hora da leitura

### 6. Técnico
Representa os técnicos responsáveis pela manutenção dos sensores.

**Atributos:**
- `id_tecnico` (PK): Identificador único do técnico
- `nome`: Nome completo do técnico
- `email`: Endereço de e-mail do técnico
- `especialidade`: Área de especialização do técnico

### 7. Manutenção
Registra as manutenções realizadas nos sensores.

**Atributos:**
- `id_manutencao` (PK): Identificador único da manutenção
- `id_sensor` (FK): Referência ao sensor que recebeu manutenção
- `id_tecnico` (FK): Referência ao técnico que realizou a manutenção
- `data_manutencao`: Data em que a manutenção foi realizada
- `tipo_manutencao`: Tipo de manutenção (preventiva, corretiva, calibração, etc.)
- `observacoes`: Observações ou detalhes sobre a manutenção

### 8. Irrigação
Registra os ciclos de irrigação realizados pelo sistema.

**Atributos:**
- `id_irrigacao` (PK): Identificador único do ciclo de irrigação
- `id_area` (FK): Referência à área onde ocorreu a irrigação
- `inicio_timestamp`: Data e hora de início da irrigação
- `fim_timestamp`: Data e hora de término da irrigação
- `duracao_minutos`: Duração da irrigação em minutos
- `volume_agua`: Volume de água utilizado em litros
- `modo`: Modo de ativação (automático ou manual)

### 9. Alerta
Registra alertas e condições críticas detectadas pelo sistema.

**Atributos:**
- `id_alerta` (PK): Identificador único do alerta
- `id_area` (FK): Referência à área que gerou o alerta
- `id_sensor` (FK): Referência ao sensor que detectou a condição crítica
- `timestamp`: Data e hora do alerta
- `tipo_alerta`: Tipo de alerta (umidade baixa, pH inadequado, etc.)
- `descricao`: Descrição detalhada do alerta
- `resolvido`: Status de resolução (1 = resolvido, 0 = não resolvido)

## Relacionamentos

1. **Fazenda 1:N Área Monitorada**: Uma fazenda pode ter várias áreas monitoradas
2. **Área Monitorada N:N Sensor** (via Sensor_Area): Uma área pode ter vários sensores e um sensor pode estar em várias áreas
3. **Sensor 1:N Leitura**: Um sensor pode gerar várias leituras
4. **Área Monitorada 1:N Leitura**: Uma área pode ter várias leituras
5. **Sensor 1:N Manutenção**: Um sensor pode receber várias manutenções
6. **Técnico 1:N Manutenção**: Um técnico pode realizar várias manutenções
7. **Área Monitorada 1:N Irrigação**: Uma área pode ter vários ciclos de irrigação
8. **Área Monitorada 1:N Alerta**: Uma área pode gerar vários alertas
9. **Sensor 1:N Alerta**: Um sensor pode gerar vários alertas

## Diagrama ER Simplificado

```
+-------------+       +------------------+       +-------------+
|   Fazenda   |------>| Área Monitorada  |<----->|   Sensor    |
+-------------+       +------------------+       +-------------+
                             ^   ^                     ^
                             |   |                     |
                             |   |                     |
+-------------+       +------+   +------+       +-------------+
| Manutenção  |<------|                 |------>|   Leitura   |
+-------------+       |                 |       +-------------+
      ^               |                 |
      |               |                 |
+-------------+       |                 |       +-------------+
|  Técnico    |       |                 |------>|   Alerta    |
+-------------+       |                 |       +-------------+
                      |                 |
                      |                 |
                      +------+   +------+
                             |   |
                             v   v
                      +------------------+
                      |    Irrigação     |
                      +------------------+
```

## Compatibilidade com o Modelo Anterior

Este modelo expandido é uma evolução do modelo anterior, mantendo compatibilidade com as funcionalidades existentes:

1. **Leituras**: A entidade `Leitura` no novo modelo corresponde à tabela `leituras` do modelo anterior, mas agora com referências explícitas aos sensores e áreas.

2. **Irrigação**: A entidade `Irrigação` no novo modelo corresponde à tabela `historico_irrigacao` do modelo anterior, mas agora associada a áreas específicas.

3. **Alertas**: A entidade `Alerta` no novo modelo corresponde à tabela `alertas` do modelo anterior, mas agora com referências explícitas aos sensores e áreas que geraram o alerta.

## Justificativa da Estrutura

1. **Escalabilidade**: O modelo expandido permite gerenciar múltiplas fazendas e áreas, cada uma com seus próprios sensores e configurações.

2. **Rastreabilidade**: Cada leitura, irrigação e alerta está vinculado não apenas ao sensor, mas também à área específica, permitindo análises mais detalhadas.

3. **Manutenção**: A inclusão das entidades `Técnico` e `Manutenção` permite rastrear o histórico de manutenções dos sensores, garantindo a confiabilidade dos dados.

4. **Flexibilidade**: A estrutura associativa entre sensores e áreas permite que sensores sejam movidos entre diferentes áreas, mantendo o histórico completo.

5. **Análise Geoespacial**: A inclusão de coordenadas geográficas nas áreas monitoradas permite análises espaciais e visualizações em mapas.

Este modelo expandido atende às necessidades de um sistema de irrigação em escala comercial, permitindo o gerenciamento de múltiplas áreas e sensores, além de fornecer dados para análises avançadas de eficiência e produtividade.