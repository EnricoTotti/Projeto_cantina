produtos = [] #criação da lista de produtos

print("=== Sistema Simples de Cantina ===") #texto bonitinho

adicionar_mais = 's'  # começa permitindo adicionar

while adicionar_mais.lower() == 's': #enquanto a resposta do adicionar mais for s, ele vai continuar o loop
    nome = input("Nome do produto: ")

    try: #o código sempre tentará fazer o código
        preco = float(input(f"Preço de {nome}: R$ "))
        produtos.append((nome, preco)) #adiciona uma tupla na lista produtos com o nome e o preço do produto
        print(f"{nome} adicionado com sucesso!\n")
    except ValueError: #exceto se der erro de valor
        print("Preço inválido. Tente novamente.\n")
        continue #continue serve para voltar para o try e tentar de novo.

    adicionar_mais = input("Deseja adicionar outro produto? (s/n): ") #pergunta para adicionar mais produtos

print("\n=== Resumo da Compra ===")
total = 0
for nome, preco in produtos: #pega a tupla de cada produto e vai passando mostrando cada um
    print(f"{nome} - R$ {preco:.2f}")
    total += preco #adicionando a soma total dos preços dos produtos

print(f"\nTotal a pagar: R$ {total:.2f}") #mostra o total a pagar