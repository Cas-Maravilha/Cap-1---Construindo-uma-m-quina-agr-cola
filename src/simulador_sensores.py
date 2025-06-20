import random
import time
import sqlite3
from datetime import datetime

# Simulador de sensores agrícolas para VS Code
# Este programa simula o comportamento do sistema de irrigação inteligente

# Limites para tomada de decisão
LIMITE_UMIDADE_BAIXA = 30.0  # Abaixo disso, solo seco
LIMITE_UMIDADE_ALTA = 70.0   # Acima disso, solo muito úmido
PH_IDEAL_MIN = 5.5           # pH mínimo ideal
PH_IDEAL_MAX = 7.0           # pH máximo ideal

# Configuração do banco de dados
DB_NAME = "../db/irrigacao_dados.db"

def inicializar_banco():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Cria a tabela se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leituras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        fosforo INTEGER,
        potassio INTEGER,
        ph REAL,
        umidade REAL,
        irrigacao_ativa INTEGER,
        condicao_critica INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado.")

def ler_sensores(modo):
    """Simula a leitura dos sensores com base no modo escolhido"""
    if modo == 1:  # Condições ideais
        return True, True, 6.5, 50.0
    elif modo == 2:  # Solo seco
        return True, True, 6.5, 25.0
    elif modo == 3:  # Deficiência de nutrientes
        return False, False, 6.5, 25.0
    elif modo == 4:  # pH inadequado
        return True, True, 8.0, 25.0
    elif modo == 5:  # Valores aleatórios
        return (
            random.choice([True, False]),
            random.choice([True, False]),
            round(random.uniform(4.0, 8.0), 1),
            round(random.uniform(20.0, 80.0), 1)
        )

def exibir_dados(fosforo, potassio, ph, umidade):
    """Exibe os dados dos sensores"""
    print("\n--- Leitura dos Sensores ---")
    print(f"Fósforo: {'Adequado' if fosforo else 'Baixo'}")
    print(f"Potássio: {'Adequado' if potassio else 'Baixo'}")
    print(f"pH: {ph}")
    print(f"Umidade do solo: {umidade}%")

def tomar_decisoes(fosforo, potassio, ph, umidade):
    """Toma decisões com base nos dados dos sensores"""
    necessita_irrigacao = False
    condicao_critica = False
    
    # Verifica se a umidade está baixa
    if umidade < LIMITE_UMIDADE_BAIXA:
        print("ALERTA: Umidade do solo baixa!")
        necessita_irrigacao = True
    
    # Verifica se a umidade está muito alta
    if umidade > LIMITE_UMIDADE_ALTA:
        print("ALERTA: Umidade do solo muito alta!")
        condicao_critica = True
    
    # Verifica se o pH está fora da faixa ideal
    if ph < PH_IDEAL_MIN or ph > PH_IDEAL_MAX:
        print("ALERTA: pH fora da faixa ideal!")
        condicao_critica = True
    
    # Verifica se os níveis de nutrientes estão baixos
    if not fosforo:
        print("ALERTA: Nível de fósforo baixo!")
        condicao_critica = True
    
    if not potassio:
        print("ALERTA: Nível de potássio baixo!")
        condicao_critica = True
    
    # Atualiza o estado da irrigação (relé)
    irrigacao_ativa = necessita_irrigacao and not condicao_critica
    
    # Exibe o status da irrigação
    print(f"Status da irrigação: {'ATIVA' if irrigacao_ativa else 'DESATIVADA'}")
    print(f"Relé (bomba d'água): {'LIGADO' if irrigacao_ativa else 'DESLIGADO'}")
    
    if condicao_critica:
        print("ATENÇÃO: Condições críticas detectadas! Verifique os sensores.")
    
    # Visualização dos LEDs
    print(f"LED Irrigação: {'LIGADO' if irrigacao_ativa else 'DESLIGADO'}")
    print(f"LED Alerta: {'LIGADO' if condicao_critica else 'DESLIGADO'}")
    
    return irrigacao_ativa, condicao_critica

def salvar_dados(fosforo, potassio, ph, umidade, irrigacao_ativa, condicao_critica):
    """Salva os dados no banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO leituras (timestamp, fosforo, potassio, ph, umidade, irrigacao_ativa, condicao_critica)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, int(fosforo), int(potassio), ph, umidade, int(irrigacao_ativa), int(condicao_critica)))
    
    conn.commit()
    conn.close()
    print(f"Dados salvos no banco de dados com ID: {cursor.lastrowid}")
    return cursor.lastrowid

def consultar_dados():
    """Consulta todos os dados no banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leituras')
    dados = cursor.fetchall()
    
    if not dados:
        print("Nenhum dado encontrado no banco de dados.")
    else:
        print("\n--- Dados Armazenados ---")
        print("ID | Timestamp | Fósforo | Potássio | pH | Umidade | Irrigação | Crítico")
        print("-" * 80)
        for dado in dados:
            id, timestamp, fosforo, potassio, ph, umidade, irrigacao, critico = dado
            print(f"{id} | {timestamp} | {'Adequado' if fosforo else 'Baixo'} | {'Adequado' if potassio else 'Baixo'} | {ph} | {umidade}% | {'ATIVA' if irrigacao else 'DESATIVADA'} | {'SIM' if critico else 'NÃO'}")
    
    conn.close()

def atualizar_dado(id, campo, valor):
    """Atualiza um dado específico no banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verifica se o ID existe
    cursor.execute('SELECT * FROM leituras WHERE id = ?', (id,))
    if not cursor.fetchone():
        print(f"Erro: ID {id} não encontrado no banco de dados.")
        conn.close()
        return False
    
    # Campos permitidos para atualização
    campos_permitidos = ['fosforo', 'potassio', 'ph', 'umidade']
    if campo not in campos_permitidos:
        print(f"Erro: Campo '{campo}' não permitido para atualização.")
        print(f"Campos permitidos: {', '.join(campos_permitidos)}")
        conn.close()
        return False
    
    # Atualiza o campo
    cursor.execute(f'UPDATE leituras SET {campo} = ? WHERE id = ?', (valor, id))
    conn.commit()
    conn.close()
    print(f"Registro {id} atualizado com sucesso: {campo} = {valor}")
    return True

def excluir_dado(id):
    """Exclui um registro do banco de dados"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verifica se o ID existe
    cursor.execute('SELECT * FROM leituras WHERE id = ?', (id,))
    if not cursor.fetchone():
        print(f"Erro: ID {id} não encontrado no banco de dados.")
        conn.close()
        return False
    
    # Exclui o registro
    cursor.execute('DELETE FROM leituras WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    print(f"Registro {id} excluído com sucesso.")
    return True

def menu_banco_dados():
    """Menu para operações CRUD no banco de dados"""
    while True:
        print("\n--- Menu do Banco de Dados ---")
        print("1. Consultar todos os registros")
        print("2. Atualizar um registro")
        print("3. Excluir um registro")
        print("4. Voltar ao menu principal")
        
        try:
            opcao = int(input("Opção: "))
        except ValueError:
            print("Por favor, digite um número válido.")
            continue
        
        if opcao == 1:
            consultar_dados()
        elif opcao == 2:
            try:
                id = int(input("ID do registro a atualizar: "))
                print("Campos disponíveis: fosforo, potassio, ph, umidade")
                campo = input("Nome do campo: ").lower()
                
                if campo in ['fosforo', 'potassio']:
                    valor_texto = input(f"Novo valor para {campo} (adequado/baixo): ").lower()
                    valor = 1 if valor_texto == 'adequado' else 0
                elif campo in ['ph', 'umidade']:
                    valor = float(input(f"Novo valor para {campo}: "))
                else:
                    print("Campo inválido.")
                    continue
                
                atualizar_dado(id, campo, valor)
            except ValueError:
                print("Erro: Valor inválido.")
        elif opcao == 3:
            try:
                id = int(input("ID do registro a excluir: "))
                excluir_dado(id)
            except ValueError:
                print("Erro: ID inválido.")
        elif opcao == 4:
            break
        else:
            print("Opção inválida. Tente novamente.")

def main():
    print("Sistema de Irrigação Inteligente - Simulador")
    print("----------------------------------------")
    print("Este programa simula o funcionamento do sistema de irrigação")
    print("com diferentes cenários de sensores.\n")
    
    # Inicializa o banco de dados
    inicializar_banco()
    
    opcao = 0
    
    while opcao != 7:
        print("\nMenu Principal:")
        print("1. Condições ideais")
        print("2. Solo seco")
        print("3. Deficiência de nutrientes")
        print("4. pH inadequado")
        print("5. Valores aleatórios")
        print("6. Operações no banco de dados")
        print("7. Sair")
        
        try:
            opcao = int(input("Opção: "))
        except ValueError:
            print("Por favor, digite um número válido.")
            continue
        
        if 1 <= opcao <= 5:
            print("\n\n======= INICIANDO SIMULAÇÃO =======")
            
            # Simula 3 ciclos de leitura
            for i in range(3):
                print(f"\n--- Ciclo {i+1} ---")
                fosforo, potassio, ph, umidade = ler_sensores(opcao)
                exibir_dados(fosforo, potassio, ph, umidade)
                irrigacao_ativa, condicao_critica = tomar_decisoes(fosforo, potassio, ph, umidade)
                
                # Pergunta se deseja salvar os dados
                salvar = input("\nDeseja salvar estes dados no banco de dados? (s/n): ").lower()
                if salvar == 's':
                    salvar_dados(fosforo, potassio, ph, umidade, irrigacao_ativa, condicao_critica)
                
                # Aguarda 2 segundos entre os ciclos
                if i < 2:
                    print("\nAguardando próxima leitura...")
                    time.sleep(2)
            
            print("\n======= FIM DA SIMULAÇÃO =======")
        elif opcao == 6:
            menu_banco_dados()
        elif opcao != 7:
            print("Opção inválida. Tente novamente.")
    
    print("Encerrando simulador...")

if __name__ == "__main__":
    main()