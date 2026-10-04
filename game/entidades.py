import pygame
from config import *
from ui.cores import (
    ESCADA,
    CINZA_BAU_ABERTO,
    CINZA_PAREDE,
    COR_BAU,
    COR_JOGADOR, DOURADO, COR_BAU_VAZIO, CINZA_INATIVO, COR_FUNDO_MASMORRA,
)
from utils import extrair_sprite
CACHE_IMAGENS={}
def obter_imagem(caminho):
    if caminho not in CACHE_IMAGENS:
        CACHE_IMAGENS[caminho] = pygame.image.load(caminho).convert_alpha()
    return CACHE_IMAGENS[caminho]

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, paredes):
        super().__init__()
        self.image = pygame.Surface((0.75*TAMANHO_PISO, 0.75*TAMANHO_PISO))
        self.image.fill(COR_JOGADOR)
        self.rect = self.image.get_rect(topleft=(x+0.25*TAMANHO_PISO,y+0.25*TAMANHO_PISO)) # colisao

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
        self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
        self.image.fill(COR_BAU)
        self.rect = self.image.get_rect(topleft=(x,y))

        self.itens = itens if itens else[]
        self.aberto = False
        self.som_abrir = pygame.mixer.Sound("assets/sons/bau.mpeg")
        self.som_abrir.set_volume(0.15)

    def abrir(self):
        self.aberto = True
        self.atualizar_cor()
        self.som_abrir.play()
        self.image.fill(CINZA_BAU_ABERTO)
        return self.itens

    def atualizar_cor(self):
        if not self.aberto:
            self.image.fill(DOURADO)
        elif len(self.itens) > 0:
            self.image.fill(CINZA_BAU_ABERTO)
        else:
            self.image.fill(COR_BAU_VAZIO)

class Escada(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
        self.image.fill(CINZA_INATIVO)
        self.rect = self.image.get_rect(topleft=(x, y))


class Parede(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, grid_x, grid_y, matriz):
        super().__init__()

        linhas = len(matriz)
        colunas = len(matriz[0])

        def eh_chao(x, y):
            if 0 <= x < colunas and 0 <= y < linhas:
                return matriz[y][x] == 0
            return False

        # 1. Verificação Ortogonal (Cruz)
        c_cima = eh_chao(grid_x, grid_y - 1)
        c_baixo = eh_chao(grid_x, grid_y + 1)
        c_esq = eh_chao(grid_x - 1, grid_y)
        c_dir = eh_chao(grid_x + 1, grid_y)

        # 2. Verificação Diagonal (X)
        c_ce = eh_chao(grid_x - 1, grid_y - 1)  # Cima-Esquerda
        c_cd = eh_chao(grid_x + 1, grid_y - 1)  # Cima-Direita
        c_be = eh_chao(grid_x - 1, grid_y + 1)  # Baixo-Esquerda
        c_bd = eh_chao(grid_x + 1, grid_y + 1)  # Baixo-Direita


        pasta = 'assets/sprites/PNG/'
        img_path = None
        cor = None
        # =======================================================
        # MAPEAMENTO DE CORES (Substitua as cores por img_path depois)
        # =======================================================

        # --- 1. PILAR ISOLADO (Chão por todos os lados) ---
        if c_cima and c_baixo and c_esq and c_dir:
            cor = (255, 255, 255)  # BRANCO

        # --- 2. PONTAS / BECOS SEM SAÍDA (Chão em 3 lados) ---
        elif c_esq and c_dir and c_baixo and not c_cima:
            cor = (255, 100, 100)  # VERMELHO CLARO: Ponta para baixo
        elif c_esq and c_dir and c_cima and not c_baixo:
            cor = (100, 255, 100)  # VERDE CLARO: Ponta para cima
        elif c_cima and c_baixo and c_dir and not c_esq:
            cor = (100, 100, 255)  # AZUL CLARO: Ponta para a direita
        elif c_cima and c_baixo and c_esq and not c_dir:
            cor = (255, 255, 100)  # AMARELO CLARO: Ponta para a esquerda

        # --- 3. CORREDORES / PAREDES FINAS (Chão em 2 lados opostos) ---
        elif c_esq and c_dir and not c_cima and not c_baixo:
            cor = (255, 150, 0)  # LARANJA: Parede fina horizontal (Caminho Cima/Baixo)
        elif c_cima and c_baixo and not c_esq and not c_dir:
            cor = (0, 255, 150)  # VERDE ÁGUA: Parede fina vertical (Caminho Esq/Dir)

        # --- 4. CANTOS EXTERNOS DAS SALAS (Chão em 2 lados adjacentes) ---
        elif c_baixo and c_dir and not c_cima and not c_esq:
            cor = (255, 0, 0)  # VERMELHO: Canto Superior Esquerdo
        elif c_baixo and c_esq and not c_cima and not c_dir:
            cor = (0, 255, 0)  # VERDE: Canto Superior Direito
        elif c_cima and c_dir and not c_baixo and not c_esq:
            cor = (0, 0, 255)  # AZUL: Canto Inferior Esquerdo
        elif c_cima and c_esq and not c_baixo and not c_dir:
            cor = (255, 255, 0)  # AMARELO: Canto Inferior Direito

        # --- 5. PAREDES RETAS DAS SALAS (Chão em apenas 1 lado) ---
        elif c_baixo:
            img_path = pasta + 'teto cima.png'# VERMELHO ESCURO: Parede Norte (Onde se vê os tijolos)
        elif c_cima:
            img_path = pasta + 'teto inferior.png'  # VERDE ESCURO: Parede Sul (Borda do teto)
        elif c_dir:
            img_path = pasta + 'teto esquerdo.png'  # AZUL ESCURO: Parede Oeste (Borda do teto esquerda)
        elif c_esq:
            img_path = pasta + 'teto direita.png'  # AMARELO ESCURO: Parede Leste (Borda do teto direita)

        # --- 6. QUINAS INTERNAS E MIOLO PROFUNDO (Sem chão encostado em cruz) ---
        else:
            # Apesar de ser maciço, pode ter chão nas diagonais formando Quinas Internas
            if c_bd:
                img_path = pasta + 'teto superior esquerdo.png'  # MAGENTA: Quina Interna Sup Esq
            elif c_be:
                img_path = pasta + 'teto superior direito.png'  # CIANO: Quina Interna Sup Dir
            elif c_cd:
                img_path = pasta + 'teto inferior esquerdo.png'  # ROXO: Quina Interna Inf Esq
            elif c_ce:
                img_path = pasta + 'teto inferior direito.png'  # VERDE-AZULADO (Teal): Quina Interna Inf Dir

            # Se não houver chão em lado rigorosamente nenhum, é o bloco de preenchimento maciço
            else:
                # Detalhe do seu jogo: Se este bloco for o telhado diretamente acima dos tijolos,
                # pintamos de uma cor. Se for mais profundo, pintamos da cor do fundo do jogo.

                cor = (23,21,47)  # a cor do fundo roxo: cor = (23, 21, 47)

        if img_path:
            self.image = obter_imagem(img_path)
        else:
            self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
            self.image.fill(cor)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))

class Piso(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = obter_imagem('assets/sprites/PNG/chão.png')
        self.rect = self.image.get_rect(topleft=(x, y))