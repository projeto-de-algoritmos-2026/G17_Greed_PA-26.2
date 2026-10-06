def troco_guloso(valor, moedas):
    troco = []
    restante = valor

    for moeda in sorted(moedas, reverse=True):
        while restante >= moeda:
            troco.append(moeda)
            restante -= moeda

    return troco
