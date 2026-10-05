import pygame
from config import *
from ui.cores import (
    CINZA_BAU_ABERTO,
    COR_BAU,
    COR_JOGADOR, COR_BAU_VAZIO, CINZA_INATIVO,
)

CACHE_IMAGENS={}
def obter_imagem(caminho):
    if caminho not in CACHE_IMAGENS:
        CACHE_IMAGENS[caminho] = pygame.image.load(caminho).convert_alpha()
    return CACHE_IMAGENS[caminho]

CACHE_SONS={}
def obter_som(caminho):
    if caminho not in CACHE_SONS:
        CACHE_SONS[caminho] = pygame.mixer.Sound(caminho)
    return CACHE_SONS[caminho]

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, paredes, progresso):
        super().__init__()
        # PLACEHOLDER: trocar por sprite
        self.image = pygame.Surface((0.75*TAMANHO_PISO, 0.75*TAMANHO_PISO))
        self.image.fill(COR_JOGADOR)
        self.rect = self.image.get_rect(topleft=(x+0.25*TAMANHO_PISO,y+0.25*TAMANHO_PISO)) # colisao

        self.paredes = paredes # pra colisao
        self.progresso = progresso # pra saber o peso da mochila

    def velocidade(self):
        if self.progresso.esta_pesado():
            return VELOCIDADE_LENTA
        return VELOCIDADE_JOGADOR

    def update(self):
        teclas = pygame.key.get_pressed()
        velocidade = self.velocidade()

        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx = -velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx = velocidade
        self.rect.x += dx

        for parede in self.paredes:
            if self.rect.colliderect(parede.rect):
                if dx > 0: self.rect.right = parede.rect.left
                if dx < 0: self.rect.left = parede.rect.right

        dy = 0
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: dy = -velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy = velocidade
        self.rect.y += dy

        for parede in self.paredes:
            if self.rect.colliderect(parede.rect):
                if dy > 0: self.rect.bottom = parede.rect.top
                if dy < 0: self.rect.top = parede.rect.bottom

        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA_VIRTUAL, ALTURA_VIRTUAL))

class Item:
    def __init__(self, nome, peso, valor, raridade="COMUM", a_granel=False, texto=None):
        self.nome = nome
        self.peso = peso
        self.valor = valor
        self.raridade = raridade

        # a granel: dá para levar só uma parte (1kg de cada vez)
        self.a_granel = a_granel

        # pergaminho: item com uma palavra escondida, decifrada no mercador
        self.texto = texto
        self.decifrado = False

    def eh_pergaminho(self):
        return self.texto is not None

    def esta_selado(self):
        return self.eh_pergaminho() and not self.decifrado

    def descricao(self):
        if self.esta_selado():
            return f"{self.nome} ({self.peso}kg) $???"
        return f"{self.nome} ({self.peso}kg) ${self.valor}"

class Bau(pygame.sprite.Sprite):
    def __init__(self, x, y, itens=None):
        super().__init__()
        # PLACEHOLDER: trocar por sprite
        self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
        self.image.fill(COR_BAU)
        self.rect = self.image.get_rect(topleft=(x,y))

        self.itens = itens if itens else[]
        self.aberto = False
        self.som_abrir = obter_som("assets/sons/bau.mpeg")
        self.som_abrir.set_volume(0.15)

    def abrir(self):
        self.aberto = True
        self.atualizar_cor()
        self.som_abrir.play()
        return self.itens

    def atualizar_cor(self):
        if not self.aberto:
            self.image.fill(COR_BAU)
        elif len(self.itens) > 0:
            self.image.fill(CINZA_BAU_ABERTO)
        else:
            self.image.fill(COR_BAU_VAZIO)

class Escada(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        # PLACEHOLDER: trocar por sprite
        self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
        self.image.fill(CINZA_INATIVO)
        self.rect = self.image.get_rect(topleft=(x, y))


def tipo_parede(matriz, x, y):
    """Olha os vizinhos da parede em (x, y) e devolve o nome do tipo dela."""
    linhas = len(matriz)
    colunas = len(matriz[0])

    def eh_chao(x, y):
        if 0 <= x < colunas and 0 <= y < linhas:
            return matriz[y][x] == 0
        return False

    # 1. Verificação Ortogonal (Cruz)
    c_cima = eh_chao(x, y - 1)
    c_baixo = eh_chao(x, y + 1)
    c_esq = eh_chao(x - 1, y)
    c_dir = eh_chao(x + 1, y)

    # 2. Verificação Diagonal (X)
    c_ce = eh_chao(x - 1, y - 1)  # Cima-Esquerda
    c_cd = eh_chao(x + 1, y - 1)  # Cima-Direita
    c_be = eh_chao(x - 1, y + 1)  # Baixo-Esquerda
    c_bd = eh_chao(x + 1, y + 1)  # Baixo-Direita

    # --- 1. PILAR ISOLADO (Chão por todos os lados) ---
    if c_cima and c_baixo and c_esq and c_dir:
        return "PILAR"

    # --- 2. PONTAS / BECOS SEM SAÍDA (Chão em 3 lados) ---
    if c_esq and c_dir and c_baixo:
        return "PONTA_BAIXO"
    if c_esq and c_dir and c_cima:
        return "PONTA_CIMA"
    if c_cima and c_baixo and c_dir:
        return "PONTA_DIR"
    if c_cima and c_baixo and c_esq:
        return "PONTA_ESQ"

    # --- 3. CORREDORES / PAREDES FINAS (Chão em 2 lados opostos) ---
    if c_esq and c_dir:
        return "FINA_HORIZONTAL"  # chão à esquerda e à direita
    if c_cima and c_baixo:
        return "FINA_VERTICAL"    # chão em cima e embaixo

    # --- 4. CANTOS EXTERNOS DAS SALAS (Chão em 2 lados adjacentes) ---
    if c_baixo and c_dir:
        return "CANTO_SUP_ESQ"
    if c_baixo and c_esq:
        return "CANTO_SUP_DIR"
    if c_cima and c_dir:
        return "CANTO_INF_ESQ"
    if c_cima and c_esq:
        return "CANTO_INF_DIR"

    # --- 5. PAREDES RETAS DAS SALAS (Chão em apenas 1 lado) ---
    if c_baixo:
        return "RETA_CIMA"   # Parede Norte (Onde se vê os tijolos)
    if c_cima:
        return "RETA_BAIXO"  # Parede Sul (Borda do teto)
    if c_dir:
        return "RETA_ESQ"    # Parede Oeste (Borda do teto esquerda)
    if c_esq:
        return "RETA_DIR"    # Parede Leste (Borda do teto direita)

    # --- 6. QUINAS INTERNAS (Sem chão encostado em cruz, só na diagonal) ---
    if c_bd:
        return "QUINA_SUP_ESQ"
    if c_be:
        return "QUINA_SUP_DIR"
    if c_cd:
        return "QUINA_INF_ESQ"
    if c_ce:
        return "QUINA_INF_DIR"

    # --- 7. MIOLO PROFUNDO (Nenhum chão por perto) ---
    return "MACICO"


PASTA_PAREDES = 'assets/sprites/PNG/'

# Aparência de cada tipo de parede: caminho do PNG ou, enquanto não há sprite, uma cor.
# PLACEHOLDER: trocar as cores por sprites.
APARENCIA_PAREDE = {
    "PILAR": (255, 255, 255),
    "PONTA_BAIXO": (255, 100, 100),
    "PONTA_CIMA": (100, 255, 100),
    "PONTA_DIR": (100, 100, 255),
    "PONTA_ESQ": (255, 255, 100),
    "FINA_HORIZONTAL": (255, 150, 0),
    "FINA_VERTICAL": (0, 255, 150),
    "CANTO_SUP_ESQ": PASTA_PAREDES + 'quina j.png',
    "CANTO_SUP_DIR": PASTA_PAREDES + 'quina l.png',
    "CANTO_INF_ESQ": PASTA_PAREDES + 'quina j invertido.png',
    "CANTO_INF_DIR": PASTA_PAREDES + 'quina l invertido.png',
    "RETA_CIMA": PASTA_PAREDES + 'teto cima.png',
    "RETA_BAIXO": PASTA_PAREDES + 'teto inferior.png',
    "RETA_ESQ": PASTA_PAREDES + 'teto esquerdo.png',
    "RETA_DIR": PASTA_PAREDES + 'teto direita.png',
    "QUINA_SUP_ESQ": PASTA_PAREDES + 'teto superior esquerdo.png',
    "QUINA_SUP_DIR": PASTA_PAREDES + 'teto superior direito.png',
    "QUINA_INF_ESQ": PASTA_PAREDES + 'teto inferior esquerdo.png',
    "QUINA_INF_DIR": PASTA_PAREDES + 'teto inferior direito.png',
    "MACICO": (23, 21, 47),  # a cor do fundo roxo
}


class Parede(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, grid_x, grid_y, matriz):
        super().__init__()
        self.tipo = tipo_parede(matriz, grid_x, grid_y)

        aparencia = APARENCIA_PAREDE[self.tipo]
        if isinstance(aparencia, str):
            self.image = obter_imagem(aparencia)
        else:
            self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
            self.image.fill(aparencia)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))

class Piso(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = obter_imagem('assets/sprites/PNG/chão.png')
        self.rect = self.image.get_rect(topleft=(x, y))
