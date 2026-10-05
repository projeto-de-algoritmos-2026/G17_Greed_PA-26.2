import pygame
from algoritmos.knapsack import mochila_gulosa, mochila_fracionaria
from config import BONUS_MAXIMO_OURO, BONUS_VENCEU_GULOSO
from game.estado import EstadoJogo
from game.fases.fase import Fase
from game.itens import juntar_granel
from ui.cores import BRANCO, CINZA_INATIVO, COR_FUNDO_MENU, DOURADO
from ui.painel import desenhar_lista_itens
from ui.texto import desenhar_texto, desenhar_texto_centralizado

MAX_ITENS_NA_LISTA = 8


class Resultado(Fase):
    """Compara a mochila do jogador com a do algoritmo guloso e dá o bônus de ouro."""

    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MENU, musica='assets/sons/masmorra.mp3')

        # O jogador pode carregar até o limite (andando lento), então o guloso também
        self.limite = progresso.limite_de_peso()

        self.itens_jogador = [item for item in progresso.inventario if not item.eh_pergaminho()]
        self.valor_jogador = sum(item.valor for item in self.itens_jogador)

        escolhidos, self.valor_guloso = mochila_gulosa(progresso.itens_do_andar, self.limite)
        self.itens_guloso = juntar_granel(escolhidos)

        # Teto: o valor que daria se fosse possível levar pedaços de qualquer item
        self.valor_teto = int(mochila_fracionaria(progresso.itens_do_andar, self.limite))

        if self.valor_guloso > 0:
            self.aproveitamento = self.valor_jogador / self.valor_guloso
        else:
            self.aproveitamento = 1

        self.bonus = int(BONUS_MAXIMO_OURO * min(self.aproveitamento, 1))
        if self.valor_jogador > self.valor_guloso:
            self.bonus += BONUS_VENCEU_GULOSO

        progresso.ouro += self.bonus
        progresso.melhor_aproveitamento = max(progresso.melhor_aproveitamento, self.aproveitamento)

    def atualizar(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.proximo_estado = EstadoJogo.MERCADOR

    def mensagem(self):
        if self.valor_jogador > self.valor_guloso:
            return "Você venceu o algoritmo guloso! Com itens inteiros ele nem sempre acerta."
        if self.valor_jogador == self.valor_guloso:
            return "Você empatou com o algoritmo guloso!"
        return f"O guloso conseguiu ${self.valor_guloso - self.valor_jogador} a mais que você."

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)

        desenhar_texto_centralizado(ecra, f"Fim do andar {self.progresso.andar}", 8, self.fonte_titulo, DOURADO)

        self.desenhar_coluna(ecra, 30, f"Sua mochila: ${self.valor_jogador}", self.itens_jogador)
        self.desenhar_coluna(ecra, 335, f"Guloso: ${self.valor_guloso}", self.itens_guloso)

        linhas = [
            (f"Guloso: ordena por valor/peso e pega o que couber em {self.limite}kg.", CINZA_INATIVO),
            (f"Teto: ${self.valor_teto} (se desse para levar pedaços, o guloso sempre acertaria).", CINZA_INATIVO),
            (self.mensagem(), BRANCO),
            (f"Aproveitamento: {int(self.aproveitamento * 100)}%   Bônus: +{self.bonus} de ouro", DOURADO),
        ]
        for i, (texto, cor) in enumerate(linhas):
            desenhar_texto(ecra, texto, 30, 252 + i * 18, self.fonte_texto, cor)

        desenhar_texto_centralizado(ecra, "[ESPAÇO] Ir ao mercador", 338, self.fonte_texto, CINZA_INATIVO)

    def desenhar_coluna(self, ecra, x, titulo, itens):
        desenhar_texto(ecra, titulo, x, 36, self.fonte_titulo, BRANCO)
        desenhar_lista_itens(ecra, self.fonte_texto, itens[:MAX_ITENS_NA_LISTA], x, 64, 270)

        escondidos = len(itens) - MAX_ITENS_NA_LISTA
        if escondidos > 0:
            desenhar_texto(ecra, f"... e mais {escondidos}", x, 64 + MAX_ITENS_NA_LISTA * 20,
                           self.fonte_texto, CINZA_INATIVO)
