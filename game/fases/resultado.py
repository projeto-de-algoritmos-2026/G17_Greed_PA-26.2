import pygame
from algoritmos.knapsack import mochila_gulosa, mochila_fracionaria
from config import APROVEITAMENTO_MINIMO, BONUS_MAXIMO_OURO, BONUS_VENCEU_GULOSO
from game.estado import EstadoJogo
from game.fases.fase import Fase
from game.entidades import Item
from game.itens import separar_granel
from ui.cores import BRANCO, CINZA_INATIVO, COR_FUNDO_MENU, COR_GULOSO, DOURADO, VERDE
from ui.painel import desenhar_barra, desenhar_lista_itens
from ui.texto import desenhar_texto, desenhar_texto_centralizado

MAX_ITENS_NA_LISTA = 4


def so_no_primeiro(itens, outros):
    """Os itens de `itens` que não estão em `outros` (comparando pelo nome), mais valiosos primeiro."""
    nomes = [item.nome for item in outros]

    diferentes = []
    for item in itens:
        if item.nome in nomes:
            nomes.remove(item.nome)
        else:
            diferentes.append(item)

    return sorted(agrupar(diferentes), key=lambda item: item.valor, reverse=True)


def agrupar(itens):
    """Junta os itens de mesmo nome em uma linha só: "3x Poção de Vida (6kg) $66"."""
    grupos = {}
    for item in itens:
        grupos.setdefault(item.nome, []).append(item)

    agrupados = []
    for nome, grupo in grupos.items():
        peso = sum(item.peso for item in grupo)
        valor = sum(item.valor for item in grupo)

        # item a granel já aparece pelo peso; os outros ganham a quantidade na frente
        if len(grupo) > 1 and not grupo[0].a_granel:
            nome = f"{len(grupo)}x {nome}"
        agrupados.append(Item(nome, peso, valor, grupo[0].raridade))
    return agrupados


class Resultado(Fase):
    """Compara a mochila do jogador com a do algoritmo guloso e dá o bônus de ouro."""

    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MENU, musica='assets/sons/masmorra.mp3')

        # O guloso enche uma mochila do mesmo tamanho da do jogador
        capacidade = progresso.capacidade_maxima

        itens_jogador = separar_granel([item for item in progresso.inventario if not item.eh_pergaminho()])
        self.valor_jogador = sum(item.valor for item in itens_jogador)
        self.peso_jogador = sum(item.peso for item in itens_jogador)

        # Mochila 0/1: cada item entra inteiro ou fica de fora
        itens_guloso, self.valor_guloso = mochila_gulosa(progresso.itens_do_andar, capacidade)
        self.peso_guloso = sum(item.peso for item in itens_guloso)

        # Mochila fracionária: o valor que daria se todo item pudesse ser cortado em pedaços.
        # Ninguém passa desse teto, nem o jogador nem o guloso.
        self.valor_teto = int(mochila_fracionaria(progresso.itens_do_andar, capacidade))

        self.so_jogador = so_no_primeiro(itens_jogador, itens_guloso)
        self.so_guloso = so_no_primeiro(itens_guloso, itens_jogador)

        if self.valor_guloso > 0:
            self.aproveitamento = self.valor_jogador / self.valor_guloso
        else:
            self.aproveitamento = 1

        self.bonus = self.calcular_bonus()
        progresso.ouro += self.bonus
        progresso.melhor_aproveitamento = max(progresso.melhor_aproveitamento, self.aproveitamento)

    def calcular_bonus(self):
        """Bônus cheio para quem empata com o guloso, nada para quem fica abaixo do mínimo."""
        if self.aproveitamento < APROVEITAMENTO_MINIMO:
            return 0

        parte = (min(self.aproveitamento, 1) - APROVEITAMENTO_MINIMO) / (1 - APROVEITAMENTO_MINIMO)
        bonus = int(BONUS_MAXIMO_OURO * parte)

        if self.valor_jogador > self.valor_guloso:
            bonus += BONUS_VENCEU_GULOSO
        return bonus

    def atualizar(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.proximo_estado = EstadoJogo.MERCADOR

    def mensagem(self):
        diferenca = abs(self.valor_jogador - self.valor_guloso)

        if self.valor_jogador > self.valor_guloso:
            return f"Você venceu o guloso por ${diferenca}! Com itens inteiros ele nem sempre acerta.", VERDE
        if self.valor_jogador == self.valor_guloso:
            return "Empate com o guloso!", BRANCO
        return f"O guloso levou ${diferenca} a mais que você.", BRANCO

    def texto_bonus(self):
        porcentagem = int(self.aproveitamento * 100)
        if self.bonus > 0:
            return f"Bônus: +{self.bonus} de ouro (você fez {porcentagem}% do guloso)"

        minimo = int(APROVEITAMENTO_MINIMO * 100)
        return f"Sem bônus: você fez {porcentagem}% do guloso e o mínimo é {minimo}%."

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        capacidade = self.progresso.capacidade_maxima

        desenhar_texto_centralizado(ecra, f"Fim do andar {self.progresso.andar}", 8, self.fonte_titulo, DOURADO)
        desenhar_texto_centralizado(ecra, f"Quem encheu melhor a mochila de {capacidade}kg?", 34,
                                    self.fonte_texto, CINZA_INATIVO)

        self.desenhar_placar(ecra, 60, "Você", self.valor_jogador, f"({self.peso_jogador}kg)", DOURADO)
        self.desenhar_placar(ecra, 82, "Guloso (itens inteiros)", self.valor_guloso, f"({self.peso_guloso}kg)",
                             COR_GULOSO)
        self.desenhar_placar(ecra, 104, "Teto (itens em pedaços)", self.valor_teto, "", CINZA_INATIVO)

        texto, cor = self.mensagem()
        desenhar_texto_centralizado(ecra, texto, 132, self.fonte_texto, cor)
        desenhar_texto_centralizado(ecra, self.texto_bonus(), 152, self.fonte_texto, DOURADO)

        self.desenhar_diferencas(ecra)

        desenhar_texto_centralizado(ecra, "Guloso: ordena por valor/kg e pega cada item inteiro que ainda couber.",
                                    300, self.fonte_texto, CINZA_INATIVO)
        desenhar_texto_centralizado(ecra, "Teto: se desse para cortar os itens (mochila fracionária), "
                                    "o guloso seria imbatível.", 316, self.fonte_texto, CINZA_INATIVO)

        desenhar_texto_centralizado(ecra, "[ESPAÇO] Ir ao mercador", 340, self.fonte_texto, CINZA_INATIVO)

    def desenhar_placar(self, ecra, y, nome, valor, detalhe, cor):
        """Uma linha do placar: nome, barra (o teto é a barra cheia) e valor."""
        desenhar_texto(ecra, nome, 30, y, self.fonte_texto, cor)
        desenhar_barra(ecra, 200, y + 1, 280, 12, valor / max(1, self.valor_teto), cor)
        desenhar_texto(ecra, f"${valor} {detalhe}", 490, y, self.fonte_texto, cor)

    def desenhar_diferencas(self, ecra):
        """Só o que mudou entre as duas mochilas: é aí que se vê onde o guloso acertou ou errou."""
        if len(self.so_jogador) == 0 and len(self.so_guloso) == 0:
            desenhar_texto_centralizado(ecra, "Você e o guloso escolheram exatamente os mesmos itens.", 210,
                                        self.fonte_texto, BRANCO)
            return

        self.desenhar_coluna(ecra, 30, "Só você levou:", self.so_jogador, DOURADO)
        self.desenhar_coluna(ecra, 335, "Só o guloso levou:", self.so_guloso, COR_GULOSO)

    def desenhar_coluna(self, ecra, x, titulo, itens, cor):
        desenhar_texto(ecra, titulo, x, 178, self.fonte_texto, cor)

        if len(itens) == 0:
            desenhar_texto(ecra, "(nada)", x, 198, self.fonte_texto, CINZA_INATIVO)
            return

        desenhar_lista_itens(ecra, self.fonte_texto, itens[:MAX_ITENS_NA_LISTA], x, 198, 270)

        escondidos = len(itens) - MAX_ITENS_NA_LISTA
        if escondidos > 0:
            desenhar_texto(ecra, f"... e mais {escondidos}", x, 198 + MAX_ITENS_NA_LISTA * 20,
                           self.fonte_texto, CINZA_INATIVO)
