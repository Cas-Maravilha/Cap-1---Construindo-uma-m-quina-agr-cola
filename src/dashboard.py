import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import datetime
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Sistema de Irrigação Inteligente",
    page_icon="💧",
    layout="wide"
)

# Função para conectar ao banco de dados
@st.cache_resource
def get_connection():
    return sqlite3.connect("../db/exemplo_irrigacao.db", check_same_thread=False)

# Função para carregar dados das leituras
@st.cache_data(ttl=60)
def load_leituras(_conn, id_area=None, dias=7):
    query = """
    SELECT l.data_hora, s.tipo_sensor, s.unidade_medida, l.valor, a.nome_area, f.nome as nome_fazenda
    FROM leitura l
    JOIN sensor s ON l.id_sensor = s.id_sensor
    JOIN area_monitorada a ON l.id_area = a.id_area
    JOIN fazenda f ON a.id_fazenda = f.id_fazenda
    WHERE l.data_hora >= datetime('now', ?)
    """
    params = [f'-{dias} days']
    
    if id_area:
        query += " AND l.id_area = ?"
        params.append(id_area)
    
    query += " ORDER BY l.data_hora"
    
    df = pd.read_sql_query(query, _conn, params=params)
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    return df

# Função para carregar dados de irrigação
@st.cache_data(ttl=60)
def load_irrigacoes(_conn, id_area=None, dias=7):
    query = """
    SELECT i.*, a.nome_area, f.nome as nome_fazenda
    FROM irrigacao i
    JOIN area_monitorada a ON i.id_area = a.id_area
    JOIN fazenda f ON a.id_fazenda = f.id_fazenda
    WHERE i.inicio_timestamp >= datetime('now', ?)
    """
    params = [f'-{dias} days']
    
    if id_area:
        query += " AND i.id_area = ?"
        params.append(id_area)
    
    query += " ORDER BY i.inicio_timestamp"
    
    df = pd.read_sql_query(query, _conn, params=params)
    df['inicio_timestamp'] = pd.to_datetime(df['inicio_timestamp'])
    df['fim_timestamp'] = pd.to_datetime(df['fim_timestamp'])
    return df

# Função para carregar dados de alertas
@st.cache_data(ttl=60)
def load_alertas(_conn, id_area=None, dias=7):
    query = """
    SELECT a.*, ar.nome_area, f.nome as nome_fazenda, s.tipo_sensor
    FROM alerta a
    JOIN area_monitorada ar ON a.id_area = ar.id_area
    JOIN fazenda f ON ar.id_fazenda = f.id_fazenda
    JOIN sensor s ON a.id_sensor = s.id_sensor
    WHERE a.timestamp >= datetime('now', ?)
    """
    params = [f'-{dias} days']
    
    if id_area:
        query += " AND a.id_area = ?"
        params.append(id_area)
    
    query += " ORDER BY a.timestamp DESC"
    
    df = pd.read_sql_query(query, _conn, params=params)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Função para carregar lista de fazendas e áreas
@st.cache_data(ttl=300)
def load_fazendas_areas(_conn):
    fazendas = pd.read_sql_query("SELECT id_fazenda, nome FROM fazenda ORDER BY nome", _conn)
    areas = pd.read_sql_query("""
        SELECT a.id_area, a.nome_area, f.nome as nome_fazenda, f.id_fazenda
        FROM area_monitorada a
        JOIN fazenda f ON a.id_fazenda = f.id_fazenda
        ORDER BY f.nome, a.nome_area
    """, _conn)
    return fazendas, areas

# Função para gerar dados simulados se o banco estiver vazio
def gerar_dados_simulados(conn):
    # Verifica se já existem dados
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fazenda")
    count = cursor.fetchone()[0]
    
    if count > 0:
        return False  # Não precisa gerar dados
    
    # Cria dados simulados
    from db_manager_expandido_completo import SistemaIrrigacaoDB
    import random
    
    db = SistemaIrrigacaoDB("../db/exemplo_irrigacao.db")
    
    # Adiciona fazendas
    id_fazenda = db.adicionar_fazenda("Fazenda Modelo", "Latitude: -23.5505, Longitude: -46.6333", 150.5)
    
    # Adiciona áreas
    id_area = db.adicionar_area(id_fazenda, "Horta Orgânica", "Polígono: [(-23.55,-46.63), (-23.55,-46.62), (-23.54,-46.62), (-23.54,-46.63)]")
    
    # Adiciona sensores
    id_sensor_umidade = db.adicionar_sensor("umidade", "DHT22", "%")
    id_sensor_ph = db.adicionar_sensor("ph", "pH-Meter-SEN0161", "pH")
    id_sensor_fosforo = db.adicionar_sensor("fosforo", "NPK-Sensor-v1", "mg/kg")
    id_sensor_potassio = db.adicionar_sensor("potassio", "NPK-Sensor-v1", "mg/kg")
    
    # Associa sensores à área
    db.associar_sensor_area(id_sensor_umidade, id_area)
    db.associar_sensor_area(id_sensor_ph, id_area)
    db.associar_sensor_area(id_sensor_fosforo, id_area)
    db.associar_sensor_area(id_sensor_potassio, id_area)
    
    # Gera leituras para os últimos 7 dias
    now = datetime.datetime.now()
    for i in range(7*24):  # Uma leitura por hora por 7 dias
        data_hora = (now - timedelta(hours=7*24-i)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Simula padrões realistas
        hora = i % 24
        # Umidade diminui durante o dia e aumenta à noite
        umidade = 50 + 20 * np.sin(i/12 * np.pi) + random.uniform(-5, 5)
        umidade = max(20, min(80, umidade))  # Limita entre 20% e 80%
        
        # pH varia pouco
        ph = 6.5 + random.uniform(-0.5, 0.5)
        
        # Fósforo e potássio diminuem gradualmente
        fosforo = max(0.2, 0.8 - i/(7*24) * 0.3 + random.uniform(-0.1, 0.1))
        potassio = max(0.2, 0.7 - i/(7*24) * 0.2 + random.uniform(-0.1, 0.1))
        
        # Registra leituras
        db.adicionar_leitura(id_sensor_umidade, id_area, umidade, data_hora)
        db.adicionar_leitura(id_sensor_ph, id_area, ph, data_hora)
        db.adicionar_leitura(id_sensor_fosforo, id_area, fosforo, data_hora)
        db.adicionar_leitura(id_sensor_potassio, id_area, potassio, data_hora)
        
        # Adiciona irrigação quando umidade está baixa
        if umidade < 30 and random.random() > 0.5:
            inicio = data_hora
            duracao = random.uniform(20, 40)  # 20-40 minutos
            fim = (datetime.datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S") + 
                   timedelta(minutes=duracao)).strftime("%Y-%m-%d %H:%M:%S")
            volume = duracao * 3  # 3 litros por minuto
            
            id_irrigacao = db.adicionar_irrigacao(id_area, "automatico", volume, inicio)
            db.finalizar_irrigacao(id_irrigacao, volume, fim)
        
        # Adiciona alertas ocasionalmente
        if i % 50 == 0:  # Aproximadamente a cada 2 dias
            if umidade < 25:
                db.adicionar_alerta(id_area, id_sensor_umidade, "Umidade Crítica", 
                                   "Umidade abaixo de 25%, verifique o sistema de irrigação", data_hora)
            elif ph < 5.5 or ph > 7.0:
                db.adicionar_alerta(id_area, id_sensor_ph, "pH Inadequado", 
                                   f"pH de {ph:.1f} está fora da faixa ideal (5.5-7.0)", data_hora)
            elif fosforo < 0.4:
                db.adicionar_alerta(id_area, id_sensor_fosforo, "Fósforo Baixo", 
                                   "Nível de fósforo abaixo do recomendado", data_hora)
            elif potassio < 0.4:
                db.adicionar_alerta(id_area, id_sensor_potassio, "Potássio Baixo", 
                                   "Nível de potássio abaixo do recomendado", data_hora)
    
    return True

# Título do dashboard
st.title("💧 Dashboard do Sistema de Irrigação Inteligente")

# Conecta ao banco de dados
conn = get_connection()

# Gera dados simulados se necessário
with st.spinner("Verificando dados..."):
    dados_gerados = gerar_dados_simulados(conn)
    if dados_gerados:
        st.success("Dados simulados gerados com sucesso!")

# Carrega lista de fazendas e áreas
fazendas, areas = load_fazendas_areas(conn)

# Sidebar para filtros
st.sidebar.header("Filtros")

# Seleção de fazenda
fazenda_selecionada = st.sidebar.selectbox(
    "Selecione a Fazenda:",
    options=fazendas['id_fazenda'].tolist(),
    format_func=lambda x: fazendas[fazendas['id_fazenda'] == x]['nome'].iloc[0]
)

# Filtra áreas pela fazenda selecionada
areas_filtradas = areas[areas['id_fazenda'] == fazenda_selecionada]

# Seleção de área
area_selecionada = st.sidebar.selectbox(
    "Selecione a Área:",
    options=areas_filtradas['id_area'].tolist(),
    format_func=lambda x: areas_filtradas[areas_filtradas['id_area'] == x]['nome_area'].iloc[0]
)

# Seleção de período
periodo = st.sidebar.slider(
    "Período de análise (dias):",
    min_value=1,
    max_value=30,
    value=7
)

# Botão para atualizar dados
if st.sidebar.button("Atualizar Dados"):
    st.experimental_rerun()

# Carrega os dados filtrados
with st.spinner("Carregando dados..."):
    df_leituras = load_leituras(conn, area_selecionada, periodo)
    df_irrigacoes = load_irrigacoes(conn, area_selecionada, periodo)
    df_alertas = load_alertas(conn, area_selecionada, periodo)

# Verifica se há dados
if df_leituras.empty:
    st.warning("Não há dados de leituras para o período e área selecionados.")
else:
    # Prepara os dados para visualização
    nome_area = areas_filtradas[areas_filtradas['id_area'] == area_selecionada]['nome_area'].iloc[0]
    nome_fazenda = areas_filtradas[areas_filtradas['id_area'] == area_selecionada]['nome_fazenda'].iloc[0]
    
    st.header(f"Área: {nome_area} - {nome_fazenda}")
    
    # Cria um DataFrame pivotado para facilitar a visualização
    df_pivot = df_leituras.pivot_table(
        index='data_hora', 
        columns='tipo_sensor', 
        values='valor',
        aggfunc='mean'
    ).reset_index()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    # Últimos valores registrados
    ultima_umidade = df_pivot['umidade'].iloc[-1] if 'umidade' in df_pivot else 0
    ultimo_ph = df_pivot['ph'].iloc[-1] if 'ph' in df_pivot else 0
    ultimo_fosforo = df_pivot['fosforo'].iloc[-1] if 'fosforo' in df_pivot else 0
    ultimo_potassio = df_pivot['potassio'].iloc[-1] if 'potassio' in df_pivot else 0
    
    # Status da irrigação
    irrigacao_ativa = False
    for _, row in df_irrigacoes.iterrows():
        if pd.isna(row['fim_timestamp']) or row['fim_timestamp'] > datetime.datetime.now():
            irrigacao_ativa = True
            break
    
    # Alertas ativos
    alertas_ativos = len(df_alertas[df_alertas['resolvido'] == 0])
    
    # Exibe métricas
    col1.metric("Umidade do Solo", f"{ultima_umidade:.1f}%", 
               delta="Normal" if 30 <= ultima_umidade <= 70 else "Crítico")
    
    col2.metric("pH", f"{ultimo_ph:.1f}", 
               delta="Normal" if 5.5 <= ultimo_ph <= 7.0 else "Crítico")
    
    col3.metric("Irrigação", "ATIVA" if irrigacao_ativa else "DESATIVADA")
    
    col4.metric("Alertas Ativos", alertas_ativos, 
               delta="Nenhum" if alertas_ativos == 0 else f"{alertas_ativos} alerta(s)")
    
    # Gráficos
    st.subheader("Monitoramento de Sensores")
    
    # Cria abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["Umidade e Irrigação", "Nutrientes e pH", "Alertas"])
    
    with tab1:
        # Gráfico de umidade com períodos de irrigação
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Adiciona linha de umidade
        if 'umidade' in df_pivot:
            fig.add_trace(
                go.Scatter(
                    x=df_pivot['data_hora'], 
                    y=df_pivot['umidade'],
                    name="Umidade (%)",
                    line=dict(color='blue', width=2)
                ),
                secondary_y=False
            )
        
        # Adiciona barras para irrigação
        for _, row in df_irrigacoes.iterrows():
            fig.add_vrect(
                x0=row['inicio_timestamp'],
                x1=row['fim_timestamp'] if not pd.isna(row['fim_timestamp']) else datetime.datetime.now(),
                fillcolor="rgba(0, 255, 0, 0.2)",
                opacity=0.5,
                layer="below",
                line_width=0,
                annotation_text="Irrigação",
                annotation_position="top left"
            )
        
        # Adiciona linhas de limite
        fig.add_hline(y=30, line_dash="dash", line_color="red", 
                     annotation_text="Limite inferior", annotation_position="bottom right")
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Limite superior", annotation_position="top right")
        
        fig.update_layout(
            title="Umidade do Solo e Períodos de Irrigação",
            xaxis_title="Data/Hora",
            yaxis_title="Umidade (%)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas de irrigação
        if not df_irrigacoes.empty:
            st.subheader("Estatísticas de Irrigação")
            
            total_irrigacoes = len(df_irrigacoes)
            duracao_media = df_irrigacoes['duracao_minutos'].mean()
            volume_total = df_irrigacoes['volume_agua'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Irrigações", total_irrigacoes)
            col2.metric("Duração Média", f"{duracao_media:.1f} min")
            col3.metric("Volume Total", f"{volume_total:.1f} L")
            
            # Tabela de irrigações
            st.dataframe(
                df_irrigacoes[['inicio_timestamp', 'fim_timestamp', 'duracao_minutos', 'volume_agua', 'modo']]
                .rename(columns={
                    'inicio_timestamp': 'Início',
                    'fim_timestamp': 'Fim',
                    'duracao_minutos': 'Duração (min)',
                    'volume_agua': 'Volume (L)',
                    'modo': 'Modo'
                }),
                hide_index=True
            )
    
    with tab2:
        # Gráfico de pH e nutrientes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Adiciona linha de pH
        if 'ph' in df_pivot:
            fig.add_trace(
                go.Scatter(
                    x=df_pivot['data_hora'], 
                    y=df_pivot['ph'],
                    name="pH",
                    line=dict(color='purple', width=2)
                ),
                secondary_y=False
            )
        
        # Adiciona linhas de nutrientes
        if 'fosforo' in df_pivot:
            fig.add_trace(
                go.Scatter(
                    x=df_pivot['data_hora'], 
                    y=df_pivot['fosforo'],
                    name="Fósforo (mg/kg)",
                    line=dict(color='green', width=2)
                ),
                secondary_y=True
            )
        
        if 'potassio' in df_pivot:
            fig.add_trace(
                go.Scatter(
                    x=df_pivot['data_hora'], 
                    y=df_pivot['potassio'],
                    name="Potássio (mg/kg)",
                    line=dict(color='orange', width=2)
                ),
                secondary_y=True
            )
        
        # Adiciona linhas de limite para pH
        fig.add_hline(y=5.5, line_dash="dash", line_color="red", 
                     annotation_text="pH mínimo", annotation_position="bottom right")
        fig.add_hline(y=7.0, line_dash="dash", line_color="red", 
                     annotation_text="pH máximo", annotation_position="top right")
        
        fig.update_layout(
            title="pH e Níveis de Nutrientes",
            xaxis_title="Data/Hora",
            height=500
        )
        
        fig.update_yaxes(title_text="pH", secondary_y=False)
        fig.update_yaxes(title_text="Nutrientes (mg/kg)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas de nutrientes
        if 'fosforo' in df_pivot and 'potassio' in df_pivot:
            st.subheader("Estatísticas de Nutrientes e pH")
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric("pH Médio", f"{df_pivot['ph'].mean():.2f}", 
                       delta="Normal" if 5.5 <= df_pivot['ph'].mean() <= 7.0 else "Fora da faixa")
            
            status_fosforo = "Adequado" if df_pivot['fosforo'].iloc[-1] > 0.5 else "Baixo"
            col2.metric("Fósforo", f"{df_pivot['fosforo'].iloc[-1]:.2f} mg/kg", 
                       delta=status_fosforo)
            
            status_potassio = "Adequado" if df_pivot['potassio'].iloc[-1] > 0.5 else "Baixo"
            col3.metric("Potássio", f"{df_pivot['potassio'].iloc[-1]:.2f} mg/kg", 
                       delta=status_potassio)
    
    with tab3:
        # Alertas
        st.subheader("Alertas Recentes")
        
        if df_alertas.empty:
            st.info("Não há alertas registrados para o período selecionado.")
        else:
            # Gráfico de alertas por tipo
            alertas_por_tipo = df_alertas['tipo_alerta'].value_counts().reset_index()
            alertas_por_tipo.columns = ['Tipo de Alerta', 'Quantidade']
            
            fig = px.bar(
                alertas_por_tipo, 
                x='Tipo de Alerta', 
                y='Quantidade',
                color='Tipo de Alerta',
                title="Alertas por Tipo"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de alertas
            st.dataframe(
                df_alertas[['timestamp', 'tipo_alerta', 'descricao', 'tipo_sensor', 'resolvido']]
                .rename(columns={
                    'timestamp': 'Data/Hora',
                    'tipo_alerta': 'Tipo',
                    'descricao': 'Descrição',
                    'tipo_sensor': 'Sensor',
                    'resolvido': 'Resolvido'
                })
                .assign(Resolvido=lambda x: x['Resolvido'].map({0: 'Não', 1: 'Sim'})),
                hide_index=True
            )

# Seção de simulação
st.sidebar.header("Simulação")
st.sidebar.info("Use esta seção para simular novas leituras e testar o sistema.")

with st.sidebar.expander("Adicionar Leitura Simulada"):
    # Formulário para adicionar leitura simulada
    with st.form("form_leitura"):
        st.write("Nova Leitura")
        
        sensor_tipo = st.selectbox(
            "Tipo de Sensor",
            options=["umidade", "ph", "fosforo", "potassio"]
        )
        
        if sensor_tipo == "umidade":
            valor = st.slider("Umidade (%)", 0.0, 100.0, 50.0)
        elif sensor_tipo == "ph":
            valor = st.slider("pH", 0.0, 14.0, 6.5)
        elif sensor_tipo == "fosforo":
            valor = st.slider("Fósforo (mg/kg)", 0.0, 1.0, 0.6)
        elif sensor_tipo == "potassio":
            valor = st.slider("Potássio (mg/kg)", 0.0, 1.0, 0.6)
        
        submitted = st.form_submit_button("Adicionar Leitura")
        
        if submitted:
            try:
                # Obtém o ID do sensor correspondente
                cursor = conn.cursor()
                cursor.execute("SELECT id_sensor FROM sensor WHERE tipo_sensor = ?", (sensor_tipo,))
                id_sensor = cursor.fetchone()[0]
                
                # Adiciona a leitura
                data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO leitura (id_sensor, id_area, valor, data_hora) VALUES (?, ?, ?, ?)",
                    (id_sensor, area_selecionada, valor, data_hora)
                )
                conn.commit()
                
                st.success(f"Leitura de {sensor_tipo} adicionada com sucesso!")
                
                # Verifica se deve gerar um alerta
                if sensor_tipo == "umidade" and valor < 30:
                    cursor.execute(
                        "INSERT INTO alerta (id_area, id_sensor, timestamp, tipo_alerta, descricao) VALUES (?, ?, ?, ?, ?)",
                        (area_selecionada, id_sensor, data_hora, "Umidade Baixa", "Umidade abaixo do limite recomendado")
                    )
                    conn.commit()
                    st.warning("Alerta de umidade baixa gerado!")
                
                elif sensor_tipo == "ph" and (valor < 5.5 or valor > 7.0):
                    cursor.execute(
                        "INSERT INTO alerta (id_area, id_sensor, timestamp, tipo_alerta, descricao) VALUES (?, ?, ?, ?, ?)",
                        (area_selecionada, id_sensor, data_hora, "pH Inadequado", f"pH de {valor:.1f} está fora da faixa ideal (5.5-7.0)")
                    )
                    conn.commit()
                    st.warning("Alerta de pH inadequado gerado!")
                
                elif sensor_tipo in ["fosforo", "potassio"] and valor < 0.5:
                    cursor.execute(
                        "INSERT INTO alerta (id_area, id_sensor, timestamp, tipo_alerta, descricao) VALUES (?, ?, ?, ?, ?)",
                        (area_selecionada, id_sensor, data_hora, f"{sensor_tipo.capitalize()} Baixo", f"Nível de {sensor_tipo} abaixo do recomendado")
                    )
                    conn.commit()
                    st.warning(f"Alerta de {sensor_tipo} baixo gerado!")
                
                # Verifica se deve iniciar irrigação
                if sensor_tipo == "umidade" and valor < 30:
                    cursor.execute(
                        "INSERT INTO irrigacao (id_area, inicio_timestamp, modo) VALUES (?, ?, ?)",
                        (area_selecionada, data_hora, "automatico")
                    )
                    conn.commit()
                    st.success("Irrigação iniciada automaticamente!")
            
            except Exception as e:
                st.error(f"Erro ao adicionar leitura: {e}")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.caption("Sistema de Irrigação Inteligente © 2023")