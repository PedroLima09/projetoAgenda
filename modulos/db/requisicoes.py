import sqlite3 as sql


class db:
    def __init__(self, db):
        """
        param db: Recebe o Banco de Dados.
        """
        self.db = db
        self.conection = None 

    def create_table(self):
        """Cria a tabela 'contatos' se ela não existir."""
        cursor = self.conection.cursor()
        

        # Criar a tabela se ela não existir 
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id       INTEGER PRIMARY KEY,
            nome     TEXT,
            email    TEXT,
            telefone TEXT
        );
        ''')

    def execute_query(self, query, parametros=None):
        """
        Execute uma consulta SQL.

        Args:
            query (str): A consulta SQL a ser executada.
            parametros (tuple, opcional): Uma tupla contendo os parâmetros da consulta.

        Returns:
            list: Retorna o resultado da consulta se for uma operação SELECT.
        """
        cursor = self.conection.cursor()

        try: 
            if parametros:
                cursor.execute(query, parametros) 
            else:
                cursor.execute(query)
            

            # Se a operação for uma seleção, retorne os resultados
            if query.startswith("SELECT"):
                return cursor.fetchall()
            
            self.conection.commit() 

        except sql.OperationalError as e:
            return f"Erro Operacional: {e}"
        except sql.IntegrityError as e:
            return f"Erro de integridade: {e}"
        except Exception as e:
            return f"Erro inesperado: {e}"
        finally:
            cursor.close()

    def connect_db(self):
        """Conecta ao banco de dados SQLite e define a conexão como self.conection."""
        try:
            self.conection = sql.connect(self.db)
            return self.conection
        except Exception as e:
            print(f"Erro ao conectar: {e}")

    def desconect_db(self):
        """Desconecta do banco de dados SQLite."""
        if self.conection: 
            self.conection.close()
        else:
            print(f"Sem conexões para encerrar.")

    def add_contact(self, valores):
        """
        Adiciona um novo contato à tabela.

        Args:
            valores (tuple): Uma tupla contendo os valores para (nome, email, telefone).
        """
        
        if valores[2].isdigit():
            if len(valores[2]) >= 11: # Verificando se tem os 11 digitos no telefone.
                if '@' in valores[1]: # Verificando se tem @ no email. 
                    query = "INSERT INTO contatos (nome, email, telefone) VALUES (?, ?, ?)" 
                    self.execute_query(query, valores)
                else:
                    raise ValueError('Digite um email valido. EX: nome@email.com')    
            else:
                raise ValueError('Verifique o formato do numero. EX: 31989992030')
        else:
            raise ValueError('Digite um numero de telefone valido.')
    def remove_contact(self, valor):
        """
        Remove um contato baseado em uma coluna e valor.

        Args:
            valor (str): Recebe uma tupla dos valores que vão ser removidos.
        """
        query = "DELETE FROM contatos WHERE nome = ? AND email = ? AND telefone = ?"
        self.execute_query(query, valor)

    def search_contact(self, valor=None):
        """
        Busca um contato baseado em valor inserido que pode estar presente em qualquer coluna.

        Args:
            valor (str): Chave de Busca

        Returns:
            Se o parametro for declarado: 
                list: Uma lista de tuplas contendo os resultados da busca.
            Se não:
                list: Uma lista de tuplas com todos os resultados do banco de dados.    
        """
        if valor:
            query = "SELECT * FROM contatos WHERE nome LIKE ? OR email LIKE ? OR telefone LIKE ?"
            search_value = '%' + valor + '%'  # Adicionando os wildcards para pesquisa
            return self.execute_query(query, (search_value, search_value, search_value))
        # Caso não receba parametros, retorna todos os contatos registrados.
        else:
            query = "SELECT nome, email, telefone FROM contatos;"
            return self.execute_query(query)

     
        
