import asyncio
import pygame

from sys import exit
from config import *
from game.estado import EstadoJogo
from game.fase_noite import FaseNoite

async def main():
    pygame.init()
    pygame.mixer.init()

    ecra = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Nightfall Looter")
    relogio = pygame.time.Clock()

    #fazer animação do menu de dia e quando inicia transiciona pra noite
    #comecando o saque

    estado_atual = EstadoJogo.NOITE
    fase_noite = FaseNoite()
    fase_noite.iniciar_musica()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

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
        await asyncio.sleep(0) # FUNDAMENTAL pra rodar no navegador

if __name__ == "__main__":
    asyncio.run(main())