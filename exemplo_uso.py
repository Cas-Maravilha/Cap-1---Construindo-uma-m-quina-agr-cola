#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso do Sistema de Irrigação Inteligente Expandido
Este script demonstra como utilizar o gerenciador de banco de dados expandido
para gerenciar fazendas, áreas, sensores e leituras.
"""

import datetime
import time
from db_manager_expandido_completo import SistemaIrrigacaoDB

def main():
    """Função principal com exemplos de uso do sistema"""
    print("=== Sistema de Irrigação Inteligente - Exemplo de Uso ===\n")
    
    # Inicializa o banco de dados
    db = SistemaIrrigacaoDB("exemplo_irrigacao.db")
    
    # 1. Cadastro de fazendas
    print("\n--- Cadastro de Fazendas ---")
    id_fazenda1 = db.adicionar_fazenda(
        "Fazenda São João", 
        "Latitude: -22.9035, Longitude: -47.0384", 
        120.5
    )
    print(f"Fazenda 1 criada com ID: {id_fazenda1}")
    
    id_fazenda2 = db.adicionar_fazenda(
        "Sítio Esperança", 
        "Latitude: -23.1256, Longitude: -46.9875", 
        35.8
    )
    print(f"Fazenda 2 criada com ID: {id_fazenda2}")
    
    # Lista as fazendas cadastradas
    fazendas = db.listar_fazendas()
    print("\nFazendas cadastradas:")
    for fazenda in fazendas:
        print(f"  - {fazenda['nome']} ({fazenda['tamanho_hectares']} hectares)")
    
    # 2. Cadastro de áreas monitoradas
    print("\n--- Cadastro de Áreas Monitoradas ---")
    id_area1 = db.adicionar_area(
        id_fazenda1, 
        "Horta Orgânica", 
        "Polígono: [(-22.903,-47.038), (-22.903,-47.037), (-22.902,-47.037), (-22.902,-47.038)]"
    )
    print(f"Área 1 criada com ID: {id_area1}")
    
    id_area2 = db.adicionar_area(
        id_fazenda1, 
        "Pomar de Citros", 
        "Polígono: [(-22.904,-47.039), (-22.904,-47.038), (-22.903,-47.038), (-22.903,-47.039)]"
    )
    print(f"Área 2 criada com ID: {id_area2}")
    
    id_area3 = db.adicionar_area(
        id_fazenda2, 
        "Estufa de Hortaliças", 
        "Polígono: [(-23.125,-46.987), (-23.125,-46.986), (-23.124,-46.986), (-23.124,-46.987)]"
    )
    print(f"Área 3 criada com ID: {id_area3}")
    
    # Lista as áreas por fazenda
    for fazenda in fazendas:
        areas = db.listar_areas(fazenda['id_fazenda'])
        print(f"\nÁreas da {fazenda['nome']}:")
        for area in areas:
            print(f"  - {area['nome_area']}")
    
    # 3. Cadastro de sensores
    print("\n--- Cadastro de Sensores ---")
    sensores = [
        ("umidade", "DHT22", "%"),
        ("ph", "pH-Meter-SEN0161", "pH"),
        ("fosforo", "NPK-Sensor-v1", "mg/kg"),
        ("potassio", "NPK-Sensor-v1", "mg/kg"),
        ("temperatura", "DS18B20", "°C"),
        ("luminosidade", "BH1750", "lux")
    ]
    
    ids_sensores = {}
    for tipo, modelo, unidade in sensores:
        id_sensor = db.adicionar_sensor(tipo, modelo, unidade)
        ids_sensores[tipo] = id_sensor
        print(f"Sensor {tipo} ({modelo}) criado com ID: {id_sensor}")
    
    # 4. Associação de sensores às áreas
    print("\n--- Associação de Sensores às Áreas ---")
    # Associa todos os sensores básicos à Horta Orgânica
    for tipo in ["umidade", "ph", "fosforo", "potassio"]:
        db.associar_sensor_area(ids_sensores[tipo], id_area1)
        print(f"Sensor {tipo} associado à Horta Orgânica")
    
    # Associa sensores específicos ao Pomar de Citros
    for tipo in ["umidade", "ph", "temperatura"]:
        db.associar_sensor_area(ids_sensores[tipo], id_area2)
        print(f"Sensor {tipo} associado ao Pomar de Citros")
    
    # Associa sensores específicos à Estufa
    for tipo in ["umidade", "temperatura", "luminosidade"]:
        db.associar_sensor_area(ids_sensores[tipo], id_area3)
        print(f"Sensor {tipo} associado à Estufa de Hortaliças")
    
    # 5. Cadastro de técnicos
    print("\n--- Cadastro de Técnicos ---")
    id_tecnico1 = db.adicionar_tecnico(
        "Carlos Oliveira", 
        "carlos.oliveira@email.com", 
        "Sensores de Solo"
    )
    print(f"Técnico 1 criado com ID: {id_tecnico1}")
    
    id_tecnico2 = db.adicionar_tecnico(
        "Ana Silva", 
        "ana.silva@email.com", 
        "Sistemas de Irrigação"
    )
    print(f"Técnico 2 criado com ID: {id_tecnico2}")
    
    # 6. Registro de manutenções
    print("\n--- Registro de Manutenções ---")
    data_manutencao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    id_manutencao1 = db.adicionar_manutencao(
        ids_sensores["ph"], 
        id_tecnico1, 
        "Calibração", 
        "Calibração com soluções padrão pH 4.0 e 7.0",
        data_manutencao
    )
    print(f"Manutenção 1 registrada com ID: {id_manutencao1}")
    
    id_manutencao2 = db.adicionar_manutencao(
        ids_sensores["umidade"], 
        id_tecnico2, 
        "Substituição", 
        "Substituição do sensor com defeito",
        data_manutencao
    )
    print(f"Manutenção 2 registrada com ID: {id_manutencao2}")
    
    # 7. Simulação de leituras de sensores
    print("\n--- Simulação de Leituras de Sensores ---")
    # Horta Orgânica - condições normais
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.adicionar_leitura(ids_sensores["umidade"], id_area1, 45.5, data_hora)
    db.adicionar_leitura(ids_sensores["ph"], id_area1, 6.8, data_hora)
    db.adicionar_leitura(ids_sensores["fosforo"], id_area1, 0.8, data_hora)
    db.adicionar_leitura(ids_sensores["potassio"], id_area1, 0.7, data_hora)
    print("Leituras registradas para Horta Orgânica - condições normais")
    
    # Pomar de Citros - solo seco
    db.adicionar_leitura(ids_sensores["umidade"], id_area2, 25.3, data_hora)
    db.adicionar_leitura(ids_sensores["ph"], id_area2, 6.5, data_hora)
    db.adicionar_leitura(ids_sensores["temperatura"], id_area2, 28.2, data_hora)
    print("Leituras registradas para Pomar de Citros - solo seco")
    
    # Estufa - temperatura alta
    db.adicionar_leitura(ids_sensores["umidade"], id_area3, 55.2, data_hora)
    db.adicionar_leitura(ids_sensores["temperatura"], id_area3, 32.5, data_hora)
    db.adicionar_leitura(ids_sensores["luminosidade"], id_area3, 12500, data_hora)
    print("Leituras registradas para Estufa - temperatura alta")
    
    # 8. Ciclos de irrigação
    print("\n--- Ciclos de Irrigação ---")
    # Inicia irrigação no Pomar (solo seco)
    id_irrigacao = db.adicionar_irrigacao(id_area2, "automatico")
    print(f"Irrigação iniciada no Pomar com ID: {id_irrigacao}")
    
    # Simula o tempo de irrigação (5 minutos)
    print("Irrigando o Pomar por 5 minutos (simulado)...")
    fim_timestamp = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    db.finalizar_irrigacao(id_irrigacao, 120.5, fim_timestamp)
    print("Irrigação finalizada")
    
    # 9. Registro de alertas
    print("\n--- Registro de Alertas ---")
    # Alerta de temperatura alta na estufa
    id_alerta1 = db.adicionar_alerta(
        id_area3, 
        ids_sensores["temperatura"], 
        "Temperatura Elevada", 
        "Temperatura acima de 30°C pode prejudicar as hortaliças"
    )
    print(f"Alerta de temperatura registrado com ID: {id_alerta1}")
    
    # Alerta de solo seco no pomar
    id_alerta2 = db.adicionar_alerta(
        id_area2, 
        ids_sensores["umidade"], 
        "Umidade Baixa", 
        "Umidade abaixo de 30% pode estressar as plantas"
    )
    print(f"Alerta de umidade registrado com ID: {id_alerta2}")
    
    # 10. Consulta de dados
    print("\n--- Consulta de Dados ---")
    
    # Consulta leituras recentes da Horta Orgânica
    print("\nLeituras recentes da Horta Orgânica:")
    leituras = db.listar_leituras(id_area=id_area1, limite=10)
    for leitura in leituras:
        print(f"  - {leitura['tipo_sensor']}: {leitura['valor']} {leitura['unidade_medida']} ({leitura['data_hora']})")
    
    # Consulta alertas não resolvidos
    print("\nAlertas não resolvidos:")
    alertas = db.listar_alertas(resolvidos=False)
    for alerta in alertas:
        print(f"  - {alerta['tipo_alerta']} em {alerta['nome_area']}: {alerta['descricao']}")
    
    # Resolve um alerta
    db.resolver_alerta(id_alerta2)
    print(f"\nAlerta de umidade marcado como resolvido")
    
    # Consulta histórico de irrigação
    print("\nHistórico de irrigação:")
    irrigacoes = db.listar_irrigacoes()
    for irrigacao in irrigacoes:
        duracao = irrigacao['duracao_minutos'] if irrigacao['duracao_minutos'] else "Em andamento"
        print(f"  - {irrigacao['nome_area']}: {duracao} minutos, {irrigacao['volume_agua']} litros")
    
    # 11. Teste de compatibilidade com o modelo anterior
    print("\n--- Compatibilidade com Modelo Anterior ---")
    leituras_compat = db.obter_leituras_compat()
    print("\nLeituras (formato compatível):")
    for leitura in leituras_compat:
        print(f"  - ID: {leitura['id']}, Umidade: {leitura['umidade']}%, pH: {leitura['ph']}, Irrigação: {'Ativa' if leitura['irrigacao_ativa'] else 'Desativada'}")
    
    # Fecha a conexão com o banco de dados
    db.fechar()
    print("\nExemplo concluído com sucesso!")

if __name__ == "__main__":
    main()