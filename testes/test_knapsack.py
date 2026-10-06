from algoritmos.knapsack import mochila_gulosa, mochila_fracionaria


class Item:
    def __init__(self, peso, valor):
        self.peso = peso
        self.valor = valor


def test_pega_tudo_quando_cabe():
    itens = [Item(2, 30), Item(3, 40)]
    escolhidos, valor = mochila_gulosa(itens, 10)
    assert len(escolhidos) == 2
    assert valor == 70


def test_prefere_o_melhor_valor_por_peso():
    leve_e_valioso = Item(1, 100)
    pesado_e_barato = Item(5, 50)
    escolhidos, valor = mochila_gulosa([pesado_e_barato, leve_e_valioso], 5)
    assert escolhidos == [leve_e_valioso]
    assert valor == 100


def test_mochila_vazia_sem_capacidade():
    escolhidos, valor = mochila_gulosa([Item(1, 10)], 0)
    assert escolhidos == []
    assert valor == 0


def test_guloso_nem_sempre_e_otimo_com_itens_inteiros():
    # O guloso pega o item de 1kg (melhor valor/peso) e depois não cabe o de 10kg.
    # A melhor resposta seria levar só o de 10kg, que vale 100.
    itens = [Item(1, 20), Item(10, 100)]
    escolhidos, valor = mochila_gulosa(itens, 10)
    assert valor == 20


def test_fracionaria_leva_um_pedaco_e_serve_de_teto():
    itens = [Item(1, 20), Item(10, 100)]
    # 1kg inteiro (20) + 9kg do segundo item (9 x 10 = 90)
    assert mochila_fracionaria(itens, 10) == 110
    assert mochila_fracionaria(itens, 10) >= mochila_gulosa(itens, 10)[1]
