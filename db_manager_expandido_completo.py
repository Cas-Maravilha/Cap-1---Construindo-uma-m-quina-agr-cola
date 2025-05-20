import sqlite3
import os
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

class SistemaIrrigacaoDB:
    """Gerenciador de banco de dados para o Sistema de Irrigação Inteligente Expandido"""
    
    def __init__(self, db_path: str = "irrigacao_expandido.db"):
        """Inicializa a conexão com o banco de dados"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.conectar()
        
        # Verifica se o banco de dados já existe
        db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0
        
        # Se não existir, cria as tabelas
        if not db_exists:
            self.criar_tabelas()
    
    def conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return False
    
    def criar_tabelas(self):
        """Cria as tabelas do banco de dados a partir do arquivo schema_expandido.sql"""
        try:
            # Lê o arquivo SQL
            with open('schema_expandido.sql', 'r') as sql_file:
                sql_script = sql_file.read()
            
            # Executa o script SQL
            self.conn.executescript(sql_script)
            self.conn.commit()
            print("Tabelas criadas com sucesso")
            return True
        except (sqlite3.Error, IOError) as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada")
    
    # OPERAÇÕES CRUD PARA FAZENDA
    
    def adicionar_fazenda(self, nome: str, localizacao: str, tamanho_hectares: float) -> int:
        """Adiciona uma nova fazenda ao banco de dados"""
        try:
            self.cursor.execute(
                "INSERT INTO fazenda (nome, localizacao, tamanho_hectares) VALUES (?, ?, ?)",
                (nome, localizacao, tamanho_hectares)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar fazenda: {e}")
            return -1
    
    def obter_fazenda(self, id_fazenda: int) -> Dict:
        """Obtém os dados de uma fazenda pelo ID"""
        try:
            self.cursor.execute("SELECT * FROM fazenda WHERE id_fazenda = ?", (id_fazenda,))
            fazenda = self.cursor.fetchone()
            return dict(fazenda) if fazenda else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter fazenda: {e}")
            return {}
    
    def listar_fazendas(self) -> List[Dict]:
        """Lista todas as fazendas cadastradas"""
        try:
            self.cursor.execute("SELECT * FROM fazenda ORDER BY nome")
            fazendas = self.cursor.fetchall()
            return [dict(fazenda) for fazenda in fazendas]
        except sqlite3.Error as e:
            print(f"Erro ao listar fazendas: {e}")
            return []
    
    def atualizar_fazenda(self, id_fazenda: int, nome: str = None, 
                         localizacao: str = None, tamanho_hectares: float = None) -> bool:
        """Atualiza os dados de uma fazenda"""
        try:
            # Obtém os dados atuais da fazenda
            fazenda_atual = self.obter_fazenda(id_fazenda)
            if not fazenda_atual:
                print(f"Fazenda com ID {id_fazenda} não encontrada")
                return False
            
            # Atualiza apenas os campos fornecidos
            nome = nome if nome is not None else fazenda_atual['nome']
            localizacao = localizacao if localizacao is not None else fazenda_atual['localizacao']
            tamanho_hectares = tamanho_hectares if tamanho_hectares is not None else fazenda_atual['tamanho_hectares']
            
            self.cursor.execute(
                "UPDATE fazenda SET nome = ?, localizacao = ?, tamanho_hectares = ? WHERE id_fazenda = ?",
                (nome, localizacao, tamanho_hectares, id_fazenda)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar fazenda: {e}")
            return False
    
    def excluir_fazenda(self, id_fazenda: int) -> bool:
        """Exclui uma fazenda do banco de dados"""
        try:
            # Verifica se existem áreas associadas a esta fazenda
            self.cursor.execute("SELECT COUNT(*) FROM area_monitorada WHERE id_fazenda = ?", (id_fazenda,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"Não é possível excluir a fazenda: existem {count} áreas associadas")
                return False
            
            self.cursor.execute("DELETE FROM fazenda WHERE id_fazenda = ?", (id_fazenda,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir fazenda: {e}")
            return False
    # OPERAÇÕES CRUD PARA ÁREA MONITORADA
    
    def adicionar_area(self, id_fazenda: int, nome_area: str, coordenadas: str) -> int:
        """Adiciona uma nova área monitorada ao banco de dados"""
        try:
            self.cursor.execute(
                "INSERT INTO area_monitorada (id_fazenda, nome_area, coordenadas) VALUES (?, ?, ?)",
                (id_fazenda, nome_area, coordenadas)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar área: {e}")
            return -1
    
    def obter_area(self, id_area: int) -> Dict:
        """Obtém os dados de uma área monitorada pelo ID"""
        try:
            self.cursor.execute("SELECT * FROM area_monitorada WHERE id_area = ?", (id_area,))
            area = self.cursor.fetchone()
            return dict(area) if area else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter área: {e}")
            return {}
    
    def listar_areas(self, id_fazenda: Optional[int] = None) -> List[Dict]:
        """Lista todas as áreas monitoradas, opcionalmente filtradas por fazenda"""
        try:
            if id_fazenda:
                self.cursor.execute(
                    "SELECT * FROM area_monitorada WHERE id_fazenda = ? ORDER BY nome_area",
                    (id_fazenda,)
                )
            else:
                self.cursor.execute("SELECT * FROM area_monitorada ORDER BY id_fazenda, nome_area")
            
            areas = self.cursor.fetchall()
            return [dict(area) for area in areas]
        except sqlite3.Error as e:
            print(f"Erro ao listar áreas: {e}")
            return []
    
    def atualizar_area(self, id_area: int, nome_area: str = None, coordenadas: str = None) -> bool:
        """Atualiza os dados de uma área monitorada"""
        try:
            # Obtém os dados atuais da área
            area_atual = self.obter_area(id_area)
            if not area_atual:
                print(f"Área com ID {id_area} não encontrada")
                return False
            
            # Atualiza apenas os campos fornecidos
            nome_area = nome_area if nome_area is not None else area_atual['nome_area']
            coordenadas = coordenadas if coordenadas is not None else area_atual['coordenadas']
            
            self.cursor.execute(
                "UPDATE area_monitorada SET nome_area = ?, coordenadas = ? WHERE id_area = ?",
                (nome_area, coordenadas, id_area)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar área: {e}")
            return False
    
    def excluir_area(self, id_area: int) -> bool:
        """Exclui uma área monitorada do banco de dados"""
        try:
            # Verifica se existem sensores associados a esta área
            self.cursor.execute("SELECT COUNT(*) FROM sensor_area WHERE id_area = ?", (id_area,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"Não é possível excluir a área: existem {count} sensores associados")
                return False
            
            self.cursor.execute("DELETE FROM area_monitorada WHERE id_area = ?", (id_area,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir área: {e}")
            return False
    
    # OPERAÇÕES CRUD PARA SENSOR
    
    def adicionar_sensor(self, tipo_sensor: str, modelo: str, unidade_medida: str) -> int:
        """Adiciona um novo sensor ao banco de dados"""
        try:
            self.cursor.execute(
                "INSERT INTO sensor (tipo_sensor, modelo, unidade_medida) VALUES (?, ?, ?)",
                (tipo_sensor, modelo, unidade_medida)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar sensor: {e}")
            return -1
    
    def obter_sensor(self, id_sensor: int) -> Dict:
        """Obtém os dados de um sensor pelo ID"""
        try:
            self.cursor.execute("SELECT * FROM sensor WHERE id_sensor = ?", (id_sensor,))
            sensor = self.cursor.fetchone()
            return dict(sensor) if sensor else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter sensor: {e}")
            return {}
    
    def listar_sensores(self, tipo_sensor: Optional[str] = None) -> List[Dict]:
        """Lista todos os sensores, opcionalmente filtrados por tipo"""
        try:
            if tipo_sensor:
                self.cursor.execute(
                    "SELECT * FROM sensor WHERE tipo_sensor = ? ORDER BY modelo",
                    (tipo_sensor,)
                )
            else:
                self.cursor.execute("SELECT * FROM sensor ORDER BY tipo_sensor, modelo")
            
            sensores = self.cursor.fetchall()
            return [dict(sensor) for sensor in sensores]
        except sqlite3.Error as e:
            print(f"Erro ao listar sensores: {e}")
            return []
    def atualizar_sensor(self, id_sensor: int, tipo_sensor: str = None, 
                          modelo: str = None, unidade_medida: str = None) -> bool:
        """Atualiza os dados de um sensor"""
        try:
            # Obtém os dados atuais do sensor
            sensor_atual = self.obter_sensor(id_sensor)
            if not sensor_atual:
                print(f"Sensor com ID {id_sensor} não encontrado")
                return False
            
            # Atualiza apenas os campos fornecidos
            tipo_sensor = tipo_sensor if tipo_sensor is not None else sensor_atual['tipo_sensor']
            modelo = modelo if modelo is not None else sensor_atual['modelo']
            unidade_medida = unidade_medida if unidade_medida is not None else sensor_atual['unidade_medida']
            
            self.cursor.execute(
                "UPDATE sensor SET tipo_sensor = ?, modelo = ?, unidade_medida = ? WHERE id_sensor = ?",
                (tipo_sensor, modelo, unidade_medida, id_sensor)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar sensor: {e}")
            return False
    
    def excluir_sensor(self, id_sensor: int) -> bool:
        """Exclui um sensor do banco de dados"""
        try:
            # Verifica se existem associações com áreas
            self.cursor.execute("SELECT COUNT(*) FROM sensor_area WHERE id_sensor = ?", (id_sensor,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"Não é possível excluir o sensor: existem {count} associações com áreas")
                return False
            
            self.cursor.execute("DELETE FROM sensor WHERE id_sensor = ?", (id_sensor,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir sensor: {e}")
            return False
    
    # OPERAÇÕES CRUD PARA ASSOCIAÇÃO SENSOR-ÁREA
    
    def associar_sensor_area(self, id_sensor: int, id_area: int, data_instalacao: str = None) -> int:
        """Associa um sensor a uma área monitorada"""
        try:
            # Se a data de instalação não for fornecida, usa a data atual
            if data_instalacao is None:
                data_instalacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "INSERT INTO sensor_area (id_sensor, id_area, data_instalacao) VALUES (?, ?, ?)",
                (id_sensor, id_area, data_instalacao)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao associar sensor à área: {e}")
            return -1
    
    def desassociar_sensor_area(self, id_sensor_area: int, data_remocao: str = None) -> bool:
        """Marca um sensor como removido de uma área"""
        try:
            # Se a data de remoção não for fornecida, usa a data atual
            if data_remocao is None:
                data_remocao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "UPDATE sensor_area SET data_remocao = ? WHERE id_sensor_area = ?",
                (data_remocao, id_sensor_area)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao desassociar sensor da área: {e}")
            return False
    
    def listar_sensores_area(self, id_area: int, ativos_apenas: bool = True) -> List[Dict]:
        """Lista todos os sensores associados a uma área"""
        try:
            if ativos_apenas:
                self.cursor.execute("""
                    SELECT sa.*, s.tipo_sensor, s.modelo, s.unidade_medida
                    FROM sensor_area sa
                    JOIN sensor s ON sa.id_sensor = s.id_sensor
                    WHERE sa.id_area = ? AND sa.data_remocao IS NULL
                    ORDER BY sa.data_instalacao
                """, (id_area,))
            else:
                self.cursor.execute("""
                    SELECT sa.*, s.tipo_sensor, s.modelo, s.unidade_medida
                    FROM sensor_area sa
                    JOIN sensor s ON sa.id_sensor = s.id_sensor
                    WHERE sa.id_area = ?
                    ORDER BY sa.data_instalacao
                """, (id_area,))
            
            sensores = self.cursor.fetchall()
            return [dict(sensor) for sensor in sensores]
        except sqlite3.Error as e:
            print(f"Erro ao listar sensores da área: {e}")
            return []
    
    def listar_areas_sensor(self, id_sensor: int, ativas_apenas: bool = True) -> List[Dict]:
        """Lista todas as áreas associadas a um sensor"""
        try:
            if ativas_apenas:
                self.cursor.execute("""
                    SELECT sa.*, a.nome_area, a.coordenadas, f.nome as nome_fazenda
                    FROM sensor_area sa
                    JOIN area_monitorada a ON sa.id_area = a.id_area
                    JOIN fazenda f ON a.id_fazenda = f.id_fazenda
                    WHERE sa.id_sensor = ? AND sa.data_remocao IS NULL
                    ORDER BY sa.data_instalacao
                """, (id_sensor,))
            else:
                self.cursor.execute("""
                    SELECT sa.*, a.nome_area, a.coordenadas, f.nome as nome_fazenda
                    FROM sensor_area sa
                    JOIN area_monitorada a ON sa.id_area = a.id_area
                    JOIN fazenda f ON a.id_fazenda = f.id_fazenda
                    WHERE sa.id_sensor = ?
                    ORDER BY sa.data_instalacao
                """, (id_sensor,))
            
            areas = self.cursor.fetchall()
            return [dict(area) for area in areas]
        except sqlite3.Error as e:
            print(f"Erro ao listar áreas do sensor: {e}")
            return []
    # OPERAÇÕES CRUD PARA LEITURAS
    
    def adicionar_leitura(self, id_sensor: int, id_area: int, valor: float, data_hora: str = None) -> int:
        """Adiciona uma nova leitura de sensor ao banco de dados"""
        try:
            # Se a data/hora não for fornecida, usa a data/hora atual
            if data_hora is None:
                data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "INSERT INTO leitura (id_sensor, id_area, valor, data_hora) VALUES (?, ?, ?, ?)",
                (id_sensor, id_area, valor, data_hora)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar leitura: {e}")
            return -1
    
    def obter_leitura(self, id_leitura: int) -> Dict:
        """Obtém os dados de uma leitura pelo ID"""
        try:
            self.cursor.execute("""
                SELECT l.*, s.tipo_sensor, s.unidade_medida, a.nome_area
                FROM leitura l
                JOIN sensor s ON l.id_sensor = s.id_sensor
                JOIN area_monitorada a ON l.id_area = a.id_area
                WHERE l.id_leitura = ?
            """, (id_leitura,))
            leitura = self.cursor.fetchone()
            return dict(leitura) if leitura else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter leitura: {e}")
            return {}
    
    def listar_leituras(self, id_area: Optional[int] = None, id_sensor: Optional[int] = None, 
                       data_inicio: Optional[str] = None, data_fim: Optional[str] = None,
                       limite: int = 100) -> List[Dict]:
        """Lista leituras com diversos filtros"""
        try:
            query = """
                SELECT l.*, s.tipo_sensor, s.unidade_medida, a.nome_area
                FROM leitura l
                JOIN sensor s ON l.id_sensor = s.id_sensor
                JOIN area_monitorada a ON l.id_area = a.id_area
                WHERE 1=1
            """
            params = []
            
            if id_area is not None:
                query += " AND l.id_area = ?"
                params.append(id_area)
            
            if id_sensor is not None:
                query += " AND l.id_sensor = ?"
                params.append(id_sensor)
            
            if data_inicio is not None:
                query += " AND l.data_hora >= ?"
                params.append(data_inicio)
            
            if data_fim is not None:
                query += " AND l.data_hora <= ?"
                params.append(data_fim)
            
            query += " ORDER BY l.data_hora DESC LIMIT ?"
            params.append(limite)
            
            self.cursor.execute(query, params)
            leituras = self.cursor.fetchall()
            return [dict(leitura) for leitura in leituras]
        except sqlite3.Error as e:
            print(f"Erro ao listar leituras: {e}")
            return []
    
    def excluir_leitura(self, id_leitura: int) -> bool:
        """Exclui uma leitura do banco de dados"""
        try:
            self.cursor.execute("DELETE FROM leitura WHERE id_leitura = ?", (id_leitura,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir leitura: {e}")
            return False
    
    # OPERAÇÕES CRUD PARA TÉCNICOS
    
    def adicionar_tecnico(self, nome: str, email: str, especialidade: str) -> int:
        """Adiciona um novo técnico ao banco de dados"""
        try:
            self.cursor.execute(
                "INSERT INTO tecnico (nome, email, especialidade) VALUES (?, ?, ?)",
                (nome, email, especialidade)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar técnico: {e}")
            return -1
    
    def obter_tecnico(self, id_tecnico: int) -> Dict:
        """Obtém os dados de um técnico pelo ID"""
        try:
            self.cursor.execute("SELECT * FROM tecnico WHERE id_tecnico = ?", (id_tecnico,))
            tecnico = self.cursor.fetchone()
            return dict(tecnico) if tecnico else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter técnico: {e}")
            return {}
    
    def listar_tecnicos(self, especialidade: Optional[str] = None) -> List[Dict]:
        """Lista todos os técnicos, opcionalmente filtrados por especialidade"""
        try:
            if especialidade:
                self.cursor.execute(
                    "SELECT * FROM tecnico WHERE especialidade = ? ORDER BY nome",
                    (especialidade,)
                )
            else:
                self.cursor.execute("SELECT * FROM tecnico ORDER BY nome")
            
            tecnicos = self.cursor.fetchall()
            return [dict(tecnico) for tecnico in tecnicos]
        except sqlite3.Error as e:
            print(f"Erro ao listar técnicos: {e}")
            return []
    def atualizar_tecnico(self, id_tecnico: int, nome: str = None, 
                           email: str = None, especialidade: str = None) -> bool:
        """Atualiza os dados de um técnico"""
        try:
            # Obtém os dados atuais do técnico
            tecnico_atual = self.obter_tecnico(id_tecnico)
            if not tecnico_atual:
                print(f"Técnico com ID {id_tecnico} não encontrado")
                return False
            
            # Atualiza apenas os campos fornecidos
            nome = nome if nome is not None else tecnico_atual['nome']
            email = email if email is not None else tecnico_atual['email']
            especialidade = especialidade if especialidade is not None else tecnico_atual['especialidade']
            
            self.cursor.execute(
                "UPDATE tecnico SET nome = ?, email = ?, especialidade = ? WHERE id_tecnico = ?",
                (nome, email, especialidade, id_tecnico)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar técnico: {e}")
            return False
    
    def excluir_tecnico(self, id_tecnico: int) -> bool:
        """Exclui um técnico do banco de dados"""
        try:
            # Verifica se existem manutenções associadas a este técnico
            self.cursor.execute("SELECT COUNT(*) FROM manutencao WHERE id_tecnico = ?", (id_tecnico,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"Não é possível excluir o técnico: existem {count} manutenções associadas")
                return False
            
            self.cursor.execute("DELETE FROM tecnico WHERE id_tecnico = ?", (id_tecnico,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir técnico: {e}")
            return False
    
    # OPERAÇÕES CRUD PARA MANUTENÇÕES
    
    def adicionar_manutencao(self, id_sensor: int, id_tecnico: int, tipo_manutencao: str, 
                            observacoes: str = None, data_manutencao: str = None) -> int:
        """Adiciona um novo registro de manutenção ao banco de dados"""
        try:
            # Se a data não for fornecida, usa a data atual
            if data_manutencao is None:
                data_manutencao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "INSERT INTO manutencao (id_sensor, id_tecnico, data_manutencao, tipo_manutencao, observacoes) VALUES (?, ?, ?, ?, ?)",
                (id_sensor, id_tecnico, data_manutencao, tipo_manutencao, observacoes)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar manutenção: {e}")
            return -1
    
    def obter_manutencao(self, id_manutencao: int) -> Dict:
        """Obtém os dados de uma manutenção pelo ID"""
        try:
            self.cursor.execute("""
                SELECT m.*, s.tipo_sensor, s.modelo, t.nome as nome_tecnico
                FROM manutencao m
                JOIN sensor s ON m.id_sensor = s.id_sensor
                JOIN tecnico t ON m.id_tecnico = t.id_tecnico
                WHERE m.id_manutencao = ?
            """, (id_manutencao,))
            manutencao = self.cursor.fetchone()
            return dict(manutencao) if manutencao else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter manutenção: {e}")
            return {}
    
    def listar_manutencoes(self, id_sensor: Optional[int] = None, id_tecnico: Optional[int] = None,
                          tipo_manutencao: Optional[str] = None, data_inicio: Optional[str] = None,
                          data_fim: Optional[str] = None) -> List[Dict]:
        """Lista manutenções com diversos filtros"""
        try:
            query = """
                SELECT m.*, s.tipo_sensor, s.modelo, t.nome as nome_tecnico
                FROM manutencao m
                JOIN sensor s ON m.id_sensor = s.id_sensor
                JOIN tecnico t ON m.id_tecnico = t.id_tecnico
                WHERE 1=1
            """
            params = []
            
            if id_sensor is not None:
                query += " AND m.id_sensor = ?"
                params.append(id_sensor)
            
            if id_tecnico is not None:
                query += " AND m.id_tecnico = ?"
                params.append(id_tecnico)
            
            if tipo_manutencao is not None:
                query += " AND m.tipo_manutencao = ?"
                params.append(tipo_manutencao)
            
            if data_inicio is not None:
                query += " AND m.data_manutencao >= ?"
                params.append(data_inicio)
            
            if data_fim is not None:
                query += " AND m.data_manutencao <= ?"
                params.append(data_fim)
            
            query += " ORDER BY m.data_manutencao DESC"
            
            self.cursor.execute(query, params)
            manutencoes = self.cursor.fetchall()
            return [dict(manutencao) for manutencao in manutencoes]
        except sqlite3.Error as e:
            print(f"Erro ao listar manutenções: {e}")
            return []
    def atualizar_manutencao(self, id_manutencao: int, tipo_manutencao: str = None,
                               observacoes: str = None) -> bool:
        """Atualiza os dados de uma manutenção"""
        try:
            # Obtém os dados atuais da manutenção
            manutencao_atual = self.obter_manutencao(id_manutencao)
            if not manutencao_atual:
                print(f"Manutenção com ID {id_manutencao} não encontrada")
                return False
            
            # Atualiza apenas os campos fornecidos
            tipo_manutencao = tipo_manutencao if tipo_manutencao is not None else manutencao_atual['tipo_manutencao']
            observacoes = observacoes if observacoes is not None else manutencao_atual['observacoes']
            
            self.cursor.execute(
                "UPDATE manutencao SET tipo_manutencao = ?, observacoes = ? WHERE id_manutencao = ?",
                (tipo_manutencao, observacoes, id_manutencao)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar manutenção: {e}")
            return False
    
    def excluir_manutencao(self, id_manutencao: int) -> bool:
        """Exclui uma manutenção do banco de dados"""
        try:
            self.cursor.execute("DELETE FROM manutencao WHERE id_manutencao = ?", (id_manutencao,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir manutenção: {e}")
            return False
    
    # OPERAÇÕES CRUD PARA IRRIGAÇÃO
    
    def adicionar_irrigacao(self, id_area: int, modo: str, volume_agua: float = None,
                           inicio_timestamp: str = None) -> int:
        """Adiciona um novo ciclo de irrigação ao banco de dados"""
        try:
            # Se a data de início não for fornecida, usa a data atual
            if inicio_timestamp is None:
                inicio_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "INSERT INTO irrigacao (id_area, inicio_timestamp, modo, volume_agua) VALUES (?, ?, ?, ?)",
                (id_area, inicio_timestamp, modo, volume_agua)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar irrigação: {e}")
            return -1
    
    def finalizar_irrigacao(self, id_irrigacao: int, volume_agua: float = None,
                           fim_timestamp: str = None) -> bool:
        """Finaliza um ciclo de irrigação"""
        try:
            # Se a data de fim não for fornecida, usa a data atual
            if fim_timestamp is None:
                fim_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Obtém a data de início para calcular a duração
            self.cursor.execute("SELECT inicio_timestamp FROM irrigacao WHERE id_irrigacao = ?", (id_irrigacao,))
            resultado = self.cursor.fetchone()
            if not resultado:
                print(f"Irrigação com ID {id_irrigacao} não encontrada")
                return False
            
            inicio = datetime.datetime.strptime(resultado[0], "%Y-%m-%d %H:%M:%S")
            fim = datetime.datetime.strptime(fim_timestamp, "%Y-%m-%d %H:%M:%S")
            duracao_minutos = (fim - inicio).total_seconds() / 60
            
            self.cursor.execute(
                "UPDATE irrigacao SET fim_timestamp = ?, duracao_minutos = ?, volume_agua = ? WHERE id_irrigacao = ?",
                (fim_timestamp, duracao_minutos, volume_agua, id_irrigacao)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao finalizar irrigação: {e}")
            return False
    
    def obter_irrigacao(self, id_irrigacao: int) -> Dict:
        """Obtém os dados de um ciclo de irrigação pelo ID"""
        try:
            self.cursor.execute("""
                SELECT i.*, a.nome_area, f.nome as nome_fazenda
                FROM irrigacao i
                JOIN area_monitorada a ON i.id_area = a.id_area
                JOIN fazenda f ON a.id_fazenda = f.id_fazenda
                WHERE i.id_irrigacao = ?
            """, (id_irrigacao,))
            irrigacao = self.cursor.fetchone()
            return dict(irrigacao) if irrigacao else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter irrigação: {e}")
            return {}
    
    def listar_irrigacoes(self, id_area: Optional[int] = None, id_fazenda: Optional[int] = None,
                         data_inicio: Optional[str] = None, data_fim: Optional[str] = None,
                         ativas_apenas: bool = False) -> List[Dict]:
        """Lista ciclos de irrigação com diversos filtros"""
        try:
            query = """
                SELECT i.*, a.nome_area, f.nome as nome_fazenda
                FROM irrigacao i
                JOIN area_monitorada a ON i.id_area = a.id_area
                JOIN fazenda f ON a.id_fazenda = f.id_fazenda
                WHERE 1=1
            """
            params = []
            
            if id_area is not None:
                query += " AND i.id_area = ?"
                params.append(id_area)
            
            if id_fazenda is not None:
                query += " AND a.id_fazenda = ?"
                params.append(id_fazenda)
            
            if data_inicio is not None:
                query += " AND i.inicio_timestamp >= ?"
                params.append(data_inicio)
            
            if data_fim is not None:
                query += " AND i.inicio_timestamp <= ?"
                params.append(data_fim)
            
            if ativas_apenas:
                query += " AND i.fim_timestamp IS NULL"
            
            query += " ORDER BY i.inicio_timestamp DESC"
            
            self.cursor.execute(query, params)
            irrigacoes = self.cursor.fetchall()
            return [dict(irrigacao) for irrigacao in irrigacoes]
        except sqlite3.Error as e:
            print(f"Erro ao listar irrigações: {e}")
            return []
    # OPERAÇÕES CRUD PARA ALERTAS
    
    def adicionar_alerta(self, id_area: int, id_sensor: int, tipo_alerta: str, 
                        descricao: str, timestamp: str = None) -> int:
        """Adiciona um novo alerta ao banco de dados"""
        try:
            # Se o timestamp não for fornecido, usa a data atual
            if timestamp is None:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute(
                "INSERT INTO alerta (id_area, id_sensor, timestamp, tipo_alerta, descricao) VALUES (?, ?, ?, ?, ?)",
                (id_area, id_sensor, timestamp, tipo_alerta, descricao)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar alerta: {e}")
            return -1
    
    def resolver_alerta(self, id_alerta: int) -> bool:
        """Marca um alerta como resolvido"""
        try:
            self.cursor.execute(
                "UPDATE alerta SET resolvido = 1 WHERE id_alerta = ?",
                (id_alerta,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao resolver alerta: {e}")
            return False
    
    def obter_alerta(self, id_alerta: int) -> Dict:
        """Obtém os dados de um alerta pelo ID"""
        try:
            self.cursor.execute("""
                SELECT a.*, s.tipo_sensor, ar.nome_area, f.nome as nome_fazenda
                FROM alerta a
                JOIN sensor s ON a.id_sensor = s.id_sensor
                JOIN area_monitorada ar ON a.id_area = ar.id_area
                JOIN fazenda f ON ar.id_fazenda = f.id_fazenda
                WHERE a.id_alerta = ?
            """, (id_alerta,))
            alerta = self.cursor.fetchone()
            return dict(alerta) if alerta else {}
        except sqlite3.Error as e:
            print(f"Erro ao obter alerta: {e}")
            return {}
    
    def listar_alertas(self, id_area: Optional[int] = None, id_sensor: Optional[int] = None,
                      tipo_alerta: Optional[str] = None, resolvidos: Optional[bool] = None,
                      data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[Dict]:
        """Lista alertas com diversos filtros"""
        try:
            query = """
                SELECT a.*, s.tipo_sensor, ar.nome_area, f.nome as nome_fazenda
                FROM alerta a
                JOIN sensor s ON a.id_sensor = s.id_sensor
                JOIN area_monitorada ar ON a.id_area = ar.id_area
                JOIN fazenda f ON ar.id_fazenda = f.id_fazenda
                WHERE 1=1
            """
            params = []
            
            if id_area is not None:
                query += " AND a.id_area = ?"
                params.append(id_area)
            
            if id_sensor is not None:
                query += " AND a.id_sensor = ?"
                params.append(id_sensor)
            
            if tipo_alerta is not None:
                query += " AND a.tipo_alerta = ?"
                params.append(tipo_alerta)
            
            if resolvidos is not None:
                query += " AND a.resolvido = ?"
                params.append(1 if resolvidos else 0)
            
            if data_inicio is not None:
                query += " AND a.timestamp >= ?"
                params.append(data_inicio)
            
            if data_fim is not None:
                query += " AND a.timestamp <= ?"
                params.append(data_fim)
            
            query += " ORDER BY a.timestamp DESC"
            
            self.cursor.execute(query, params)
            alertas = self.cursor.fetchall()
            return [dict(alerta) for alerta in alertas]
        except sqlite3.Error as e:
            print(f"Erro ao listar alertas: {e}")
            return []
    
    def excluir_alerta(self, id_alerta: int) -> bool:
        """Exclui um alerta do banco de dados"""
        try:
            self.cursor.execute("DELETE FROM alerta WHERE id_alerta = ?", (id_alerta,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao excluir alerta: {e}")
            return False
    
    # MÉTODOS DE COMPATIBILIDADE COM O MODELO ANTERIOR
    
    def obter_leituras_compat(self, limite: int = 10) -> List[Dict]:
        """Obtém leituras no formato do modelo anterior"""
        try:
            self.cursor.execute("SELECT * FROM leituras_compat ORDER BY timestamp DESC LIMIT ?", (limite,))
            leituras = self.cursor.fetchall()
            return [dict(leitura) for leitura in leituras]
        except sqlite3.Error as e:
            print(f"Erro ao obter leituras compatíveis: {e}")
            return []
    
    def obter_historico_irrigacao_compat(self) -> List[Dict]:
        """Obtém histórico de irrigação no formato do modelo anterior"""
        try:
            self.cursor.execute("SELECT * FROM historico_irrigacao_compat ORDER BY inicio_timestamp DESC")
            historico = self.cursor.fetchall()
            return [dict(registro) for registro in historico]
        except sqlite3.Error as e:
            print(f"Erro ao obter histórico de irrigação compatível: {e}")
            return []
    
    def obter_alertas_compat(self) -> List[Dict]:
        """Obtém alertas no formato do modelo anterior"""
        try:
            self.cursor.execute("SELECT * FROM alertas_compat ORDER BY timestamp DESC")
            alertas = self.cursor.fetchall()
            return [dict(alerta) for alerta in alertas]
        except sqlite3.Error as e:
            print(f"Erro ao obter alertas compatíveis: {e}")
            return []

# Exemplo de uso
if __name__ == "__main__":
    db = SistemaIrrigacaoDB()
    
    # Exemplo de criação de dados
    print("Criando dados de exemplo...")
    
    # Adiciona uma fazenda
    id_fazenda = db.adicionar_fazenda("Fazenda Modelo", "Latitude: -23.5505, Longitude: -46.6333", 150.5)
    print(f"Fazenda criada com ID: {id_fazenda}")
    
    # Adiciona uma área monitorada
    id_area = db.adicionar_area(id_fazenda, "Setor A - Hortaliças", "Polígono: [(-23.55,-46.63), (-23.55,-46.62), (-23.54,-46.62), (-23.54,-46.63)]")
    print(f"Área criada com ID: {id_area}")
    
    # Adiciona sensores
    id_sensor_umidade = db.adicionar_sensor("umidade", "DHT22", "%")
    id_sensor_ph = db.adicionar_sensor("ph", "pH-Meter-SEN0161", "pH")
    id_sensor_fosforo = db.adicionar_sensor("fosforo", "NPK-Sensor-v1", "mg/kg")
    id_sensor_potassio = db.adicionar_sensor("potassio", "NPK-Sensor-v1", "mg/kg")
    
    print(f"Sensores criados com IDs: {id_sensor_umidade}, {id_sensor_ph}, {id_sensor_fosforo}, {id_sensor_potassio}")
    
    # Associa sensores à área
    db.associar_sensor_area(id_sensor_umidade, id_area)
    db.associar_sensor_area(id_sensor_ph, id_area)
    db.associar_sensor_area(id_sensor_fosforo, id_area)
    db.associar_sensor_area(id_sensor_potassio, id_area)
    
    # Adiciona um técnico
    id_tecnico = db.adicionar_tecnico("João Silva", "joao.silva@email.com", "Sensores de Solo")
    print(f"Técnico criado com ID: {id_tecnico}")
    
    # Adiciona uma manutenção
    id_manutencao = db.adicionar_manutencao(id_sensor_ph, id_tecnico, "Calibração", "Calibração com soluções padrão pH 4.0 e 7.0")
    print(f"Manutenção registrada com ID: {id_manutencao}")
    
    # Adiciona leituras
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.adicionar_leitura(id_sensor_umidade, id_area, 25.5, data_hora)
    db.adicionar_leitura(id_sensor_ph, id_area, 6.8, data_hora)
    db.adicionar_leitura(id_sensor_fosforo, id_area, 0.8, data_hora)  # 0.8 > 0.5, então é "adequado"
    db.adicionar_leitura(id_sensor_potassio, id_area, 0.3, data_hora)  # 0.3 < 0.5, então é "baixo"
    
    # Adiciona um ciclo de irrigação
    id_irrigacao = db.adicionar_irrigacao(id_area, "automatico")
    print(f"Irrigação iniciada com ID: {id_irrigacao}")
    
    # Finaliza o ciclo de irrigação após 5 minutos (simulado)
    fim_timestamp = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    db.finalizar_irrigacao(id_irrigacao, 120.5, fim_timestamp)
    
    # Adiciona um alerta
    id_alerta = db.adicionar_alerta(id_area, id_sensor_potassio, "Deficiência de Nutrientes", "Nível de potássio abaixo do recomendado")
    print(f"Alerta registrado com ID: {id_alerta}")
    
    # Testa a compatibilidade com o modelo anterior
    print("\nLeituras (formato compatível):")
    leituras_compat = db.obter_leituras_compat()
    for leitura in leituras_compat:
        print(f"ID: {leitura['id']}, Umidade: {leitura['umidade']}%, pH: {leitura['ph']}, Irrigação: {leitura['irrigacao_ativa']}")
    
    # Fecha a conexão
    db.fechar()