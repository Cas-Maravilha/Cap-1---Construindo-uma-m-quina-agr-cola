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