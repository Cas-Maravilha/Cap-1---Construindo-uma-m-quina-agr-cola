import sqlite3
import os

def initialize_database():
    """Inicializa o banco de dados com o schema SQL"""
    db_path = "exemplo_irrigacao.db"
    schema_path = "schema_expandido.sql"
    
    # Verifica se o arquivo schema existe
    if not os.path.exists(schema_path):
        print(f"Erro: Arquivo {schema_path} não encontrado!")
        return False
    
    try:
        # Lê o arquivo schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Conecta ao banco de dados e executa o schema
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        conn.commit()
        
        print(f"Banco de dados {db_path} inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    initialize_database()