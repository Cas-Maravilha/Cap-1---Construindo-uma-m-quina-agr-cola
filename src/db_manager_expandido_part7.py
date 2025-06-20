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