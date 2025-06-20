# Sistema de Irrigação Inteligente - Modelo Expandido

Este documento descreve a expansão do Sistema de Irrigação Inteligente para um modelo mais completo, adequado para uso em escala comercial em múltiplas fazendas e áreas de cultivo.

## Evolução do Modelo de Dados

O sistema evoluiu de um modelo simples focado em um único conjunto de sensores para um modelo completo que gerencia:

- Múltiplas fazendas
- Diversas áreas monitoradas
- Vários tipos de sensores
- Técnicos responsáveis pela manutenção
- Histórico detalhado de irrigação e alertas

### Comparação entre os Modelos

| Aspecto | Modelo Original | Modelo Expandido |
|---------|----------------|-----------------|
| Escopo | Um único sistema de irrigação | Múltiplas fazendas e áreas |
| Sensores | Fixos (umidade, pH, fósforo, potássio) | Configuráveis e expansíveis |
| Manutenção | Não contemplada | Registro completo de manutenções |
| Rastreabilidade | Básica | Completa (quem, quando, onde) |
| Análise | Limitada a um ponto | Comparativa entre áreas |

## Estrutura do Banco de Dados Expandido

O novo modelo inclui as seguintes entidades:

1. **Fazenda**: Representa a propriedade agrícola
2. **Área Monitorada**: Setores específicos dentro da fazenda
3. **Sensor**: Dispositivos de medição configuráveis
4. **Sensor_Area**: Associação entre sensores e áreas (N:N)
5. **Leitura**: Dados coletados pelos sensores
6. **Técnico**: Profissionais responsáveis pela manutenção
7. **Manutenção**: Registros de intervenções nos sensores
8. **Irrigação**: Ciclos de irrigação realizados
9. **Alerta**: Condições críticas detectadas

## Operações CRUD Implementadas

O sistema implementa operações CRUD (Create, Read, Update, Delete) completas para todas as entidades:

### Fazendas
- Adicionar, consultar, listar, atualizar e excluir fazendas
- Gerenciar informações como nome, localização e tamanho

### Áreas Monitoradas
- Adicionar, consultar, listar, atualizar e excluir áreas
- Associar áreas a fazendas específicas
- Armazenar coordenadas geográficas para análise espacial

### Sensores
- Adicionar, consultar, listar, atualizar e excluir sensores
- Configurar diferentes tipos de sensores e unidades de medida
- Associar e desassociar sensores de áreas específicas

### Leituras
- Registrar leituras de sensores com timestamp
- Consultar histórico de leituras com diversos filtros
- Analisar tendências e padrões nos dados

### Técnicos e Manutenções
- Gerenciar equipe técnica responsável pelos sensores
- Registrar manutenções preventivas e corretivas
- Acompanhar histórico de intervenções por sensor

### Irrigação
- Iniciar e finalizar ciclos de irrigação
- Registrar volume de água utilizado
- Calcular automaticamente a duração da irrigação

### Alertas
- Registrar condições críticas detectadas
- Marcar alertas como resolvidos
- Consultar histórico de alertas por área ou sensor

## Compatibilidade com o Modelo Anterior

Para garantir compatibilidade com aplicações existentes, o sistema inclui visões SQL que simulam as tabelas do modelo anterior:

- `leituras_compat`: Simula a tabela `leituras` original
- `historico_irrigacao_compat`: Simula a tabela `historico_irrigacao` original
- `alertas_compat`: Simula a tabela `alertas` original

Isso permite que aplicações existentes continuem funcionando sem modificações, enquanto novas aplicações podem aproveitar o modelo expandido.

## Justificativa da Estrutura de Dados

A estrutura expandida foi projetada considerando:

1. **Escalabilidade**: Suporte a múltiplas fazendas e áreas
2. **Flexibilidade**: Configuração de diferentes tipos de sensores
3. **Rastreabilidade**: Histórico completo de leituras, manutenções e alertas
4. **Integridade Referencial**: Relacionamentos bem definidos entre entidades
5. **Análise Avançada**: Dados estruturados para permitir análises comparativas

## Como Usar o Sistema Expandido

### Configuração Inicial
1. Execute o script `schema_expandido.sql` para criar as tabelas
2. Use a classe `SistemaIrrigacaoDB` para interagir com o banco de dados

### Fluxo de Trabalho Típico
1. Cadastre fazendas e áreas monitoradas
2. Registre os sensores disponíveis
3. Associe sensores às áreas apropriadas
4. Cadastre técnicos responsáveis pela manutenção
5. Comece a registrar leituras, ciclos de irrigação e alertas

### Exemplo de Código

```python
# Inicializa o banco de dados
db = SistemaIrrigacaoDB()

# Adiciona uma fazenda
id_fazenda = db.adicionar_fazenda("Fazenda Modelo", "Latitude: -23.5505, Longitude: -46.6333", 150.5)

# Adiciona uma área monitorada
id_area = db.adicionar_area(id_fazenda, "Setor A - Hortaliças", "Polígono: [...]")

# Adiciona sensores
id_sensor_umidade = db.adicionar_sensor("umidade", "DHT22", "%")
id_sensor_ph = db.adicionar_sensor("ph", "pH-Meter-SEN0161", "pH")

# Associa sensores à área
db.associar_sensor_area(id_sensor_umidade, id_area)
db.associar_sensor_area(id_sensor_ph, id_area)

# Registra leituras
db.adicionar_leitura(id_sensor_umidade, id_area, 25.5)
db.adicionar_leitura(id_sensor_ph, id_area, 6.8)

# Inicia um ciclo de irrigação
id_irrigacao = db.adicionar_irrigacao(id_area, "automatico")

# Finaliza o ciclo de irrigação
db.finalizar_irrigacao(id_irrigacao, 120.5)
```

## Conclusão

O modelo expandido representa uma evolução significativa do sistema original, transformando-o de um projeto experimental para uma solução robusta de gerenciamento agrícola. A estrutura de dados foi projetada para atender às necessidades de fazendas comerciais, mantendo compatibilidade com o sistema original e permitindo análises avançadas para otimização da irrigação e uso de recursos.