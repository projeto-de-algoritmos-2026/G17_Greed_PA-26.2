import asyncio
import pygame

from sys import exit
from config import *
from game.fases import FASES
from game.estado import EstadoJogo
from game.progresso import Progresso
from ui.controles import desenhar_controles
from ui.cores import PRETO
from ui.texto import carregar_fonte


def apresentar(ecra_real, ecra_virtual):
    """Estica a tela virtual para a janela sem deformar: mantém a proporção,
    centraliza e deixa faixas pretas no que sobrar."""
    largura_real, altura_real = ecra_real.get_size()
    escala = min(largura_real / LARGURA_VIRTUAL, altura_real / ALTURA_VIRTUAL)

    largura = int(LARGURA_VIRTUAL * escala)
    altura = int(ALTURA_VIRTUAL * escala)
    ecra_esticado = pygame.transform.scale(ecra_virtual, (largura, altura))

    ecra_real.fill(PRETO)
    ecra_real.blit(ecra_esticado, ((largura_real - largura) // 2, (altura_real - altura) // 2))


async def main():
    pygame.init()
    pygame.mixer.init()

    ecra_real = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Nightfall Looter")
    tela_cheia = False

    #tudo é desenhado nesta tela menor (sprites 16x16) e depois esticado
    ecra_virtual = pygame.Surface((LARGURA_VIRTUAL, ALTURA_VIRTUAL))
    relogio = pygame.time.Clock()

    fonte_titulo = carregar_fonte(20)
    fonte_texto = carregar_fonte(14)
    mostrando_controles = False

    progresso = Progresso()
    fase_atual = FASES[EstadoJogo.MENU](progresso)

    while True:
        estava_pausado = mostrando_controles
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F1:
                    mostrando_controles = not mostrando_controles
                elif evento.key == pygame.K_ESCAPE and mostrando_controles:
                    mostrando_controles = False
                elif evento.key == pygame.K_F11:
                    tela_cheia = not tela_cheia
                    if tela_cheia:
                        ecra_real = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        ecra_real = pygame.display.set_mode((LARGURA, ALTURA))

        #com os controles abertos o jogo fica pausado
        #(a tecla que fecha os controles também não chega na fase)
        if not mostrando_controles and not estava_pausado:
            fase_atual.atualizar(eventos)

        if fase_atual.proximo_estado is not None:
            proximo_estado = fase_atual.proximo_estado
            if proximo_estado == EstadoJogo.MENU:
                progresso = Progresso()  #voltou ao menu: o jogo recomeça do zero
            fase_atual = FASES[proximo_estado](progresso)

        fase_atual.desenhar(ecra_virtual)
        if mostrando_controles:
            desenhar_controles(ecra_virtual, fonte_titulo, fonte_texto)

        apresentar(ecra_real, ecra_virtual)

        pygame.display.flip()
        relogio.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
