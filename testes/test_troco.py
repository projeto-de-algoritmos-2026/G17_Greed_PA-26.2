from algoritmos.troco import troco_guloso

MOEDAS = [100, 50, 25, 10, 5, 1]


def test_exemplo_do_mercador():
    assert troco_guloso(185, MOEDAS) == [100, 50, 25, 10]


def test_repete_a_mesma_moeda():
    assert troco_guloso(230, MOEDAS) == [100, 100, 25, 5]


def test_valor_zero_nao_usa_moedas():
    assert troco_guloso(0, MOEDAS) == []


def test_guloso_nem_sempre_e_otimo_com_moedas_estranhas():
    # Com moedas 1, 3 e 4 o guloso usa 3 moedas para 6 (4+1+1); o melhor seria 3+3.
    assert troco_guloso(6, [1, 3, 4]) == [4, 1, 1]
