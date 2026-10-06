import pygame
from config import *

CACHE_IMAGENS={}
def obter_imagem(caminho):
    if caminho not in CACHE_IMAGENS:
        CACHE_IMAGENS[caminho] = pygame.image.load(caminho).convert_alpha()
    return CACHE_IMAGENS[caminho]

# sprites do 0x72 (CC0)
PASTA_0X72 = 'assets/sprites/0x72/'

def carregar_animacao(nome, quadros=4):
    return [obter_imagem(f"{PASTA_0X72}{nome}_f{i}.png") for i in range(quadros)]

CACHE_SONS={}
def obter_som(caminho):
    if caminho not in CACHE_SONS:
        CACHE_SONS[caminho] = pygame.mixer.Sound(caminho)
    return CACHE_SONS[caminho]

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, paredes, progresso):
        super().__init__()
        self.parado = carregar_animacao("knight_m_idle_anim")
        self.correndo = carregar_animacao("knight_m_run_anim")
        self.image = self.parado[0]
        self.tempo_animacao = 0
        self.virado_para_esquerda = False

        # colisao (menor que o desenho)
        self.rect = pygame.Rect(x+0.25*TAMANHO_PISO, y+0.25*TAMANHO_PISO, 0.75*TAMANHO_PISO, 0.75*TAMANHO_PISO)

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
        self.animar(dx, dy, velocidade)

    def animar(self, dx, dy, velocidade):
        if dx < 0: self.virado_para_esquerda = True
        if dx > 0: self.virado_para_esquerda = False

        quadros = self.correndo if (dx != 0 or dy != 0) else self.parado

        self.tempo_animacao += velocidade
        quadro = quadros[self.tempo_animacao // TEMPO_POR_QUADRO % len(quadros)]
        self.image = pygame.transform.flip(quadro, self.virado_para_esquerda, False)

    def desenhar(self, ecra):
        ecra.blit(self.image, self.image.get_rect(midbottom=self.rect.midbottom))

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

BAU_FECHADO = PASTA_0X72 + 'chest_full_open_anim_f0.png'
BAU_ABERTO = PASTA_0X72 + 'chest_full_open_anim_f2.png'
BAU_VAZIO = PASTA_0X72 + 'chest_empty_open_anim_f2.png'

class Bau(pygame.sprite.Sprite):
    def __init__(self, x, y, itens=None):
        super().__init__()
        self.image = obter_imagem(BAU_FECHADO)
        self.rect = self.image.get_rect(topleft=(x,y))

        self.itens = itens if itens else[]
        self.aberto = False
        self.som_abrir = obter_som("assets/sons/bau.mpeg")
        self.som_abrir.set_volume(0.15)

    def abrir(self):
        self.aberto = True
        self.atualizar_imagem()
        self.som_abrir.play()
        return self.itens

    def atualizar_imagem(self):
        if not self.aberto:
            self.image = obter_imagem(BAU_FECHADO)
        elif len(self.itens) > 0:
            self.image = obter_imagem(BAU_ABERTO)
        else:
            self.image = obter_imagem(BAU_VAZIO)

class Escada(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = obter_imagem(PASTA_0X72 + 'escada.png')
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

PAREDE_CHAO_EMBAIXO = PASTA_PAREDES + 'teto cima.png'
PAREDE_CHAO_EM_CIMA = PASTA_PAREDES + 'teto inferior.png'
PAREDE_CHAO_NA_DIREITA = PASTA_PAREDES + 'teto esquerdo.png'
PAREDE_CHAO_NA_ESQUERDA = PASTA_PAREDES + 'teto direita.png'

# Aparência de cada tipo de parede: caminho do PNG, cor, ou lista de PNGs sobrepostos.
APARENCIA_PAREDE = {
    "PILAR": [PAREDE_CHAO_EM_CIMA, PAREDE_CHAO_EMBAIXO, PAREDE_CHAO_NA_ESQUERDA, PAREDE_CHAO_NA_DIREITA],
    "PONTA_BAIXO": [PAREDE_CHAO_EMBAIXO, PAREDE_CHAO_NA_ESQUERDA, PAREDE_CHAO_NA_DIREITA],
    "PONTA_CIMA": [PAREDE_CHAO_EM_CIMA, PAREDE_CHAO_NA_ESQUERDA, PAREDE_CHAO_NA_DIREITA],
    "PONTA_DIR": [PAREDE_CHAO_EM_CIMA, PAREDE_CHAO_EMBAIXO, PAREDE_CHAO_NA_DIREITA],
    "PONTA_ESQ": [PAREDE_CHAO_EM_CIMA, PAREDE_CHAO_EMBAIXO, PAREDE_CHAO_NA_ESQUERDA],
    "FINA_HORIZONTAL": [PAREDE_CHAO_NA_ESQUERDA, PAREDE_CHAO_NA_DIREITA],
    "FINA_VERTICAL": [PAREDE_CHAO_EM_CIMA, PAREDE_CHAO_EMBAIXO],
    "CANTO_SUP_ESQ": PASTA_PAREDES + 'quina j.png',
    "CANTO_SUP_DIR": PASTA_PAREDES + 'quina l.png',
    "CANTO_INF_ESQ": PASTA_PAREDES + 'quina j invertido.png',
    "CANTO_INF_DIR": PASTA_PAREDES + 'quina l invertido.png',
    "RETA_CIMA": PAREDE_CHAO_EMBAIXO,
    "RETA_BAIXO": PAREDE_CHAO_EM_CIMA,
    "RETA_ESQ": PAREDE_CHAO_NA_DIREITA,
    "RETA_DIR": PAREDE_CHAO_NA_ESQUERDA,
    "QUINA_SUP_ESQ": PASTA_PAREDES + 'teto superior esquerdo.png',
    "QUINA_SUP_DIR": PASTA_PAREDES + 'teto superior direito.png',
    "QUINA_INF_ESQ": PASTA_PAREDES + 'teto inferior esquerdo.png',
    "QUINA_INF_DIR": PASTA_PAREDES + 'teto inferior direito.png',
    "MACICO": (23, 21, 47),  # a cor do fundo roxo
}


def sobrepor_imagens(caminhos):
    chave = "+".join(caminhos)
    if chave not in CACHE_IMAGENS:
        imagem = obter_imagem(caminhos[0]).copy()
        for caminho in caminhos[1:]:
            imagem.blit(obter_imagem(caminho), (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
        CACHE_IMAGENS[chave] = imagem
    return CACHE_IMAGENS[chave]


class Parede(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, grid_x, grid_y, matriz):
        super().__init__()
        self.tipo = tipo_parede(matriz, grid_x, grid_y)

        aparencia = APARENCIA_PAREDE[self.tipo]
        if isinstance(aparencia, str):
            self.image = obter_imagem(aparencia)
        elif isinstance(aparencia, list):
            self.image = sobrepor_imagens(aparencia)
        else:
            self.image = pygame.Surface((TAMANHO_PISO, TAMANHO_PISO))
            self.image.fill(aparencia)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))

class Piso(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = obter_imagem('assets/sprites/PNG/chão.png')
        self.rect = self.image.get_rect(topleft=(x, y))
