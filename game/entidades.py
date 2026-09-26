# Classes: Item, Bau, Cidade, Pergaminho, Jogador
import pygame
from config import *
from ui.cores import COR_JOGADOR, COR_BAU

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, paredes):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(COR_JOGADOR)
        self.rect = self.image.get_rect(topleft=(x+5,y+5)) # colisao

        self.paredes = paredes # pra colisao

        self.inventario = []
        self.carga_atual = 0
        self.capacidade_maxima = 20

    def update(self):
        teclas = pygame.key.get_pressed()

        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx = -VELOCIDADE_JOGADOR
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx = VELOCIDADE_JOGADOR
        self.rect.x += dx

        for parede in self.paredes:
            if self.rect.colliderect(parede.rect):
                if dx > 0: self.rect.right = parede.rect.left
                if dx < 0: self.rect.left = parede.rect.right

        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: dy = -VELOCIDADE_JOGADOR
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy = VELOCIDADE_JOGADOR
        self.rect.y += dy

        for parede in self.paredes:
            if self.rect.colliderect(parede.rect):
                if dy > 0: self.rect.bottom = parede.rect.top
                if dy < 0: self.rect.top = parede.rect.bottom

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
        self.image.fill(COR_BAU)
        self.rect = self.image.get_rect(topleft=(x,y))

        self.itens = itens if itens else[] # operador ternário
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


class Parede(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((40, 40))
        self.image.fill((80, 80, 80))

        self.rect = self.image.get_rect(topleft=(x, y))