import pygame
import random
from game.fases.fase import Fase
from game.entidades import Jogador, Parede, Bau, Item
from ui.cores import COR_FUNDO_MASMORRA
from config import TAMANHO_PISO, COLUNAS, LINHAS



class celulaBSP:
    def __init__(self, x, y, largura, altura):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.esq = None
        self.dir = None
        self.sala = None

    def dividir(self, iteracoes):
        #se a área for menor que 7, vira sala imediatamente.
        # quanto menor o numero mais salas. se diminui muito pode quebrar
        # e tem que alterar outros parametros ao longo da funcao dividir
        if iteracoes == 0 or self.largura < 7 or self.altura < 7:
            w = random.randint(3, max(3, self.largura - 2))
            h = random.randint(3, max(3, self.altura - 2))

            px = self.x + random.randint(1, max(1, self.largura - w - 1))
            py = self.y + random.randint(1, max(1, self.altura - h - 1))

            self.sala = pygame.Rect(px, py, w, h)
            return

            # Tenta cortar no eixo mais longo, mas exige um mínimo de 8 blocos para agir
        cortou = False
        if self.largura >= 7 and self.largura >= self.altura:
            corte = random.randint(4, self.largura - 4)
            self.esq = celulaBSP(self.x, self.y, corte, self.altura)
            self.dir = celulaBSP(self.x + corte, self.y, self.largura - corte, self.altura)
            cortou = True
        elif self.altura >= 7:
            corte = random.randint(4, self.altura - 4)
            self.esq = celulaBSP(self.x, self.y, self.largura, corte)
            self.dir = celulaBSP(self.x, self.y + corte, self.largura, self.altura - corte)
            cortou = True

        # Se conseguiu cortar, prossegue com os filhos. Se falhou, força a criação da sala (iteracoes=0)
        if cortou:
            self.esq.dividir(iteracoes - 1)
            self.dir.dividir(iteracoes - 1)
        else:
            self.dividir(0)

    def aplicar_matriz(self, matriz):
        if self.sala is not None:
            for i in range(self.sala.top, self.sala.bottom):
                for j in range(self.sala.left, self.sala.right):
                    matriz[i][j] = 0

        elif self.esq is not None and self.dir is not None:
            self.esq.aplicar_matriz(matriz)
            self.dir.aplicar_matriz(matriz)

            x1, y1 = self.esq.centro()
            x2, y2 = self.dir.centro()

            inicio_x = int(min(x1, x2))
            fim_x = int(max(x1, x2))
            inicio_y = int(min(y1, y2))
            fim_y = int(max(y1, y2))

            for i in range(inicio_x, fim_x + 1):
                matriz[y1][i] = 0
            for i in range(inicio_y, fim_y + 1):
                matriz[i][x2] = 0

    def centro(self) -> tuple[int, int]:
        if self.sala is not None:
            return self.sala.center
        if self.esq is not None:
            return self.esq.centro()
        return (self.x + self.largura // 2, self.y + self.altura // 2)

    def obter_salas(self):
        if self.sala is not None:
            return [self.sala]
        salas = []
        if self.esq is not None:
            salas.extend(self.esq.obter_salas())
        if self.dir is not None:
            salas.extend(self.dir.obter_salas())
        return salas


class FaseNoite(Fase):
    def __init__(self):
        super().__init__(cor_fundo=COR_FUNDO_MASMORRA, musica='assets/sons/masmorra.mp3')

        self.grupo_baus = pygame.sprite.Group()
        self.grupo_paredes = pygame.sprite.Group()

        # O estado do jogo dita se o jogador está a andar ou a mexer no inventário
        self.estado_fase = "EXPLORANDO"
        self.bau_aberto_atualmente = None

        self.matriz_mapa = [[1 for _ in range(COLUNAS)] for _ in range(LINHAS)]

        arvore = celulaBSP(0, 0, COLUNAS, LINHAS)
        arvore.dividir(3)
        arvore.aplicar_matriz(self.matriz_mapa)

        self.salas_geradas = arvore.obter_salas()
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

        if len(self.salas_geradas) > 0:
            cx, cy = self.salas_geradas[0].center
            self.jogador = Jogador(cx * TAMANHO_PISO, cy * TAMANHO_PISO, self.grupo_paredes)
            self.grupo_sprites.add(self.jogador)

            for sala in self.salas_geradas[1:]:
                cx, cy = sala.center
                item_teste = Item("Rubi", 1, 100)
                bau = Bau(cx * TAMANHO_PISO, cy * TAMANHO_PISO, [item_teste])
                self.grupo_sprites.add(bau)
                self.grupo_baus.add(bau)

    def atualizar(self, eventos):
        if self.estado_fase == "EXPLORANDO":
            super().atualizar(eventos)

            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    self.tentar_abrir_baus()

        elif self.estado_fase == "LOTEANDO":
            for evento in eventos:
                #  ESC sai da tela do bau
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.estado_fase = "EXPLORANDO"
                    self.bau_aberto_atualmente = None

    def tentar_abrir_baus(self):
        baus_proximos = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
        for bau in baus_proximos:
            if isinstance(bau, Bau) and not bau.aberto:
                bau.abrir()
                self.bau_aberto_atualmente = bau
                self.estado_fase = "LOTEANDO"  # Altera o estado e congela o jogo

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)

        # O painel visual do inventário (HUD) que sobrepõe a masmorra
        if self.estado_fase == "LOTEANDO":
            painel = pygame.Surface((500, 400))
            painel.fill((50, 50, 60))
            ecra.blit(painel, (150, 100))