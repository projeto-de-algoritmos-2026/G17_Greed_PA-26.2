# Classes: Item, Bau, Cidade, Pergaminho, Jogador
import pygame
from config import *
from ui.cores import COR_JOGADOR

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(COR_JOGADOR)
        self.rect = self.image.get_rect(center=(x,y)) #colisao

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.rect.x -= VELOCIDADE_JOGADOR #diminui o x
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.rect.x += VELOCIDADE_JOGADOR
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.rect.y -= VELOCIDADE_JOGADOR
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.rect.y += VELOCIDADE_JOGADOR

        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

class Item:
    def __init__(self, nome, peso, valor):
        self.nome = nome
        self.peso = peso
        self.valor = valor

class Bau(pygame.sprite.Sprite):
    def __init__(self, x, y, itens=None):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(( 218,165, 32))
        self.rect = self.image.get_rect(center=(x,y))

        self.itens = itens if itens else[]
        self.aberto = False
        self.som_abrir = pygame.mixer.Sound("assets/sons/bau.mpeg")
        self.som_abrir.set_volume(0.1)

    def abrir(self):
        self.aberto = True
        self.som_abrir.play()
        self.image.fill((100,100,100))
        return self.itens

    class Cidade(pygame.sprite.Sprite):
        def __init__(self, x, y, nome):
            super().__init__()
            self.image = pygame.Surface((40,40))
            self.image.fill((70,130,180))
            self.rect = self.image.get_rect(center=(x,y))

            #caminhoneiro e cmp
            self.nome = nome
            self.precos = {}
