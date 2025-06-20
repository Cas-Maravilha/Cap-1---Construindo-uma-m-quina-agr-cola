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
            with open('../db/schema_expandido.sql', 'r') as sql_file:
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