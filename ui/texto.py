import pygame
from config import FONTE, LARGURA_VIRTUAL
from ui.cores import BRANCO


def carregar_fonte(tamanho):
    return pygame.font.Font(FONTE, tamanho)


def desenhar_texto(ecra, texto, x, y, fonte, cor=BRANCO):
    imagem = fonte.render(texto, False, cor)   # False = sem anti-aliasing
    ecra.blit(imagem, (x, y))
    return imagem.get_width()


def desenhar_texto_centralizado(ecra, texto, y, fonte, cor=BRANCO):
    largura_texto = fonte.size(texto)[0]
    desenhar_texto(ecra, texto, (LARGURA_VIRTUAL - largura_texto) // 2, y, fonte, cor)
