import sqlite3
import serial
import re
import time
import argparse
from datetime import datetime

# Configurações do banco de dados
DB_NAME = "../db/irrigacao_dados.db"

# Expressões regulares para extrair dados do monitor serial
RE_UMIDADE = r"Umidade do solo: (\d+\.\d+)%"
RE_PH = r"pH: (\d+\.\d+)"
RE_FOSFORO = r"Fósforo: (Adequado|Baixo)"
RE_POTASSIO = r"Potássio: (Adequado|Baixo)"
RE_IRRIGACAO = r"Status da irrigação: (ATIVA|DESATIVADA)"
RE_CONDICAO = r"ATENÇÃO: Condições críticas detectadas!"

class BancoDadosIrrigacao:
    def __init__(self, db_name=DB_NAME):
        """Inicializa a conexão com o banco de dados"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.conectar()
        self.criar_tabelas()
    
    def conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Conexão estabelecida com {self.db_name}")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
    
    def criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem"""
        try:
            # Tabela de leituras (principal)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leituras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                umidade REAL,
                ph REAL,
                fosforo INTEGER,  -- 1 = adequado, 0 = baixo
                potassio INTEGER, -- 1 = adequado, 0 = baixo
                irrigacao_ativa INTEGER, -- 1 = ativa, 0 = desativada
                condicao_critica INTEGER -- 1 = sim, 0 = não
            )
            ''')
            
            # Tabela de histórico de irrigação
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_irrigacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leitura_id INTEGER,
                inicio_timestamp TEXT,
                fim_timestamp TEXT,
                duracao_minutos REAL,
                FOREIGN KEY (leitura_id) REFERENCES leituras (id)
            )
            ''')
            
            # Tabela de alertas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leitura_id INTEGER,
                timestamp TEXT,
                tipo_alerta TEXT,
                descricao TEXT,
                resolvido INTEGER DEFAULT 0, -- 0 = não, 1 = sim
                FOREIGN KEY (leitura_id) REFERENCES leituras (id)
            )
            ''')
            
            self.conn.commit()
            print("Tabelas criadas/verificadas com sucesso")
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
    
    def inserir_leitura(self, umidade, ph, fosforo, potassio, irrigacao_ativa, condicao_critica):
        """Insere uma nova leitura no banco de dados"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Converte valores de texto para inteiros
            fosforo_int = 1 if fosforo == "Adequado" else 0
            potassio_int = 1 if potassio == "Adequado" else 0
            irrigacao_int = 1 if irrigacao_ativa == "ATIVA" else 0
            
            self.cursor.execute('''
            INSERT INTO leituras (timestamp, umidade, ph, fosforo, potassio, irrigacao_ativa, condicao_critica)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, umidade, ph, fosforo_int, potassio_int, irrigacao_int, condicao_critica))
            
            leitura_id = self.cursor.lastrowid
            self.conn.commit()
            print(f"Leitura inserida com ID: {leitura_id}")
            
            # Verifica se deve registrar um alerta
            if condicao_critica:
                self.registrar_alerta(leitura_id, "Condição crítica", "Verificar sensores")
            
            # Verifica se deve registrar início/fim de irrigação
            self.verificar_status_irrigacao(leitura_id, irrigacao_ativa)
            
            return leitura_id
        except sqlite3.Error as e:
            print(f"Erro ao inserir leitura: {e}")
            return None
    
    def registrar_alerta(self, leitura_id, tipo_alerta, descricao):
        """Registra um alerta no banco de dados"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
            INSERT INTO alertas (leitura_id, timestamp, tipo_alerta, descricao)
            VALUES (?, ?, ?, ?)
            ''', (leitura_id, timestamp, tipo_alerta, descricao))
            
            self.conn.commit()
            print(f"Alerta registrado para leitura ID: {leitura_id}")
        except sqlite3.Error as e:
            print(f"Erro ao registrar alerta: {e}")
    
    def verificar_status_irrigacao(self, leitura_id, status_irrigacao):
        """Verifica mudanças no status de irrigação e registra no histórico"""
        try:
            # Obtém o status anterior da irrigação
            self.cursor.execute('''
            SELECT irrigacao_ativa FROM leituras 
            WHERE id < ? ORDER BY id DESC LIMIT 1
            ''', (leitura_id,))
            
            resultado = self.cursor.fetchone()
            
            if resultado is None:
                # Primeira leitura, não há histórico anterior
                return
            
            status_anterior = "ATIVA" if resultado[0] == 1 else "DESATIVADA"
            
            # Se houve mudança de status
            if status_anterior != status_irrigacao:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if status_irrigacao == "ATIVA":
                    # Irrigação foi ativada
                    self.cursor.execute('''
                    INSERT INTO historico_irrigacao (leitura_id, inicio_timestamp)
                    VALUES (?, ?)
                    ''', (leitura_id, timestamp))
                else:
                    # Irrigação foi desativada
                    self.cursor.execute('''
                    SELECT id, inicio_timestamp FROM historico_irrigacao
                    WHERE fim_timestamp IS NULL
                    ORDER BY id DESC LIMIT 1
                    ''')
                    
                    ultimo_registro = self.cursor.fetchone()
                    
                    if ultimo_registro:
                        historico_id, inicio = ultimo_registro
                        
                        # Calcula a duração em minutos
                        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
                        fim_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        duracao = (fim_dt - inicio_dt).total_seconds() / 60
                        
                        self.cursor.execute('''
                        UPDATE historico_irrigacao
                        SET fim_timestamp = ?, duracao_minutos = ?
                        WHERE id = ?
                        ''', (timestamp, duracao, historico_id))
                
                self.conn.commit()
                print(f"Histórico de irrigação atualizado: {status_anterior} -> {status_irrigacao}")
        except sqlite3.Error as e:
            print(f"Erro ao verificar status de irrigação: {e}")
    
    def consultar_leituras(self, limite=10):
        """Consulta as últimas leituras do banco de dados"""
        try:
            self.cursor.execute('''
            SELECT id, timestamp, umidade, ph, 
                   CASE WHEN fosforo = 1 THEN 'Adequado' ELSE 'Baixo' END as fosforo,
                   CASE WHEN potassio = 1 THEN 'Adequado' ELSE 'Baixo' END as potassio,
                   CASE WHEN irrigacao_ativa = 1 THEN 'ATIVA' ELSE 'DESATIVADA' END as irrigacao,
                   CASE WHEN condicao_critica = 1 THEN 'SIM' ELSE 'NÃO' END as condicao_critica
            FROM leituras
            ORDER BY id DESC
            LIMIT ?
            ''', (limite,))
            
            leituras = self.cursor.fetchall()
            
            if not leituras:
                print("Nenhuma leitura encontrada")
            else:
                print("\n=== Últimas Leituras ===")
                print("ID | Timestamp | Umidade | pH | Fósforo | Potássio | Irrigação | Crítico")
                print("-" * 80)
                for leitura in leituras:
                    print(f"{leitura[0]} | {leitura[1]} | {leitura[2]}% | {leitura[3]} | {leitura[4]} | {leitura[5]} | {leitura[6]} | {leitura[7]}")
            
            return leituras
        except sqlite3.Error as e:
            print(f"Erro ao consultar leituras: {e}")
            return []
    
    def atualizar_leitura(self, leitura_id, campo, valor):
        """Atualiza um campo específico de uma leitura"""
        try:
            # Verifica se o ID existe
            self.cursor.execute('SELECT * FROM leituras WHERE id = ?', (leitura_id,))
            if not self.cursor.fetchone():
                print(f"Erro: ID {leitura_id} não encontrado no banco de dados.")
                return False
            
            # Campos permitidos para atualização
            campos_permitidos = ['umidade', 'ph', 'fosforo', 'potassio']
            if campo not in campos_permitidos:
                print(f"Erro: Campo '{campo}' não permitido para atualização.")
                print(f"Campos permitidos: {', '.join(campos_permitidos)}")
                return False
            
            # Converte valores de texto para inteiros quando necessário
            if campo in ['fosforo', 'potassio'] and isinstance(valor, str):
                valor = 1 if valor.lower() == 'adequado' else 0
            
            # Atualiza o campo
            self.cursor.execute(f'UPDATE leituras SET {campo} = ? WHERE id = ?', (valor, leitura_id))
            self.conn.commit()
            print(f"Registro {leitura_id} atualizado com sucesso: {campo} = {valor}")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar leitura: {e}")
            return False
    
    def excluir_leitura(self, leitura_id):
        """Exclui uma leitura do banco de dados"""
        try:
            # Verifica se o ID existe
            self.cursor.execute('SELECT * FROM leituras WHERE id = ?', (leitura_id,))
            if not self.cursor.fetchone():
                print(f"Erro: ID {leitura_id} não encontrado no banco de dados.")
                return False
            
            # Exclui registros relacionados primeiro (integridade referencial)
            self.cursor.execute('DELETE FROM alertas WHERE leitura_id = ?', (leitura_id,))
            self.cursor.execute('DELETE FROM historico_irrigacao WHERE leitura_id = ?', (leitura_id,))
            
            # Exclui a leitura
            self.cursor.execute('DELETE FROM leituras WHERE id = ?', (leitura_id,))
            self.conn.commit()
            print(f"Registro {leitura_id} excluído com sucesso.")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir leitura: {e}")
            return False
    
    def consultar_alertas(self):
        """Consulta os alertas registrados"""
        try:
            self.cursor.execute('''
            SELECT a.id, a.timestamp, a.tipo_alerta, a.descricao, 
                   CASE WHEN a.resolvido = 1 THEN 'Sim' ELSE 'Não' END as resolvido,
                   l.umidade, l.ph
            FROM alertas a
            JOIN leituras l ON a.leitura_id = l.id
            ORDER BY a.id DESC
            ''')
            
            alertas = self.cursor.fetchall()
            
            if not alertas:
                print("Nenhum alerta encontrado")
            else:
                print("\n=== Alertas Registrados ===")
                print("ID | Timestamp | Tipo | Descrição | Resolvido | Umidade | pH")
                print("-" * 80)
                for alerta in alertas:
                    print(f"{alerta[0]} | {alerta[1]} | {alerta[2]} | {alerta[3]} | {alerta[4]} | {alerta[5]}% | {alerta[6]}")
            
            return alertas
        except sqlite3.Error as e:
            print(f"Erro ao consultar alertas: {e}")
            return []
    
    def consultar_historico_irrigacao(self):
        """Consulta o histórico de irrigação"""
        try:
            self.cursor.execute('''
            SELECT h.id, h.inicio_timestamp, h.fim_timestamp, h.duracao_minutos,
                   l.umidade, l.ph
            FROM historico_irrigacao h
            JOIN leituras l ON h.leitura_id = l.id
            ORDER BY h.id DESC
            ''')
            
            historico = self.cursor.fetchall()
            
            if not historico:
                print("Nenhum registro de irrigação encontrado")
            else:
                print("\n=== Histórico de Irrigação ===")
                print("ID | Início | Fim | Duração (min) | Umidade | pH")
                print("-" * 80)
                for reg in historico:
                    fim = reg[2] if reg[2] else "Em andamento"
                    duracao = f"{reg[3]:.1f}" if reg[3] else "-"
                    print(f"{reg[0]} | {reg[1]} | {fim} | {duracao} | {reg[4]}% | {reg[5]}")
            
            return historico
        except sqlite3.Error as e:
            print(f"Erro ao consultar histórico de irrigação: {e}")
            return []
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada")

def processar_linha_serial(linha, db):
    """Processa uma linha do monitor serial e extrai os dados"""
    # Dicionário para armazenar os dados extraídos
    dados = {
        'umidade': None,
        'ph': None,
        'fosforo': None,
        'potassio': None,
        'irrigacao_ativa': None,
        'condicao_critica': 0  # Default: sem condição crítica
    }
    
    # Extrai os dados usando expressões regulares
    match_umidade = re.search(RE_UMIDADE, linha)
    if match_umidade:
        dados['umidade'] = float(match_umidade.group(1))
    
    match_ph = re.search(RE_PH, linha)
    if match_ph:
        dados['ph'] = float(match_ph.group(1))
    
    match_fosforo = re.search(RE_FOSFORO, linha)
    if match_fosforo:
        dados['fosforo'] = match_fosforo.group(1)
    
    match_potassio = re.search(RE_POTASSIO, linha)
    if match_potassio:
        dados['potassio'] = match_potassio.group(1)
    
    match_irrigacao = re.search(RE_IRRIGACAO, linha)
    if match_irrigacao:
        dados['irrigacao_ativa'] = match_irrigacao.group(1)
    
    # Verifica se há condição crítica
    if re.search(RE_CONDICAO, linha):
        dados['condicao_critica'] = 1
    
    # Verifica se temos dados suficientes para inserir no banco
    if (dados['umidade'] is not None and 
        dados['ph'] is not None and 
        dados['fosforo'] is not None and 
        dados['potassio'] is not None and 
        dados['irrigacao_ativa'] is not None):
        
        # Insere os dados no banco
        db.inserir_leitura(
            dados['umidade'], 
            dados['ph'], 
            dados['fosforo'], 
            dados['potassio'], 
            dados['irrigacao_ativa'], 
            dados['condicao_critica']
        )
        return True
    
    return False

def ler_serial(porta, baudrate, db):
    """Lê dados da porta serial e os processa"""
    try:
        # Abre a porta serial
        ser = serial.Serial(porta, baudrate, timeout=1)
        print(f"Conectado à porta serial {porta} com baudrate {baudrate}")
        
        buffer = ""
        leituras_completas = 0
        
        while True:
            # Lê uma linha da porta serial
            try:
                linha = ser.readline().decode('utf-8').strip()
                if linha:
                    print(f"Serial: {linha}")
                    buffer += linha + "\n"
                    
                    # Verifica se temos uma leitura completa
                    if "Status da irrigação:" in linha:
                        if processar_linha_serial(buffer, db):
                            leituras_completas += 1
                            print(f"Leitura completa processada: {leituras_completas}")
                        buffer = ""
            except UnicodeDecodeError:
                print("Erro ao decodificar dados da serial")
            
            time.sleep(0.1)
    
    except serial.SerialException as e:
        print(f"Erro ao abrir porta serial: {e}")
    except KeyboardInterrupt:
        print("\nLeitura serial interrompida pelo usuário")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Porta serial fechada")

def simular_dados(db, num_leituras=5, intervalo=2):
    """Simula dados para teste do banco de dados"""
    import random
    
    print(f"Simulando {num_leituras} leituras com intervalo de {intervalo} segundos")
    
    for i in range(num_leituras):
        # Gera valores aleatórios
        umidade = round(random.uniform(20.0, 80.0), 1)
        ph = round(random.uniform(4.0, 8.0), 1)
        fosforo = "Adequado" if random.random() > 0.3 else "Baixo"
        potassio = "Adequado" if random.random() > 0.3 else "Baixo"
        irrigacao = "ATIVA" if umidade < 30.0 and fosforo == "Adequado" and potassio == "Adequado" else "DESATIVADA"
        condicao_critica = 1 if (umidade > 70.0 or ph < 5.5 or ph > 7.0 or fosforo == "Baixo" or potassio == "Baixo") else 0
        
        # Exibe os valores simulados
        print(f"\n--- Simulação {i+1}/{num_leituras} ---")
        print(f"Umidade do solo: {umidade}%")
        print(f"pH: {ph}")
        print(f"Fósforo: {fosforo}")
        print(f"Potássio: {potassio}")
        print(f"Status da irrigação: {irrigacao}")
        if condicao_critica:
            print("ATENÇÃO: Condições críticas detectadas! Verifique os sensores.")
        
        # Insere no banco de dados
        db.inserir_leitura(umidade, ph, fosforo, potassio, irrigacao, condicao_critica)
        
        # Aguarda o intervalo
        if i < num_leituras - 1:
            time.sleep(intervalo)

def menu_crud(db):
    """Menu para operações CRUD no banco de dados"""
    while True:
        print("\n=== Menu do Banco de Dados ===")
        print("1. Consultar últimas leituras")
        print("2. Consultar alertas")
        print("3. Consultar histórico de irrigação")
        print("4. Atualizar uma leitura")
        print("5. Excluir uma leitura")
        print("6. Simular novas leituras")
        print("7. Voltar/Sair")
        
        try:
            opcao = int(input("Opção: "))
        except ValueError:
            print("Por favor, digite um número válido.")
            continue
        
        if opcao == 1:
            try:
                limite = int(input("Número de leituras a exibir: "))
                db.consultar_leituras(limite)
            except ValueError:
                print("Valor inválido. Usando limite padrão.")
                db.consultar_leituras()
        
        elif opcao == 2:
            db.consultar_alertas()
        
        elif opcao == 3:
            db.consultar_historico_irrigacao()
        
        elif opcao == 4:
            try:
                leitura_id = int(input("ID da leitura a atualizar: "))
                print("Campos disponíveis: umidade, ph, fosforo, potassio")
                campo = input("Nome do campo: ").lower()
                
                if campo in ['fosforo', 'potassio']:
                    valor_texto = input(f"Novo valor para {campo} (adequado/baixo): ").lower()
                    valor = "Adequado" if valor_texto == 'adequado' else "Baixo"
                elif campo in ['umidade', 'ph']:
                    valor = float(input(f"Novo valor para {campo}: "))
                else:
                    print("Campo inválido.")
                    continue
                
                db.atualizar_leitura(leitura_id, campo, valor)
            except ValueError:
                print("Erro: Valor inválido.")
        
        elif opcao == 5:
            try:
                leitura_id = int(input("ID da leitura a excluir: "))
                confirmacao = input(f"Tem certeza que deseja excluir a leitura {leitura_id}? (s/n): ").lower()
                if confirmacao == 's':
                    db.excluir_leitura(leitura_id)
            except ValueError:
                print("Erro: ID inválido.")
        
        elif opcao == 6:
            try:
                num_leituras = int(input("Número de leituras a simular: "))
                intervalo = int(input("Intervalo entre leituras (segundos): "))
                simular_dados(db, num_leituras, intervalo)
            except ValueError:
                print("Valores inválidos. Usando configuração padrão.")
                simular_dados(db)
        
        elif opcao == 7:
            break
        
        else:
            print("Opção inválida. Tente novamente.")

def main():
    parser = argparse.ArgumentParser(description='Captura dados do monitor serial do ESP32 e armazena em banco de dados SQL')
    parser.add_argument('--porta', help='Porta serial do ESP32 (ex: COM3, /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=115200, help='Taxa de transmissão (padrão: 115200)')
    parser.add_argument('--simular', action='store_true', help='Simular dados em vez de ler da porta serial')
    parser.add_argument('--db', default=DB_NAME, help=f'Nome do banco de dados (padrão: {DB_NAME})')
    
    args = parser.parse_args()
    
    print("=== Sistema de Armazenamento de Dados de Irrigação ===")
    
    # Inicializa o banco de dados
    db = BancoDadosIrrigacao(args.db)
    
    try:
        if args.simular:
            # Modo de simulação
            print("Modo de simulação ativado")
            simular_dados(db)
            menu_crud(db)
        elif args.porta:
            # Modo de leitura serial
            print(f"Iniciando leitura da porta serial {args.porta}")
            print("Pressione Ctrl+C para interromper a leitura")
            ler_serial(args.porta, args.baudrate, db)
        else:
            # Modo interativo
            print("Nenhuma porta serial especificada. Entrando no modo interativo.")
            menu_crud(db)
    
    finally:
        # Fecha a conexão com o banco de dados
        db.fechar()

if __name__ == "__main__":
    main()