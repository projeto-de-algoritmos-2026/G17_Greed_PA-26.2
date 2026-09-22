import pygame
from game.entidades import Jogador

class Fase():
    def __init__(self, cor_fundo, musica):
        self.musica_ambiente = musica
        self.cor_fundo = cor_fundo
        self.grupo_sprites = pygame.sprite.Group()
        self.jogador = Jogador(x=400, y=300)
        self.grupo_sprites.add(self.jogador)
        self.tocar_musica()

    def tocar_musica(self):
        pygame.mixer.music.load(self.musica_ambiente)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)

    def atualizar(self, eventos):
        self.grupo_sprites.update()

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)

