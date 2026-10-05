from algoritmos.huffman import construir_codigos, codificar, decodificar


def test_codifica_e_decodifica_de_volta():
    for palavra in ["MAPA", "TESOURO", "ABRACADABRA"]:
        codigos = construir_codigos(palavra)
        assert decodificar(codificar(palavra, codigos), codigos) == palavra


def test_letra_mais_comum_tem_o_menor_codigo():
    codigos = construir_codigos("ABRACADABRA")
    assert len(codigos["A"]) == min(len(codigo) for codigo in codigos.values())


def test_nenhum_codigo_e_comeco_de_outro():
    codigos = list(construir_codigos("ENCANTAMENTO").values())
    for a in codigos:
        for b in codigos:
            assert a == b or not b.startswith(a)


def test_texto_com_uma_letra_so():
    codigos = construir_codigos("AAA")
    assert codigos == {"A": "0"}
    assert decodificar(codificar("AAA", codigos), codigos) == "AAA"
