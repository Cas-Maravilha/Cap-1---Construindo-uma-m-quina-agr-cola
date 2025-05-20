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