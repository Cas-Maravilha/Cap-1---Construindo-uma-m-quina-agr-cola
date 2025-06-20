-- Schema SQL para o Sistema de Irrigação Inteligente Expandido
-- Este script cria todas as tabelas necessárias para o modelo ER expandido

-- Tabela Fazenda
CREATE TABLE IF NOT EXISTS fazenda (
    id_fazenda INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    localizacao TEXT NOT NULL,
    tamanho_hectares REAL NOT NULL
);

-- Tabela Área Monitorada
CREATE TABLE IF NOT EXISTS area_monitorada (
    id_area INTEGER PRIMARY KEY AUTOINCREMENT,
    id_fazenda INTEGER NOT NULL,
    nome_area TEXT NOT NULL,
    coordenadas TEXT NOT NULL,
    FOREIGN KEY (id_fazenda) REFERENCES fazenda (id_fazenda)
);

-- Tabela Sensor
CREATE TABLE IF NOT EXISTS sensor (
    id_sensor INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_sensor TEXT NOT NULL,
    modelo TEXT NOT NULL,
    unidade_medida TEXT NOT NULL
);

-- Tabela associativa Sensor_Area
CREATE TABLE IF NOT EXISTS sensor_area (
    id_sensor_area INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sensor INTEGER NOT NULL,
    id_area INTEGER NOT NULL,
    data_instalacao TEXT NOT NULL,
    data_remocao TEXT,
    FOREIGN KEY (id_sensor) REFERENCES sensor (id_sensor),
    FOREIGN KEY (id_area) REFERENCES area_monitorada (id_area)
);

-- Tabela Técnico
CREATE TABLE IF NOT EXISTS tecnico (
    id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    especialidade TEXT NOT NULL
);

-- Tabela Manutenção
CREATE TABLE IF NOT EXISTS manutencao (
    id_manutencao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sensor INTEGER NOT NULL,
    id_tecnico INTEGER NOT NULL,
    data_manutencao TEXT NOT NULL,
    tipo_manutencao TEXT NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (id_sensor) REFERENCES sensor (id_sensor),
    FOREIGN KEY (id_tecnico) REFERENCES tecnico (id_tecnico)
);

-- Tabela Leitura (expandida a partir do modelo anterior)
CREATE TABLE IF NOT EXISTS leitura (
    id_leitura INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sensor INTEGER NOT NULL,
    id_area INTEGER NOT NULL,
    valor REAL NOT NULL,
    data_hora TEXT NOT NULL,
    FOREIGN KEY (id_sensor) REFERENCES sensor (id_sensor),
    FOREIGN KEY (id_area) REFERENCES area_monitorada (id_area)
);

-- Tabela Irrigação (expandida a partir do historico_irrigacao anterior)
CREATE TABLE IF NOT EXISTS irrigacao (
    id_irrigacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_area INTEGER NOT NULL,
    inicio_timestamp TEXT NOT NULL,
    fim_timestamp TEXT,
    duracao_minutos REAL,
    volume_agua REAL,
    modo TEXT NOT NULL, -- 'automatico' ou 'manual'
    FOREIGN KEY (id_area) REFERENCES area_monitorada (id_area)
);

-- Tabela Alerta (expandida a partir do modelo anterior)
CREATE TABLE IF NOT EXISTS alerta (
    id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_area INTEGER NOT NULL,
    id_sensor INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    tipo_alerta TEXT NOT NULL,
    descricao TEXT NOT NULL,
    resolvido INTEGER DEFAULT 0, -- 0 = não, 1 = sim
    FOREIGN KEY (id_area) REFERENCES area_monitorada (id_area),
    FOREIGN KEY (id_sensor) REFERENCES sensor (id_sensor)
);

-- Visões para compatibilidade com o modelo anterior

-- Visão que simula a tabela 'leituras' do modelo anterior
CREATE VIEW IF NOT EXISTS leituras_compat AS
SELECT 
    l.id_leitura as id,
    l.data_hora as timestamp,
    (SELECT valor FROM leitura WHERE id_sensor = s_fosforo.id_sensor AND id_area = l.id_area AND data_hora = l.data_hora) > 0.5 as fosforo,
    (SELECT valor FROM leitura WHERE id_sensor = s_potassio.id_sensor AND id_area = l.id_area AND data_hora = l.data_hora) > 0.5 as potassio,
    (SELECT valor FROM leitura WHERE id_sensor = s_ph.id_sensor AND id_area = l.id_area AND data_hora = l.data_hora) as ph,
    (SELECT valor FROM leitura WHERE id_sensor = s_umidade.id_sensor AND id_area = l.id_area AND data_hora = l.data_hora) as umidade,
    CASE WHEN EXISTS (
        SELECT 1 FROM irrigacao 
        WHERE id_area = l.id_area 
        AND inicio_timestamp <= l.data_hora 
        AND (fim_timestamp IS NULL OR fim_timestamp >= l.data_hora)
    ) THEN 1 ELSE 0 END as irrigacao_ativa,
    CASE WHEN EXISTS (
        SELECT 1 FROM alerta 
        WHERE id_area = l.id_area 
        AND timestamp = l.data_hora 
        AND resolvido = 0
    ) THEN 1 ELSE 0 END as condicao_critica
FROM 
    leitura l
JOIN 
    sensor s_umidade ON s_umidade.tipo_sensor = 'umidade'
JOIN 
    sensor s_ph ON s_ph.tipo_sensor = 'ph'
JOIN 
    sensor s_fosforo ON s_fosforo.tipo_sensor = 'fosforo'
JOIN 
    sensor s_potassio ON s_potassio.tipo_sensor = 'potassio'
GROUP BY 
    l.id_area, l.data_hora;

-- Visão que simula a tabela 'historico_irrigacao' do modelo anterior
CREATE VIEW IF NOT EXISTS historico_irrigacao_compat AS
SELECT 
    id_irrigacao as id,
    (SELECT id_leitura FROM leitura WHERE id_area = i.id_area AND data_hora <= i.inicio_timestamp ORDER BY data_hora DESC LIMIT 1) as leitura_id,
    inicio_timestamp,
    fim_timestamp,
    duracao_minutos
FROM 
    irrigacao i;

-- Visão que simula a tabela 'alertas' do modelo anterior
CREATE VIEW IF NOT EXISTS alertas_compat AS
SELECT 
    id_alerta as id,
    (SELECT id_leitura FROM leitura WHERE id_area = a.id_area AND data_hora <= a.timestamp ORDER BY data_hora DESC LIMIT 1) as leitura_id,
    timestamp,
    tipo_alerta,
    descricao,
    resolvido
FROM 
    alerta a;

-- Índices para melhorar a performance

-- Índices para a tabela area_monitorada
CREATE INDEX IF NOT EXISTS idx_area_fazenda ON area_monitorada(id_fazenda);

-- Índices para a tabela sensor_area
CREATE INDEX IF NOT EXISTS idx_sensor_area_sensor ON sensor_area(id_sensor);
CREATE INDEX IF NOT EXISTS idx_sensor_area_area ON sensor_area(id_area);
CREATE INDEX IF NOT EXISTS idx_sensor_area_instalacao ON sensor_area(data_instalacao);

-- Índices para a tabela leitura
CREATE INDEX IF NOT EXISTS idx_leitura_sensor ON leitura(id_sensor);
CREATE INDEX IF NOT EXISTS idx_leitura_area ON leitura(id_area);
CREATE INDEX IF NOT EXISTS idx_leitura_data ON leitura(data_hora);

-- Índices para a tabela irrigacao
CREATE INDEX IF NOT EXISTS idx_irrigacao_area ON irrigacao(id_area);
CREATE INDEX IF NOT EXISTS idx_irrigacao_inicio ON irrigacao(inicio_timestamp);

-- Índices para a tabela alerta
CREATE INDEX IF NOT EXISTS idx_alerta_area ON alerta(id_area);
CREATE INDEX IF NOT EXISTS idx_alerta_sensor ON alerta(id_sensor);
CREATE INDEX IF NOT EXISTS idx_alerta_timestamp ON alerta(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerta_resolvido ON alerta(resolvido);