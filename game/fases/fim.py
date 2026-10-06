import pygame
from game.estado import EstadoJogo
from game.fases.fase import Fase
from ui.cores import BRANCO, CINZA_INATIVO, COR_FUNDO_MENU, DOURADO
from ui.texto import carregar_fonte, desenhar_texto_centralizado


class Fim(Fase):
    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MENU, musica='assets/sons/intro.mpeg')
        self.fonte_logo = carregar_fonte(40)

    def atualizar(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.proximo_estado = EstadoJogo.MENU

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)

        desenhar_texto_centralizado(ecra, "Fim de jogo", 70, self.fonte_logo, DOURADO)

        melhor = int(self.progresso.melhor_aproveitamento * 100)
        linhas = [
            f"Andares concluídos: {self.progresso.andar}",
            f"Ouro final: {self.progresso.ouro}",
            f"Melhor aproveitamento contra o guloso: {melhor}%",
        ]
        for i, linha in enumerate(linhas):
            desenhar_texto_centralizado(ecra, linha, 150 + i * 30, self.fonte_titulo, BRANCO)

        desenhar_texto_centralizado(ecra, "[ESPAÇO] Voltar ao menu", 330, self.fonte_texto, CINZA_INATIVO)
