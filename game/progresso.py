from config import CAPACIDADE_INICIAL, FATOR_SOBRECARGA


class Progresso:
    """Tudo que o jogador leva de uma fase para a outra."""

    def __init__(self):
        self.andar = 1
        self.ouro = 0
        self.inventario = []          # lista de Item
        self.capacidade_maxima = CAPACIDADE_INICIAL   # kg

        # melhorias compradas no mercador
        self.compras_mochila = 0
        self.nivel_sorte = 0
        self.nivel_decifrador = 0

        # preenchido pela masmorra e usado na tela de resultado
        self.itens_do_andar = []
        self.melhor_aproveitamento = 0

    def peso_total(self):
        return sum(item.peso for item in self.inventario)

    def limite_de_peso(self):
        """Máximo que dá para carregar (acima da capacidade, mas andando lento)."""
        return int(self.capacidade_maxima * FATOR_SOBRECARGA)

    def esta_pesado(self):
        return self.peso_total() > self.capacidade_maxima
