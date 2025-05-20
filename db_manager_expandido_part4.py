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