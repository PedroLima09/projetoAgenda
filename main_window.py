import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from modulos.db.requisicoes import db

class BaseToplevel(ctk.CTkToplevel):
    """
    Classe Base para subjanelas. Ela estabelece o padrão geral e conexão com o banco de dados.
    
    Args:
    - master: janela mestre.
    - title (str): título da subjanela.
    - label_text (str): texto do rótulo principal.
    """
    # Classe Pai, para todas as outras subjanelas herdarem o mesmo padrão
    def __init__(self, master, title, label_text, *args, **kwargs):

        # Estabelecendo o banco de dados.
        self.database = db('contatos.db')
        self.database.connect_db()
        self.database.create_table()

        # Definindo a Classe principal.
        super().__init__(master, *args, **kwargs)

        # Configurando o padrão das subjanelas.
        self.geometry("600x400")
        self.title(title)
        self.label = ctk.CTkLabel(self, text=label_text)
        self.label.pack(padx=20, pady=20)
    
    def limpar_entry(self, entry):
        entry.delete(0, tk.END)  

class AddContactToplevel(BaseToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, "Adicionar Contato", "Informações do Contato:", *args, **kwargs)
         # Lista de placeholders para os Entry widgets
        placeholders = ["Nome do Contato", "Email do Contato", "Telefone do Contato"]

        # Criando e posicionando cada Entry
        self.entries = []  # Uma lista para guardar referências aos Entry widgets
        for placeholder in placeholders:
            entry = ctk.CTkEntry(self, placeholder_text=placeholder)
            entry.pack(padx=20, pady=20)
            self.entries.append(entry)

        # Botão de ação (Adicionar)
        button = ctk.CTkButton(self, text="Adicionar", command=self.add_contato)
        button.pack(padx=20, pady=20)

    def add_contato(self):
        """
        Adiciona um novo contato ao banco de dados usando os valores dos Entry widgets.
        """
        # Pegando cada uma das entrys na lista.
        nome = self.entries[0].get()
        email = self.entries[1].get()
        telefone = self.entries[2].get()
        
        try:
            # Verificando se os 3 campos foram preenchidos.
            if nome and email and telefone:
                # Adicionando ao db os 3 valores.
                self.database.add_contact((nome, email, telefone))
                messagebox.showwarning("Cadastro Concluido", "Contato adicionado com sucesso!")
                App.uptade_tree(app)
                # Limpa as entradas após a adição
                for entry in self.entries:
                    self.limpar_entry(entry)
                # Finalizando a Janela.
                self.destroy()  
                
            else:
                # Erro por falta de preenchimento de algum dos campos.
                raise ValueError("Preencha todos os campos corretamente!")       
                
        except Exception as e:
            messagebox.showwarning("Erro no cadastro", str(e))
            # Limpa as entradas 
            for entry in self.entries:
                self.limpar_entry(entry)
                
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        # Estabelecendo o banco de dados.
        self.database = db('contatos.db')
        self.database.connect_db()
        self.database.create_table()

        super().__init__(*args, **kwargs)
        self.geometry("650x450")
        self.maxsize(700, 600)
        self.minsize(650, 450)
        App.title(self, "Agenda")

        search_frame = ctk.CTkFrame(self, fg_color='transparent') # Frame de pesquisa
        search_frame.grid(row=0, column=2, padx=20, pady=20, sticky='EW')

        self.valor_entry = ctk.CTkEntry(search_frame, placeholder_text="Valor") # Entry de pesquisa
        self.valor_entry.grid(row=0, column= 1, padx=20, pady=20, sticky='EW')

        self.search_button = ctk.CTkButton(search_frame, text="🔍", width=10, command=self.filter_contacts) # Botão de ação (Pesquisa)
        self.search_button.grid(row=0, column= 2, sticky='EW', padx=5)

        self.tree = ttk.Treeview(self, columns=("Nome", "Email", "Telefone"), show="headings") # Definindo as Colunas do TreeView
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.grid(row=1, column=0, pady=20, padx=20, columnspan=3, sticky='EW')
        
        self.populate_contacts() # Chamada da função para preencher a treeview

        theme = ctk.CTkOptionMenu(master=self,
                                       values=["Dark", "Light", "Default"],
                                       command= self.theme_selector,
                                       width=30,
                                       height=30) # Menu Seletor de Temas.
        
        theme.grid(row=3, column=0, pady=20, padx=20, sticky='EW')
        theme.set('Tema')

        add_button = ctk.CTkButton(self, text="Novo Contato", command=self.open_add_contact)
        add_button.grid(row=0, column=0, pady=20, padx=20)

        remove_button = ctk.CTkButton(self, text="Remover", command=self.remove_contact)
        remove_button.grid(row=0, column=1, pady=20, padx=20)
        self.toplevel_window = None

    def open_add_contact(self):
        self.add_contact_top_level = AddContactToplevel(self) # Instanciando a Tela de Adicionar Contato.
        
    def populate_contacts(self, search_query=None):
        """
        Preenche a Treeview com contatos pesquisados no banco de dados.
        Se um termo de pesquisa for fornecido, filtra os resultados por esse termo.
        """
        # Limpa o Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Pega todos os contatos ou apenas os filtrados
        if search_query:
            contacts = self.database.search_contact(search_query)
            # Definindo o index inicial como 1, para evitar a exibição da coluna ID, caso tenha alguma
            # Pesquisa a ser realizada.
            start_index = 1
        # Caso a pesquisa seja realizada vazia, entrega todos os contatos do db.    
        else:
            start_index = 0  # Define o inicial como 0, numa busca geral o id já é automaticamente desconsiderado.
            contacts = self.database.search_contact() # Chamando a função buscar contato sem parametros.

        for contact in contacts:  # Selecionando e inserindo as 3 colunas.
            self.tree.insert("", tk.END, values=(contact[start_index], contact[start_index+1], contact[start_index+2]))

    def filter_contacts(self):
        search_query = self.valor_entry.get() # Buscando o resultado do que foi digitado.
        self.populate_contacts(search_query) # Enviando o resultado da busca pra função que pesquisa e preenche o tree-view   

    def remove_contact(self):
        """
        Remove um contato baseado em uma coluna e valor.
        Args:
            valor (str): Recebe a Tupla com os valores a serem removidos.
        """
        selected = self.tree.selection()[0] # Pegando a seleção do usuario, na posição 0.
        item_values = self.tree.item(selected, "values") # Pegando os valores do item selecionado para enviar a função de remover.
        confirm  = messagebox.askyesno("Remover", f"Deseja remover o contato: {item_values}?")
        try:
            if confirm:
                self.database.remove_contact(item_values) # Chamada para função de remover.
                messagebox.showwarning("Removido", f"Contato {item_values[0]} Removido com Sucesso!")
                self.uptade_tree()
            else:
                raise ValueError("Erro ao deletar o Contato.")
            
        except Exception as e:
            return messagebox.showerror("Erro!", {e})     
           
    def uptade_tree(self):
        self.populate_contacts()

    def theme_selector(self, choice):
        """
        param choice: Escolha de tema selecionada pelo usuario.

        returns:
            define pela função set_appearence_mode o tema da interface.
        """
        if choice == 'Dark':
            ctk.set_appearance_mode("dark")
        elif choice == 'Light':
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")

if __name__ == "__main__":
    app = App()
    app.mainloop()