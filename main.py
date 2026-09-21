import asyncio
import pygame
import sys
from game.estado import EstadoJogo
from config import *
from game.fase_noite import FaseNoite

async def main():
    pygame.init()
    ecra = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Nightfall Looter")
    relogio = pygame.time.Clock()
    #fazer animação do menu de dia e quando inicia transiciona pra noite
    #comecando o saque
    estado_atual = EstadoJogo.NOITE
    a_correr = True
    fase_noite = FaseNoite()

    while a_correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_correr = False
        if estado_atual == EstadoJogo.NOITE:
            ecra.fill((30, 30, 40))
            fase_noite.atualizar()
            fase_noite.desenhar(ecra)
        elif estado_atual == EstadoJogo.DIA:
            ecra.fill((135, 206, 235))
            # TODO: fase_dia.atualizar()
            # TODO: fase_dia.desenhar(ecra)
        elif estado_atual == EstadoJogo.CIDADE:
            ecra.fill((200, 180, 140))
            # TODO: fase_cidade.atualizar()
            # TODO: fase_cidade.desenhar(ecra)
        pygame.display.flip()
        relogio.tick(FPS)


        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())