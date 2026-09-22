import asyncio
import pygame

from sys import exit
from config import *
#from game.fases import menu, fase_noite, fase_dia, fase_cidade, fim
from game.fases import fase_noite
from game.estado import EstadoJogo


async def main():
    pygame.init()
    pygame.mixer.init()

    ecra = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Nightfall Looter")
    relogio = pygame.time.Clock()

#   fases = {
#        EstadoJogo.MENU: menu,
#        EstadoJogo.NOITE: fase_noite,
#        EstadoJogo.DIA: fase_dia,
#        EstadoJogo.CIDADE: fase_cidade,
#        EstadoJogo.FIM : fim,
#    }

    estado_atual = EstadoJogo.MENU
    fase_atual = fase_noite()
    while True:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

        #fase_atual = fases[estado_atual]()


        fase_atual.atualizar(eventos)
        fase_atual.desenhar(ecra)

        pygame.display.flip()
        relogio.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())