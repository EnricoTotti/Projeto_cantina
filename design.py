import customtkinter as ctk
from CTkListbox import *
from PIL import Image
from CTkMessagebox import CTkMessagebox
import mysql.connector
from datetime import datetime

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='cantina'
)

#funções de banco de dados
def carregar_produtos():
    global lista_box, cod_produtos

    cod_produtos = {} #limpar dicionario quando for recarregar
    lista_box.delete(0, 'end') #limpa a lista toda, do primeiro (0) até o ultimo (end)

    query = conexao.cursor()

    query.execute('SELECT * from produto where status = 1')

    resultado = query.fetchall()

    for i, linha in enumerate(resultado): #enumerate para falar o indice da lista que fica armazenada no i
        codigo = linha[0] #carrega o código
        nome = linha[1] 
        preco = linha[2]

        lista_box.insert('END', f"#{codigo} {nome} R$ {preco:.2f}".replace(".", ","))
        cod_produtos[i] = codigo #adiciona o código do produto no indice certo da lista

def remover_produto():
    selecionado = lista_box.curselection() #pega apenas o indice do elemento da lista selecionada

    if not selecionado: #if caso a variavel selecionado, nao contenha nada dentro dela ou seja, um produto nao foi selecionado
        if selecionado == 0:
            pass
        else:
            CTkMessagebox(title="Erro", message="Selecione um produto para adicionar a venda!", icon="warning")
            return


    produto_cod = cod_produtos[selecionado] #o produto cod pega exatamente o codigo do produto do bd utilizando o indice que foi salvo na hora de carregar os produtos

    
    query = conexao.cursor()
    query.execute(f"SELECT COUNT(*) FROM `itens_venda` WHERE cod_produto = {produto_cod} AND status = 1")
    quantidade_linhas = query.fetchone()[0]

    if quantidade_linhas != 0:
        query = conexao.cursor()
        sql = 'UPDATE produto SET status= 0 WHERE cod_produto = %s'
        query.execute(sql, (produto_cod,))
        conexao.commit()
    else:
        query = conexao.cursor()
        sql = 'DELETE FROM produto WHERE cod_produto = %s'
        query.execute(sql, (produto_cod,))
        conexao.commit()

    CTkMessagebox(title="Sucesso", message="Produto removido com sucesso!", icon="check")

    
    # Atualiza a lista após remover
    carregar_produtos()

    


def botao_adicionar_compra():

    global cod_produtos_venda

    selecionado = lista_box.curselection()


    if not selecionado:
        if selecionado == 0:
            pass
        else:
            CTkMessagebox(title="Erro", message="Selecione um produto para adicionar a venda!", icon="warning")
            return
    
    
    produto_cod = cod_produtos[selecionado]

    try:
        global cod_produtos_venda

        query = conexao.cursor()
        sql = 'select * FROM produto WHERE cod_produto = %s'
        query.execute(sql, (produto_cod,))

        resultado = query.fetchall()


        produto = resultado[0]
        
        codigo = produto[0]
        nome = produto[1]
        preco = produto[2]
        qtde = int(lb_quantidade.cget("text"))

        if codigo in cod_produtos_venda:
            CTkMessagebox(title="Erro", message="Este produto já está adicionado! se quiser adicioná-lo, remova-o da venda.", icon="warning")
            return

        cod_produtos_venda.append(codigo)
        
        adicionar_item_venda(nome, preco, qtde, codigo)

        CTkMessagebox(title="Sucesso", message="Produto adicionado com sucesso!", icon="check")


        

    except Exception as e: #caso aconteça algum erro
        CTkMessagebox(title="Erro", message=f"Erro ao adicionar o produto: {e}", icon="cancel")


def adicionar_item_venda(nome, preco, quantidade, codigo):
    global valor_total, frame_selecionado, produtos_venda #vvariavel para saber qual o frame que estã selecionado
    

    frame_item = ctk.CTkFrame(scroll_frame_venda, width=945, height=60, fg_color="#333333")
    frame_item.pack(pady=5)
    frame_item.pack_propagate(False)

    texto = f"#{codigo} {nome}    R$ {preco:.2f}".replace(".", ",") + f"    Quantidade: {quantidade}"
    label = ctk.CTkLabel(frame_item, text=texto, font=("Verdana", 20), anchor="w")
    label.pack(fill="both", expand=True, padx=10)

    valor_item = preco * quantidade

    valor_total.append(valor_item)

    
    produtos_venda[codigo] = {"quantidade": quantidade, "valor_unico": valor_item, "cod_produto": codigo}


    calcular_valor_total()


    def clique(e=None, t=texto):
        global frame_selecionado

        if frame_selecionado is not None: #se ja existe um frame selecionado, ele mudará para cor antiga
            frame_selecionado.configure(fg_color="#333333")

        # troca a cor do novo frame selecionado e armazena no frame selecionado
        frame_item.configure(fg_color="#1f6aa5")
        frame_selecionado = frame_item

        mudar_valor_unitario(t)
        
        

    # vincula o clique ao frame
    frame_item.bind("<Button-1>", clique) #button 1 é o evento de clique do mouse esquerdo
    label.bind("<Button-1>", clique)  # também no label

def remover_item_venda():
    global frame_selecionado, cod_produtos_venda, produtos_venda, valor_total

    if frame_selecionado is None:
        CTkMessagebox(title="Erro", message="Selecione um item da venda para remover.", icon="warning")
        return

    texto = frame_selecionado.winfo_children()[0].cget("text") #pega o widget filho do frame, ou seja, a label
    partes = texto.split()
                                # 0        1            2      3          4          5
    # exemplo split como está: ['#2', 'Refrigerante', 'R$', '4,00', 'Quantidade:', '1']

    
    try:
        codigo = int(partes[0][1:])  # remove o "#" e transforma em int
        if codigo in produtos_venda:
            quantidade = produtos_venda[codigo]["quantidade"]
            preco = float(partes[3].replace("R$", "").replace(",", "."))
            valor = preco * quantidade
            valor_total.remove(valor)

            print(valor_total)

            del produtos_venda[codigo]
            cod_produtos_venda.remove(codigo)
            print(produtos_venda)

    except Exception as e:
        print(f"Erro ao remover produto: {e}")

    frame_selecionado.destroy()
    frame_selecionado = None
    calcular_valor_total()
    
    
def finalizar_venda():

    global frame_selecionado

    total_valor = float(lb_preco_total.cget('text')[3:].replace(",", ".")) #formatação do texto para float e retirada da virgula e R$
    forma_pagamento = cb_forma_pagamento.get()
    cod_venda = 0

    if not produtos_venda:
        CTkMessagebox(title="Erro", message="Adicione um item antes de finalizar uma venda!", icon="warning")
        return

    query = conexao.cursor()
    sql = 'INSERT INTO `venda`( `valor_total`, `forma_pagamento`, status) VALUES (%s, %s, 1);'
    valores = (total_valor, forma_pagamento)
    query.execute(sql, valores)
    conexao.commit()

    cod_venda = query.lastrowid

    finalizar_item_venda(cod_venda)
    

    #mensagem que adição deu certo
    CTkMessagebox(title="Sucesso", message="Venda finalizada com sucesso!", icon="check")


    frame_selecionado = None

    for widget in scroll_frame_venda.winfo_children():
        if widget.winfo_exists():
            widget.destroy()
        
    lb_preco_total.configure(text="R$ 0,00")
    lb_preco_unitario.configure(text="R$ 0,00")
    produtos_venda.clear()
    cod_produtos_venda.clear()
    valor_total.clear()
    
    

def finalizar_item_venda(codigo_venda):
    
    for item in produtos_venda:
        qtde = produtos_venda[item]["quantidade"]
        valor_unico = produtos_venda[item]["valor_unico"]
        cod_produto = produtos_venda[item]["cod_produto"]
        

        query = conexao.cursor()
        sql = 'INSERT INTO `itens_venda`(`qtde`, `valor_unico`, `cod_produto`, `cod_venda`, status) VALUES (%s, %s, %s, %s, 1)'
        valores = (qtde, valor_unico, cod_produto, codigo_venda)
        query.execute(sql, valores)
        conexao.commit()

def resetar_bd():

    resposta = CTkMessagebox(title="Confirmação", message="Tem certeza que deseja resetar o banco de dados? Todas as informações serão perdidas.", icon="warning", option_1="Sim", option_2="Não")

    if resposta.get() != "Sim":
        return  # Se não confirmar, cancela a função


    query = conexao.cursor()    
    query.execute('DELETE FROM `itens_venda`')
    conexao.commit()

    query = conexao.cursor()    
    query.execute('DELETE FROM `produto`')
    conexao.commit()

    query = conexao.cursor()    
    query.execute('DELETE FROM `venda`')
    conexao.commit()

    CTkMessagebox(title="Sucesso", message="Seu banco de dados foi resetado!", icon="check")

    lb_preco_total.configure(text="R$ 0,00")
    lb_preco_unitario.configure(text="R$ 0,00")
    produtos_venda.clear()
    cod_produtos_venda.clear()
    valor_total.clear()
    for widget in scroll_frame_venda.winfo_children():
        widget.destroy()

    carregar_produtos()




#funçoes para abrir coisas, entre outras
def abrir_janela_addproduto():

    def adicionar_produto():

        nome = campo_nome.get()
        preco = campo_preco.get()

        
        if not nome or not preco:
            CTkMessagebox(title="Erro", message="Por favor, preencha todos os campos.", icon="warning")
            return

        try:
            preco = float(preco.replace(',', '.'))

            query = conexao.cursor()
            sql = 'INSERT INTO produto (nome, preco, status) VALUES (%s, %s, 1)'
            valores = (nome, preco)
            query.execute(sql, valores)
            conexao.commit()

            #mensagem que adição deu certo
            CTkMessagebox(title="Sucesso", message="Produto adicionado com sucesso!", icon="check")
            

            carregar_produtos()

            janela_addproduto.destroy()

        except ValueError:
            CTkMessagebox(title="Erro", message="O preço precisa ser um numero válido!", icon="cancel")

        except Exception as error: 
            CTkMessagebox(title="Erro", message=f"Ocorreu um erro!\nerro: {error}", icon="cancel")




    largura_janela = 400
    altura_janela = 320

    janela_addproduto = ctk.CTkToplevel(app)
    janela_addproduto.title("Adicionar produto")
    janela_addproduto.resizable(False, False) #nao deixa aumentar o tamanho da tela
    janela_addproduto.overrideredirect(True)

    # pega a altura e largura da tela
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()

    # Calculo de posição centralizada
    pos_x = (largura_tela // 2) - (largura_janela // 2)
    pos_y = (altura_tela // 2) - (altura_janela // 2)

    # Define tamanho e posição da nova janela
    janela_addproduto.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    
    janela_addproduto.grab_set() #serve para não interagir com a janela principal até essa ser fechada
    

    label = ctk.CTkLabel(janela_addproduto, text="Adicionar produto", font=('Verdana', 21))
    label.pack(pady=20)

    lb_nome = ctk.CTkLabel(janela_addproduto, text="Nome", font=('Verdana', 17))
    lb_nome.pack()
    campo_nome = ctk.CTkEntry(janela_addproduto, width=300)
    campo_nome.pack(pady=10)

    lb_preco = ctk.CTkLabel(janela_addproduto, text="Preço (R$)", font=('Verdana', 17))
    lb_preco.pack()
    campo_preco = ctk.CTkEntry(janela_addproduto, width=300)
    campo_preco.pack(pady=10)

    bt_adicionar = ctk.CTkButton(janela_addproduto, text='ADICIONAR', width=300, height=50, command=adicionar_produto)
    bt_adicionar.pack(pady=30)

    bt_fechar = ctk.CTkButton(janela_addproduto, text='X', command=janela_addproduto.destroy, width=30, height=30)
    bt_fechar.place(x=10, y=10)

def aumentar_estoque():
    quantidade_atual = int(lb_quantidade.cget("text"))  # pega o valor atual do texto da label e converte pra int
    nova_quantidade = quantidade_atual + 1

    lb_quantidade.configure(text=str(nova_quantidade))  # atualiza o texto da label

def diminuir_estoque():
    quantidade_atual = int(lb_quantidade.cget("text"))  # pega o valor atual do texto da label e converte pra int

    if quantidade_atual == 1:
        CTkMessagebox(title="Aviso", message="É preciso ter pelo menos um", icon="warning")
        return
        

    nova_quantidade = quantidade_atual - 1

    lb_quantidade.configure(text=str(nova_quantidade))  # atualiza o texto da label




def mudar_valor_unitario(texto):
    
    partes = texto.split()

    try:
        preco = 0.0
        quantidade = 1

        if "R$" in partes:
            idx_preco = partes.index("R$")
            preco = float(partes[idx_preco + 1].replace(",", "."))

        if "Quantidade:" in partes:
            idx_qtd = partes.index("Quantidade:")
            quantidade = int(partes[idx_qtd + 1])

        total = preco * quantidade
        lb_preco_unitario.configure(text=f"R$ {total:,.2f}".replace(".", ","))

    except Exception as e:
        print(f"Erro ao processar valor unitário: {e}")

def calcular_valor_total():

    global valor_total

    total = sum(valor_total)

    lb_preco_total.configure(text=f"R$ {total:.2f}".replace(".", ","))


def abrir_janela_consulta():

    def consultar_venda():

        for widget in scroll_frame_relatorio.winfo_children():
            if widget.winfo_exists():
                widget.destroy()

        ano = cb_ano.get()

        query = conexao.cursor()

        query.execute(f"SELECT venda.cod_venda, venda.valor_total, venda.data_cadastro, SUM(itens_venda.qtde) AS total_itens, venda.forma_pagamento FROM venda JOIN itens_venda ON venda.cod_venda = itens_venda.cod_venda WHERE venda.data_cadastro >= '{ano}-01-01' GROUP BY venda.cod_venda")

        resultado = query.fetchall()

        for i, linha in enumerate(resultado): #enumerate para falar o indice da lista que fica armazenada no i
            codigo = linha[0] #carrega o código
            valor_total = linha[1] 
            data_cadastro = linha[2].strftime('%d/%m/%Y')
            qtde = linha[3]
            forma_pagamento = linha[4]

            frame_item = ctk.CTkFrame(scroll_frame_relatorio, width=1420, height=60, fg_color="#333333")
            frame_item.pack(pady=5)
            frame_item.pack_propagate(False)

            texto = f"#{codigo} Valor Total: R$:{valor_total}    Data da venda: {data_cadastro}  Total de itens: {qtde} Forma de pagamento: {forma_pagamento}"
            label = ctk.CTkLabel(frame_item, text=texto, font=("Verdana", 20), anchor="w")
            label.pack(fill="both", expand=True, padx=10)

            

            

    largura_janela = 1500
    altura_janela = 800

    janela_consulta = ctk.CTkToplevel(app)
    janela_consulta.title("Consultas")
    janela_consulta.resizable(False, False) #nao deixa aumentar o tamanho da tela
    janela_consulta.overrideredirect(True)

    # pega a altura e largura da tela
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()

    # Calculo de posição centralizada
    pos_x = (largura_tela // 2) - (largura_janela // 2)
    pos_y = (altura_tela // 2) - (altura_janela // 2)

    # Define tamanho e posição da nova janela
    janela_consulta.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    
    janela_consulta.grab_set() #serve para não interagir com a janela principal até essa ser fechada

    bt_fechar = ctk.CTkButton(janela_consulta, text='X', command=janela_consulta.destroy, width=30, height=30)
    bt_fechar.place(x=10, y=10)

    lb_consulta = ctk.CTkLabel(janela_consulta, text='RELATÓRIO DE VENDAS', font=('Verdana', 21))
    lb_consulta.pack(pady=10)

    ano_atual = datetime.now().year
    anos = [str(ano) for ano in range(2020, ano_atual + 1)]

    cb_ano = ctk.CTkComboBox(janela_consulta, width=205, height=30, values=anos, state='readonly', font=('Verdana', 24), justify='center')
    cb_ano.set(str(ano_atual))
    cb_ano.place(x=1285, y=10)

    bt_consultar = ctk.CTkButton(janela_consulta, width=150, height=30, text='GERAR RELATÓRIO', font=('Verdana', 20), command=consultar_venda)
    bt_consultar.place(x=1070, y=10)

    scroll_frame_relatorio  = ctk.CTkScrollableFrame(janela_consulta, width=1460, height=730)
    scroll_frame_relatorio.pack()





#algumas variaveis globais

cod_produtos = {}
cod_produtos_venda = []
produtos_venda = {}
texto_item_venda = {}
indice_venda = 0
valor_total = []
frame_selecionado = None


#aparencia do app

modo = 'dark'

def mudar_aparencia():
    global modo
    if modo == 'dark':
        modo = 'light'
    else:
        modo = 'dark'
    
    ctk.set_appearance_mode(modo)


#criação app
app =   ctk.CTk()
app.title('Sistema de login')
app.attributes("-fullscreen", True)



#criação de imagem
img_lixeira = ctk.CTkImage(
    dark_image=Image.open("lixeira.png"),  # mesmo para tema escuro e claro
    light_image=Image.open("lixeira.png"),
    size=(32, 32)  # ajuste conforme necessário
)

img_modo = ctk.CTkImage(
    dark_image=Image.open("modo-escuro.png"),  # mesmo para tema escuro e claro
    light_image=Image.open("modo-escuro.png"),
    size=(32, 32)  # ajuste conforme necessário
)



#criação do layout de botoes,  frame e labels

#botao sair
bt_sair = ctk.CTkButton(app, text='X', command=exit, width=50, height=50)
bt_sair.place(x=20, y=20)



#conteudo frame geral
frame_geral = ctk.CTkFrame(app, width=1500, height=900, border_width=3, border_color='#1f6aa5')
frame_geral.place(x=20, y=85)
frame_geral.pack_propagate(False)

bt_reset = ctk.CTkButton(app, width=200, height=60, text="RESETAR", command=resetar_bd, font=('Verdana', 21))
bt_reset.place(x=20, y=1000)

frame_lb_caixa = ctk.CTkFrame(frame_geral, width=1460, height=50, fg_color='#1f6aa5')
frame_lb_caixa.place(x=20, y=20)
frame_lb_caixa.propagate(False)

lb_caixa = ctk.CTkLabel(frame_lb_caixa, font=('Verdana', 30, 'bold'), text='CAIXA', pady=10)
lb_caixa.pack()




frame_valor_unitario = ctk.CTkFrame(frame_geral, width=450, height=200)
frame_valor_unitario.place(x=20, y=90)
frame_valor_unitario.pack_propagate(False)

frame_lb_valor_unitario = ctk.CTkFrame(frame_valor_unitario, width=430, height=40, fg_color='#1f6aa5')
frame_lb_valor_unitario.pack(pady=10)
frame_lb_valor_unitario.pack_propagate(False)

lb_valor_unitario = ctk.CTkLabel(frame_lb_valor_unitario, font=('Verdana', 20, 'bold'), text='VALOR', pady=5)
lb_valor_unitario.pack(pady=10)

lb_preco_unitario = ctk.CTkLabel(frame_valor_unitario, font=('Verdana', 30, 'bold'), text='R$ 0,00', pady=5)
lb_preco_unitario.pack(pady=30)





frame_estoque = ctk.CTkFrame(frame_geral, width=450, height=200)
frame_estoque.place(x=20, y=300)
frame_estoque.pack_propagate(False)

frame_lb_estoque = ctk.CTkFrame(frame_estoque, width=430, height=40, fg_color='#1f6aa5')
frame_lb_estoque.pack(pady=10)
frame_lb_estoque.pack_propagate(False)

lb_estoque = ctk.CTkLabel(frame_lb_estoque, font=('Verdana', 20, 'bold'), text='QUANTIDADE', pady=5)
lb_estoque.pack(pady=10)

lb_quantidade = ctk.CTkLabel(frame_estoque, font=('Verdana', 30, 'bold'), text='1', pady=5)
lb_quantidade.pack(pady=30)

botao_menos = ctk.CTkButton(frame_estoque, text='-', width=35, height=35, font=('Verdana', 30, 'bold'), fg_color='#333333', command=diminuir_estoque)
botao_menos.place(x=120, y=92)

botao_mais = ctk.CTkButton(frame_estoque, text='+', width=35, height=35, font=('Verdana', 30, 'bold'), fg_color='#333333', command=aumentar_estoque)
botao_mais.place(x=300, y=92)





frame_valor_total = ctk.CTkFrame(frame_geral, width=450, height=200)
frame_valor_total.place(x=20, y=510)
frame_valor_total.pack_propagate(False)

frame_lb_valor_total = ctk.CTkFrame(frame_valor_total, width=430, height=40, fg_color='#1f6aa5')
frame_lb_valor_total.pack(pady=10)
frame_lb_valor_total.pack_propagate(False)

lb_valor_total = ctk.CTkLabel(frame_lb_valor_total, font=('Verdana', 20, 'bold'), text='VALOR TOTAL', pady=5)
lb_valor_total.pack(pady=10)

lb_preco_total = ctk.CTkLabel(frame_valor_total, font=('Verdana', 30, 'bold'), text='R$ 0,00', pady=5)
lb_preco_total.pack(pady=30)



frame_botoes_venda = ctk.CTkFrame(frame_geral, width=450, height=170)
frame_botoes_venda.place(x=20, y=720)
frame_botoes_venda.pack_propagate(False)




cb_forma_pagamento = ctk.CTkComboBox(frame_botoes_venda, width=205, height=70, values=["PIX", "Débito", "Crédito"], state='readonly', font=('Verdana', 24), justify='center')
cb_forma_pagamento.set("PIX")
cb_forma_pagamento.place(x=235, y=10)

bt_remover_item_venda = ctk.CTkButton(frame_botoes_venda, width=215, height=70, text='REMOVER ITEM', fg_color='red', font=('Verdana', 24), hover_color='darkred', command=remover_item_venda)
bt_remover_item_venda.place(x=10, y=10) 

bt_finalizar_venda = ctk.CTkButton(frame_botoes_venda, width=430, height=70, text='FINALIZAR VENDA', fg_color='green', font=('Verdana', 24), hover_color='darkgreen', command=finalizar_venda)
bt_finalizar_venda.place(x=10, y=90)












frame_lista_produto = ctk.CTkFrame(frame_geral, width=1000, height=800)
frame_lista_produto.place(x=480, y=90)
frame_lista_produto.pack_propagate(False)

frame_venda = ctk.CTkFrame(frame_lista_produto, width=980, height=40, fg_color='#1f6aa5')
frame_venda.pack(pady=10)
frame_venda.pack_propagate(False)

lb_venda = ctk.CTkLabel(frame_venda, font=('Verdana', 24, 'bold'), text='VENDA', pady=5)
lb_venda.pack(pady=10)

scroll_frame_venda = ctk.CTkScrollableFrame(frame_lista_produto, width=955, height=720)
scroll_frame_venda.pack()





#conteudo frame_produtos

frame_direita = ctk.CTkFrame(app, width=400, height=1080)
frame_direita.place(x=1520, y=0)

bt_aparencia = ctk.CTkButton(app, text='', width=50, height=50, fg_color='gray', hover_color='darkgray', command=mudar_aparencia, image=img_modo)
bt_aparencia.place(x=1850, y=20)

frame_produtos = ctk.CTkFrame(frame_direita, width=360, height=900 ,border_width=3, border_color='#1f6aa5')
frame_produtos.place(x=20, y=85)

frame_produtos.pack_propagate(False)

frame_titulo = ctk.CTkFrame(frame_produtos, width=340, height=50 , fg_color='#1f6aa5')
frame_titulo.pack(pady=10)
frame_titulo.pack_propagate(False)

lb_titulo_produto  = ctk.CTkLabel(frame_titulo, text='Produtos', font=('Verdana', 20, 'bold'))
lb_titulo_produto.pack(pady=10)

lista_box = CTkListbox(frame_produtos, width=320, height=740, font=('Verdana', 19))
lista_box.pack(padx=10)


bt_adicionar_compra = ctk.CTkButton(frame_produtos, width=190, height=50, text='ADICIONAR PARA VENDA', fg_color='green', hover_color='darkgreen', command=botao_adicionar_compra)
bt_adicionar_compra.place(y=835, x=10)

bt_adicionar_produto = ctk.CTkButton(frame_produtos, width=60, height=50, text='+', fg_color='green', hover_color='darkgreen', font=('Verdana', 21),  command=abrir_janela_addproduto)
bt_adicionar_produto.place(y=835, x=210)

bt_remover_produto = ctk.CTkButton(frame_produtos, width=60, height=50, text='', image=img_lixeira, fg_color='red', hover_color='darkred', font=('Verdana', 19), command=remover_produto)
bt_remover_produto.place(y=835, x=285)

bt_consulta = ctk.CTkButton(frame_direita,  width=360, height=65, text="CONSULTAS", font=('Verdana', 21), command=abrir_janela_consulta)
bt_consulta.place(x=20, y=1000)


carregar_produtos()

app.mainloop()