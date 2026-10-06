import copy
import random
from config import CHANCE_PERGAMINHO
from game.entidades import Item

# "chance" é o peso do sorteio: quanto maior, mais o item aparece nos baús.
# "a_granel" marca os itens que dá para levar só uma parte (o valor é o do item inteiro).
# Raro não quer dizer melhor valor por kg: há itens pesados e caros que valem a pena
# e deixam o guloso sem espaço — é aí que dá para ganhar dele.
CATALOGO = [
    {"nome": "Poção de Vida", "peso": 2, "valor": 22, "chance": 50, "raridade": "COMUM"},
    {"nome": "Adaga", "peso": 3, "valor": 30, "chance": 40, "raridade": "COMUM"},
    {"nome": "Capacete de Ferro", "peso": 4, "valor": 34, "chance": 30, "raridade": "COMUM"},
    {"nome": "Espada Longa", "peso": 6, "valor": 45, "chance": 20, "raridade": "COMUM"},
    {"nome": "Anel de Prata", "peso": 1, "valor": 30, "chance": 18, "raridade": "RARO"},
    {"nome": "Escudo Reforçado", "peso": 7, "valor": 95, "chance": 15, "raridade": "RARO"},
    {"nome": "Pó de Cristal", "peso": 4, "valor": 48, "chance": 15, "raridade": "RARO", "a_granel": True},
    {"nome": "Rubi", "peso": 1, "valor": 55, "chance": 10, "raridade": "EPICO"},
    {"nome": "Cálice Encantado", "peso": 3, "valor": 80, "chance": 8, "raridade": "EPICO"},
    {"nome": "Elixir em Frasco", "peso": 3, "valor": 66, "chance": 6, "raridade": "EPICO", "a_granel": True},
    {"nome": "Coroa de Ouro", "peso": 5, "valor": 140, "chance": 5, "raridade": "LENDARIO"},
    {"nome": "Cajado do Arquimago", "peso": 9, "valor": 230, "chance": 3, "raridade": "LENDARIO"},
]

# Pergaminhos: quanto mais raro, maior a palavra, o valor e o nível exigido para ler.
PERGAMINHOS = {
    "COMUM": {"chance": 50, "nivel": 1, "valor": 40, "palavras": ["OURO", "FADA", "MAPA", "DADO"]},
    "RARO": {"chance": 30, "nivel": 2, "valor": 90, "palavras": ["COROA", "ADAGA", "MOEDA", "BARRIL"]},
    "EPICO": {"chance": 15, "nivel": 3, "valor": 170, "palavras": ["TESOURO", "MASMORRA", "ESMERALDA"]},
    "LENDARIO": {"chance": 5, "nivel": 4, "valor": 320, "palavras": ["ABRACADABRA", "NECROMANTE", "ENCANTAMENTO"]},
}

# Quanto vale um pergaminho que ninguém decifrou
VALOR_PERGAMINHO_SELADO = 5


def chance_com_sorte(chance, raridade, nivel_sorte):
    """A sorte aumenta a chance de tudo que não é comum."""
    if raridade == "COMUM":
        return chance
    return chance * (1 + 0.5 * nivel_sorte)


def criar_item(dados):
    return Item(dados["nome"], dados["peso"], dados["valor"], dados["raridade"],
                a_granel=dados.get("a_granel", False))


def criar_pergaminho(raridade, palavra):
    # Pergaminho não pesa nada e não entra na conta da mochila
    return Item("Pergaminho", 0, VALOR_PERGAMINHO_SELADO, raridade, texto=palavra)


def sortear_pergaminho(nivel_sorte):
    raridades = list(PERGAMINHOS)
    chances = [chance_com_sorte(PERGAMINHOS[r]["chance"], r, nivel_sorte) for r in raridades]

    raridade = random.choices(raridades, weights=chances)[0]
    palavra = random.choice(PERGAMINHOS[raridade]["palavras"])
    return criar_pergaminho(raridade, palavra)


def sortear_loot(nivel_sorte):
    """Sorteia os itens de um baú."""
    qtd_itens = random.randint(1, 3)
    chances = [chance_com_sorte(d["chance"], d["raridade"], nivel_sorte) for d in CATALOGO]

    escolhas = random.choices(CATALOGO, weights=chances, k=qtd_itens)

    loot = []
    for escolha in escolhas:
        adicionar_item(loot, criar_item(escolha))

    if random.randint(1, 100) <= CHANCE_PERGAMINHO:
        loot.append(sortear_pergaminho(nivel_sorte))

    return loot


def adicionar_item(lista, item):
    """Põe o item na lista. Item a granel se junta ao monte de mesmo nome."""
    if item.a_granel:
        for outro in lista:
            if outro.nome == item.nome:
                outro.peso += item.peso
                outro.valor += item.valor
                return
    lista.append(item)


def retirar_item(lista, indice):
    """Tira o item da lista e o devolve. De item a granel sai só 1kg por vez."""
    item = lista[indice]

    if item.a_granel and item.peso > 1:
        valor_do_kg = item.valor // item.peso
        item.peso -= 1
        item.valor -= valor_do_kg
        return Item(item.nome, 1, valor_do_kg, item.raridade, a_granel=True)

    return lista.pop(indice)


def separar_granel(itens):
    """Devolve uma lista nova em que cada monte a granel virou vários itens de 1kg."""
    separados = []
    for item in itens:
        if item.a_granel:
            valor_do_kg = item.valor // item.peso
            for _ in range(item.peso):
                separados.append(Item(item.nome, 1, valor_do_kg, item.raridade, a_granel=True))
        else:
            separados.append(item)
    return separados


def juntar_granel(itens):
    """O contrário de separar_granel: devolve uma lista nova com os montes reunidos."""
    juntos = []
    for item in itens:
        adicionar_item(juntos, copy.copy(item))
    return juntos
