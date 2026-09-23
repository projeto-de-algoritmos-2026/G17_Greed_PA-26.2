import pygame
from game.fases.fase import Fase
from game.entidades import Jogador, Parede,  Bau, Item
from ui.cores import COR_FUNDO_MASMORRA
from config import TAMANHO_PISO

#numero 0 é chao
# 1 é parede
# 2 é o player
# 3 é báu
class FaseNoite(Fase):
    def __init__(self):
        super().__init__(cor_fundo = COR_FUNDO_MASMORRA, musica = 'assets/sons/masmorra.mp3')

        self.grupo_baus = pygame.sprite.Group()
        item1 = Item(nome="Espada Longa", peso=5, valor=50)
        item2 = Item(nome="Poção de Vida", peso=1, valor=20)
        #bau_armas = Bau(x=200, y=150, itens=[item1, item2])
        item3 = Item(nome="Coroa de Ouro", peso=3, valor=150)
        #bau_tesouro = Bau(x=600, y=400, itens=[item3])

        #self.grupo_sprites.add(bau_armas, bau_tesouro)
        #self.grupo_baus.add(bau_armas, bau_tesouro)
        self.grupo_paredes = pygame.sprite.Group()

        self.matriz_mapa = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 0, 1, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 3, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],

        ]

        self.construir_mapa()

    def construir_mapa(self):
        for y, linha in enumerate(self.matriz_mapa):
            for x, valor in enumerate(linha):
                pos_x = x * TAMANHO_PISO
                pos_y = y * TAMANHO_PISO

                if valor == 1:
                    parede = Parede(pos_x, pos_y)
                    self.grupo_sprites.add(parede)
                    self.grupo_paredes.add(parede)
                elif valor == 2:
                    self.jogador = Jogador(pos_x, pos_y, self.grupo_paredes)
                    self.grupo_sprites.add(self.jogador)
                elif valor == 3:
                    item_teste = Item("Rubi", 1, 100)
                    bau = Bau(pos_x, pos_y, [item_teste])
                    self.grupo_sprites.add(bau)
                    self.grupo_baus.add(bau)


    def atualizar(self, eventos):
        super().atualizar(eventos)
        for evento in eventos:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                self.tentar_abrir_baus()

    def tentar_abrir_baus(self):
        baus_proximos = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
        for bau in baus_proximos:
            if isinstance(bau, Bau) and not bau.aberto:
                self.saquear_loot(bau.abrir())

    def saquear_loot(self, itens_saqueados):
        for item in itens_saqueados:
            print(f"Loot: {item.nome} | Peso: {item.peso} | Valor: {item.valor}")


