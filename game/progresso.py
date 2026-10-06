from config import CAPACIDADE_INICIAL, DIVISOR_ZONA_PESADA


class Progresso:
    """Tudo que o jogador leva de uma fase para a outra."""

    def __init__(self):
        self.andar = 1
        self.ouro = 0
        self.inventario = []          # lista de Item
        self.capacidade_maxima = CAPACIDADE_INICIAL   # kg que cabem na mochila

        # melhorias compradas no mercador
        self.compras_mochila = 0
        self.nivel_sorte = 0
        self.nivel_decifrador = 0

        # preenchido pela masmorra e usado na tela de resultado
        self.itens_do_andar = []
        self.melhor_aproveitamento = 0

    def peso_total(self):
        return sum(item.peso for item in self.inventario)

    def espaco_livre(self):
        return self.capacidade_maxima - self.peso_total()

    def peso_leve(self):
        """Até este peso o jogador anda normal; acima dele começa a zona pesada."""
        return self.capacidade_maxima - self.capacidade_maxima // DIVISOR_ZONA_PESADA

    def esta_pesado(self):
        return self.peso_total() > self.peso_leve()
