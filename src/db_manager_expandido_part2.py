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