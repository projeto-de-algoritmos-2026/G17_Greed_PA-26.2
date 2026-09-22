# Tela da masmorra + integração com knapsack.py

import pygame
from game.entidades import Jogador, Bau, Item
from ui.cores import COR_FUNDO_MASMORRA

class FaseNoite:
    def __init__(self):
        self.grupo_sprites  = pygame.sprite.Group() #tudo q mexe no ecra
        self.grupo_baus = pygame.sprite.Group()

        self.jogador = Jogador(x=400, y=300)
        self.grupo_sprites.add(self.jogador)

        item1 = Item(nome="Espada Longa", peso=5, valor=50)
        item2 = Item(nome="Poção de Vida", peso=1, valor=20)
        bau_armas = Bau(x=200, y=150, itens=[item1, item2])
        item3 = Item(nome="Coroa de Ouro", peso=3, valor=150)
        bau_tesouro = Bau(x=600, y=400, itens=[item3])

        self.grupo_sprites.add(bau_armas, bau_tesouro)
        self.grupo_baus.add(bau_armas, bau_tesouro)

    def iniciar_musica(self):
        pygame.mixer.music.load("assets/sons/masmorra.mp3")
        pygame.mixer.music.set_volume(3)
        pygame.mixer.music.play(-1)
    def atualizar(self):
        self.grupo_sprites.update()
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE]:
            baus_tocados = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
            for bau in baus_tocados:
                if isinstance(bau, Bau):
                    if not bau.aberto:
                        itens_saqueados = bau.abrir()

                        print("\n BAÚ ABERTO")
                        for item in itens_saqueados:
                            print(f"Loot: {item.nome} | Peso: {item.peso} | Valor: {item.valor}")
    def desenhar(self, ecra):
        ecra.fill(COR_FUNDO_MASMORRA)
        self.grupo_sprites.draw(ecra)