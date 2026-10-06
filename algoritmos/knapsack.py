def valor_por_peso(item):
    return item.valor / item.peso


def mochila_gulosa(itens, capacidade):
    """Mochila 0/1: cada item entra inteiro ou não entra."""
    ordenados = sorted(itens, key=valor_por_peso, reverse=True)

    escolhidos = []
    valor_total = 0
    espaco_livre = capacidade

    for item in ordenados:
        if item.peso <= espaco_livre:
            escolhidos.append(item)
            valor_total += item.valor
            espaco_livre -= item.peso

    return escolhidos, valor_total


def mochila_fracionaria(itens, capacidade):
    """Mochila fracionária: dá para levar só um pedaço de um item."""

    ordenados = sorted(itens, key=valor_por_peso, reverse=True)

    valor_total = 0
    espaco_livre = capacidade

    for item in ordenados:
        if espaco_livre == 0:
            break

        peso_levado = min(item.peso, espaco_livre)
        valor_total += valor_por_peso(item) * peso_levado
        espaco_livre -= peso_levado

    return valor_total
