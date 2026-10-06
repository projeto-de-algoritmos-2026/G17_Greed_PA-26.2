import heapq

def construir_codigos(texto):
    frequencias = {}
    for letra in texto:
        frequencias[letra] = frequencias.get(letra, 0) + 1

    fila = []
    desempate = 0
    for letra in sorted(frequencias):
        heapq.heappush(fila, (frequencias[letra], desempate, letra))
        desempate += 1

    while len(fila) > 1:
        freq_a, _, arvore_a = heapq.heappop(fila)
        freq_b, _, arvore_b = heapq.heappop(fila)
        heapq.heappush(fila, (freq_a + freq_b, desempate, (arvore_a, arvore_b)))
        desempate += 1

    codigos = {}
    if fila:
        arvore = fila[0][2]
        if isinstance(arvore, str):
            codigos[arvore] = "0"  # texto com uma letra só
        else:
            preencher_codigos(arvore, "", codigos)
    return codigos


def preencher_codigos(arvore, prefixo, codigos):
    if isinstance(arvore, str):
        codigos[arvore] = prefixo
        return

    esquerda, direita = arvore
    preencher_codigos(esquerda, prefixo + "0", codigos)
    preencher_codigos(direita, prefixo + "1", codigos)


def codificar(texto, codigos):
    return "".join(codigos[letra] for letra in texto)


def decodificar(bits, codigos):
    letra_do_codigo = {codigo: letra for letra, codigo in codigos.items()}

    texto = ""
    codigo_atual = ""
    for bit in bits:
        codigo_atual += bit
        if codigo_atual in letra_do_codigo:
            texto += letra_do_codigo[codigo_atual]
            codigo_atual = ""
    return texto
