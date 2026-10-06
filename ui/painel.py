import pygame
from config import LARGURA_VIRTUAL, ALTURA_VIRTUAL
from ui.cores import (
    COR_BORDA_PAINEL,
    COR_CURSOR,
    COR_FUNDO_PAINEL,
    COR_TRILHO,
    CORES_RARIDADE,
    DOURADO,
)
from ui.texto import desenhar_texto

ALTURA_LINHA = 20


def desenhar_painel(ecra, largura, altura):
    """Desenha um painel no centro da tela e devolve o canto (x, y) dele."""
    x = (LARGURA_VIRTUAL - largura) // 2
    y = (ALTURA_VIRTUAL - altura) // 2

    pygame.draw.rect(ecra, COR_FUNDO_PAINEL, (x, y, largura, altura))
    pygame.draw.rect(ecra, COR_BORDA_PAINEL, (x, y, largura, altura), width=2)
    return x, y


def desenhar_barra(ecra, x, y, largura, altura, fracao, cor):
    """Barra horizontal: `fracao` (de 0 a 1) é o quanto dela fica preenchido."""
    pygame.draw.rect(ecra, COR_TRILHO, (x, y, largura, altura))

    preenchido = int(largura * max(0, min(fracao, 1)))
    pygame.draw.rect(ecra, cor, (x, y, preenchido, altura))


def desenhar_lista_itens(ecra, fonte, itens, x, y, largura, selecionado=None, max_itens=8):
    """Desenha os itens um embaixo do outro, cada nome na cor da sua raridade.

    `selecionado` é o índice do item com o cursor (None = lista sem cursor).
    Quando a lista é maior que `max_itens`, ela rola e ganha uma barra na direita.
    """
    inicio = 0
    if selecionado is not None:
        inicio = max(0, selecionado - max_itens + 1)

    for i, item in enumerate(itens[inicio: inicio + max_itens]):
        y_item = y + i * ALTURA_LINHA

        if inicio + i == selecionado:
            pygame.draw.rect(ecra, COR_CURSOR, (x - 5, y_item - 2, largura, ALTURA_LINHA - 2))

        desenhar_texto(ecra, item.descricao(), x, y_item, fonte, CORES_RARIDADE[item.raridade])

    if len(itens) > max_itens:
        altura_trilho = max_itens * ALTURA_LINHA
        x_barra = x + largura - 4
        pygame.draw.rect(ecra, COR_TRILHO, (x_barra, y, 4, altura_trilho))

        altura_barra = max(20, altura_trilho * max_itens // len(itens))
        progresso = inicio / (len(itens) - max_itens)
        y_barra = y + int((altura_trilho - altura_barra) * progresso)
        pygame.draw.rect(ecra, DOURADO, (x_barra, y_barra, 4, altura_barra))
