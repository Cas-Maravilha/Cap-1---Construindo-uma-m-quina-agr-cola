# Modelo Entidade-Relacionamento (MER) - Sistema de Irrigação Inteligente

## Entidades

### 1. Leituras
Armazena os dados coletados pelos sensores em cada ciclo de leitura.

**Atributos:**
- `id` (PK): Identificador único da leitura
- `timestamp`: Data e hora da leitura
- `umidade`: Percentual de umidade do solo
- `ph`: Valor do pH do solo
- `fosforo`: Nível de fósforo (1 = adequado, 0 = baixo)
- `potassio`: Nível de potássio (1 = adequado, 0 = baixo)
- `irrigacao_ativa`: Status da irrigação (1 = ativa, 0 = desativada)
- `condicao_critica`: Presença de condições críticas (1 = sim, 0 = não)

### 2. Histórico de Irrigação
Registra os períodos em que o sistema de irrigação esteve ativo.

**Atributos:**
- `id` (PK): Identificador único do registro
- `leitura_id` (FK): Referência à leitura que iniciou o ciclo de irrigação
- `inicio_timestamp`: Data e hora de início da irrigação
- `fim_timestamp`: Data e hora de término da irrigação (NULL se ainda estiver ativa)
- `duracao_minutos`: Duração da irrigação em minutos

### 3. Alertas
Registra alertas e condições críticas detectadas pelo sistema.

**Atributos:**
- `id` (PK): Identificador único do alerta
- `leitura_id` (FK): Referência à leitura que gerou o alerta
- `timestamp`: Data e hora do alerta
- `tipo_alerta`: Tipo de alerta (ex: "Umidade baixa", "pH inadequado")
- `descricao`: Descrição detalhada do alerta
- `resolvido`: Status de resolução (1 = resolvido, 0 = não resolvido)

## Relacionamentos

1. **Leitura → Histórico de Irrigação**: Uma leitura pode iniciar um ciclo de irrigação (1:0..1)
2. **Leitura → Alertas**: Uma leitura pode gerar múltiplos alertas (1:N)

## Diagrama ER

```
+-------------+       +---------------------+
|   Leituras  |       | Histórico Irrigação |
+-------------+       +---------------------+
| PK id       |------>| PK id               |
| timestamp   |       | FK leitura_id       |
| umidade     |       | inicio_timestamp    |
| ph          |       | fim_timestamp       |
| fosforo     |       | duracao_minutos     |
| potassio    |       +---------------------+
| irrigacao   |
| condicao    |       +-------------+
+-------------+       |   Alertas   |
       |              +-------------+
       +------------->| PK id       |
                      | FK leitura_id|
                      | timestamp    |
                      | tipo_alerta  |
                      | descricao    |
                      | resolvido    |
                      +-------------+
```

## Justificativa da Estrutura

1. **Normalização**: O modelo está na 3ª Forma Normal, evitando redundância de dados e garantindo integridade.

2. **Separação de Responsabilidades**:
   - A tabela `leituras` armazena apenas os dados brutos dos sensores
   - A tabela `historico_irrigacao` registra os ciclos de irrigação, permitindo análises de duração e frequência
   - A tabela `alertas` centraliza todos os eventos críticos, facilitando o monitoramento

3. **Rastreabilidade**:
   - Cada alerta e ciclo de irrigação está vinculado à leitura que o originou
   - Isso permite correlacionar eventos com as condições do solo no momento

4. **Flexibilidade para Análises**:
   - A estrutura permite consultas complexas como:
     - Tempo médio de irrigação por faixa de umidade
     - Correlação entre pH e frequência de alertas
     - Eficiência da irrigação (quanto tempo leva para a umidade atingir níveis ideais)

5. **Escalabilidade**:
   - O modelo pode ser facilmente expandido para incluir novos sensores ou parâmetros
   - Novas entidades podem ser adicionadas (ex: Zonas de Irrigação, Configurações) sem alterar a estrutura existente

Esta estrutura de dados suporta todos os requisitos do sistema de irrigação inteligente, permitindo não apenas o armazenamento eficiente dos dados, mas também análises avançadas para otimização do uso de água e nutrientes.