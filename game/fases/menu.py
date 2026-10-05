import pygame
from game.estado import EstadoJogo
from game.fases.fase import Fase
from ui.controles import desenhar_controles
from ui.cores import BRANCO, CINZA_INATIVO, COR_FUNDO_MENU, DOURADO
from ui.texto import carregar_fonte, desenhar_texto_centralizado

OPCOES = ["Iniciar", "Controles", "Sair"]


class Menu(Fase):
    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MENU, musica='assets/sons/intro.mpeg')
        self.fonte_logo = carregar_fonte(40)

        self.indice_selecionado = 0
        self.mostrando_controles = False

    def atualizar(self, eventos):
        for evento in eventos:
            if evento.type != pygame.KEYDOWN:
                continue

            if self.mostrando_controles:
                if evento.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    self.mostrando_controles = False

            elif evento.key in (pygame.K_UP, pygame.K_w):
                self.indice_selecionado = max(0, self.indice_selecionado - 1)
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.indice_selecionado = min(len(OPCOES) - 1, self.indice_selecionado + 1)
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.escolher(OPCOES[self.indice_selecionado])

    def escolher(self, opcao):
        if opcao == "Iniciar":
            self.proximo_estado = EstadoJogo.MASMORRA
        elif opcao == "Controles":
            self.mostrando_controles = True
        elif opcao == "Sair":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)

        desenhar_texto_centralizado(ecra, "Nightfall Looter", 70, self.fonte_logo, DOURADO)
        desenhar_texto_centralizado(ecra, "Encha a mochila melhor que o algoritmo guloso", 120,
                                    self.fonte_texto, CINZA_INATIVO)

        for i, opcao in enumerate(OPCOES):
            if i == self.indice_selecionado:
                desenhar_texto_centralizado(ecra, f"> {opcao} <", 180 + i * 30, self.fonte_titulo, DOURADO)
            else:
                desenhar_texto_centralizado(ecra, opcao, 180 + i * 30, self.fonte_titulo, BRANCO)

        desenhar_texto_centralizado(ecra, "[SETAS] Escolher | [ESPAÇO] Confirmar | [F1] Controles", 330,
                                    self.fonte_texto, CINZA_INATIVO)

        if self.mostrando_controles:
            desenhar_controles(ecra, self.fonte_titulo, self.fonte_texto)
