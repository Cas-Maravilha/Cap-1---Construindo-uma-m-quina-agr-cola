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