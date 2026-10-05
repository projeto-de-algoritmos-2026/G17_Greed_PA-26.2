import pygame
import random
from game.estado import EstadoJogo
from game.fases.fase import Fase
from game.entidades import Jogador, Parede, Bau, Escada, Piso
from game.itens import sortear_loot, adicionar_item, retirar_item, separar_granel
from game.mapas import ANDAR_1, itens_andar_1
from ui.cores import (
    BRANCO,
    CINZA_INATIVO,
    COR_DIVISORIA_PAINEL,
    COR_FUNDO_MASMORRA,
    DOURADO,
    VERMELHO,
)
from ui.painel import desenhar_painel, desenhar_lista_itens
from ui.texto import desenhar_texto
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
        # se a área for menor que esse valor(altura ou largura), vira sala imediatamente.
        if iteracoes == 0 or self.largura < 8 or self.altura < 8:
            w = random.randint(4, max(4, self.largura - 2))
            h = random.randint(4, max(4, self.altura - 2))

            px = self.x + random.randint(1, max(1, self.largura - w - 1))
            py = self.y + random.randint(1, max(1, self.altura - h - 1))

            self.sala = pygame.Rect(px, py, w, h)
            return


        cortou = False
        if self.largura >= 10 and self.largura >= self.altura:
            corte = random.randint(4, self.largura - 4)
            self.esq = celulaBSP(self.x, self.y, corte, self.altura)
            self.dir = celulaBSP(self.x + corte, self.y, self.largura - corte, self.altura)
            cortou = True
        elif self.altura >= 10:
            corte = random.randint(4, self.altura - 4)
            self.esq = celulaBSP(self.x, self.y, self.largura, corte)
            self.dir = celulaBSP(self.x, self.y + corte, self.largura, self.altura - corte)
            cortou = True

        if cortou:
            self.esq.dividir(iteracoes - 1)
            self.dir.dividir(iteracoes - 1)
        else:
            self.dividir(0)

    def aplicar_matriz(self, matriz):
        if self.sala is not None:
            for i in range(self.sala.top, self.sala.bottom):
                for j in range(self.sala.left, self.sala.right):
                    if 0 < i < LINHAS - 1 and 0 < j < COLUNAS - 1:
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

            largura_corredor = random.randint(1, 2)

            for i in range(inicio_x, fim_x + 1):
                for w in range(largura_corredor):
                    if 0 < y1 + w < LINHAS - 1 and 0 < i < COLUNAS - 1:
                        matriz[y1 + w][i] = 0

            for i in range(inicio_y, fim_y + 1):
                for w in range(largura_corredor):
                    if 0 < i < LINHAS - 1 and 0 < x2 + w < COLUNAS - 1:
                        matriz[i][x2 + w] = 0

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




class FaseMasmorra(Fase):
    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MASMORRA, musica='assets/sons/masmorra.mp3')

        self.grupo_baus = pygame.sprite.Group()
        self.grupo_paredes = pygame.sprite.Group()
        self.grupo_escada = pygame.sprite.GroupSingle()
        self.escada_gerada = False

        self.estado_fase = "EXPLORANDO"
        self.bau_aberto_atualmente = None

        self.painel_focado = "MOCHILA"
        self.indice_selecionado = 0

        # O primeiro andar é sempre o mesmo; os outros são sorteados
        if self.progresso.andar == 1:
            self.montar_andar_fixo()
        else:
            self.montar_andar_aleatorio()

        self.construir_mapa()
        self.guardar_itens_do_andar()
        self.gerar_escada()  # só acontece aqui se o andar não tiver nenhum baú

    def montar_andar_fixo(self):
        self.matriz_mapa = [[1 if letra == "#" else 0 for letra in linha] for linha in ANDAR_1]

        itens_dos_baus = itens_andar_1()
        self.baus_do_andar = []  # cada baú: (x, y, itens)

        for y, linha in enumerate(ANDAR_1):
            for x, letra in enumerate(linha):
                if letra == "J":
                    self.posicao_jogador = (x, y)
                elif letra == "B":
                    itens = itens_dos_baus[len(self.baus_do_andar)]
                    self.baus_do_andar.append((x, y, itens))

    def montar_andar_aleatorio(self):
        self.matriz_mapa = [[1 for _ in range(COLUNAS)] for _ in range(LINHAS)]

        arvore = celulaBSP(0, 0, COLUNAS, LINHAS)
        arvore.dividir(4)
        arvore.aplicar_matriz(self.matriz_mapa)

        # O jogador nasce na primeira sala; cada uma das outras ganha um baú
        salas = arvore.obter_salas()
        self.posicao_jogador = salas[0].center

        self.baus_do_andar = []
        for sala in salas[1:]:
            x, y = sala.center
            self.baus_do_andar.append((x, y, sortear_loot(self.progresso.nivel_sorte)))

    def construir_mapa(self):
        for y, linha in enumerate(self.matriz_mapa):
            for x, valor in enumerate(linha):
                pos_x = x * TAMANHO_PISO
                pos_y = y * TAMANHO_PISO

                if valor == 0:
                    piso = Piso(pos_x, pos_y)
                    self.grupo_sprites.add(piso)

                elif valor == 1:
                    parede = Parede(pos_x, pos_y, x, y, self.matriz_mapa)
                    self.grupo_sprites.add(parede)
                    self.grupo_paredes.add(parede)

        for x, y, itens in self.baus_do_andar:
            bau = Bau(x * TAMANHO_PISO, y * TAMANHO_PISO, itens)
            self.grupo_sprites.add(bau)
            self.grupo_baus.add(bau)

        x, y = self.posicao_jogador
        self.jogador = Jogador(x * TAMANHO_PISO, y * TAMANHO_PISO, self.grupo_paredes, self.progresso)
        self.grupo_sprites.add(self.jogador)

    def guardar_itens_do_andar(self):
        """Guarda tudo que o jogador poderia levar deste andar (baús + o que já
        estava na mochila). A tela de resultado roda o algoritmo guloso nessa lista."""
        todos = list(self.progresso.inventario)
        for bau in self.grupo_baus:
            todos.extend(bau.itens)

        sem_pergaminhos = [item for item in todos if not item.eh_pergaminho()]
        self.progresso.itens_do_andar = separar_granel(sem_pergaminhos)

    def atualizar(self, eventos):
        if self.estado_fase == "EXPLORANDO":
            super().atualizar(eventos)

            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    if self.escada_gerada and pygame.sprite.spritecollideany(self.jogador, self.grupo_escada):
                        self.proximo_estado = EstadoJogo.RESULTADO
                    else:
                        self.tentar_abrir_baus()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
                    self.ver_mochila()

        elif self.estado_fase == "LOTEANDO":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.estado_fase = "EXPLORANDO"
                        self.bau_aberto_atualmente = None
                        self.gerar_escada()

                    elif evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT or evento.key == pygame.K_TAB:
                        self.painel_focado = "MOCHILA" if self.painel_focado == "BAU" else "BAU"
                        self.indice_selecionado = 0
                    elif evento.key == pygame.K_UP:
                        self.indice_selecionado = max(0, self.indice_selecionado - 1)
                    elif evento.key == pygame.K_DOWN:
                        lista_atual = self.bau_aberto_atualmente.itens if self.painel_focado == "BAU" else self.progresso.inventario
                        self.indice_selecionado = min(max(0, len(lista_atual) - 1), self.indice_selecionado + 1)
                    elif evento.key == pygame.K_SPACE:
                        self.transferir_item()

        elif self.estado_fase == "INVENTARIO":
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_e:
                        self.estado_fase = "EXPLORANDO"
                    elif evento.key == pygame.K_UP:
                        self.indice_selecionado = max(0, self.indice_selecionado - 1)
                    elif evento.key == pygame.K_DOWN:
                        if len(self.progresso.inventario) > 0:
                            self.indice_selecionado = min(len(self.progresso.inventario) - 1, self.indice_selecionado + 1)

    def tentar_abrir_baus(self):
        baus_proximos = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
        for bau in baus_proximos:
            if not bau.aberto:
                bau.abrir()
            self.bau_aberto_atualmente = bau
            self.estado_fase = "LOTEANDO"
            self.painel_focado = "BAU"
            self.indice_selecionado = 0
            break

    def ver_mochila(self):
        if self.estado_fase == "EXPLORANDO":
            self.estado_fase = "INVENTARIO"
            self.painel_focado = "MOCHILA"
            self.indice_selecionado = 0
            self.bau_aberto_atualmente = None

    def transferir_item(self):
        mochila = self.progresso.inventario
        bau = self.bau_aberto_atualmente.itens

        if self.painel_focado == "BAU":
            origem, destino = bau, mochila
        else:
            origem, destino = mochila, bau

        if len(origem) == 0:
            return

        item = origem[self.indice_selecionado]
        peso_movido = 1 if item.a_granel else item.peso  # item a granel vai 1kg por vez

        if destino is mochila:
            if self.progresso.peso_total() + peso_movido > self.progresso.limite_de_peso():
                return  # não aguenta mais peso

        adicionar_item(destino, retirar_item(origem, self.indice_selecionado))
        self.indice_selecionado = max(0, min(self.indice_selecionado, len(origem) - 1))
        self.bau_aberto_atualmente.atualizar_cor()

    def gerar_escada(self):
        if self.escada_gerada:
            return

        todos_abertos = True
        for bau in self.grupo_baus:
            if not bau.aberto:
                todos_abertos = False
                break

        if todos_abertos:
            ocupados = [(x, y) for x, y, itens in self.baus_do_andar]

            pisos_livres = []
            for y in range(LINHAS):
                for x in range(COLUNAS):
                    if self.matriz_mapa[y][x] == 0 and (x, y) not in ocupados:
                        pisos_livres.append((x, y))

            if pisos_livres:
                x_escolhido, y_escolhido = random.choice(pisos_livres)
                escada = Escada(x_escolhido * TAMANHO_PISO, y_escolhido * TAMANHO_PISO)
                self.grupo_sprites.add(escada)
                self.grupo_escada.add(escada)
                self.escada_gerada = True

    def titulo_mochila(self):
        peso = self.progresso.peso_total()
        titulo = f"Mochila ({peso}/{self.progresso.capacidade_maxima}kg)"
        if self.progresso.esta_pesado():
            titulo += " LENTO"
        return titulo

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)

        if self.estado_fase == "EXPLORANDO":
            self.desenhar_informacoes(ecra)
        elif self.estado_fase == "LOTEANDO":
            self.desenhar_painel_bau(ecra)
        elif self.estado_fase == "INVENTARIO":
            self.desenhar_painel_mochila(ecra)

    def desenhar_informacoes(self, ecra):
        texto = f"Andar {self.progresso.andar} | Ouro {self.progresso.ouro} | {self.titulo_mochila()}"
        cor = VERMELHO if self.progresso.esta_pesado() else BRANCO
        desenhar_texto(ecra, texto, 6, 2, self.fonte_texto, cor)

        if self.escada_gerada:
            desenhar_texto(ecra, "A escada apareceu! [ESPAÇO] em cima dela para descer", 6, 18,
                           self.fonte_texto, DOURADO)

    def desenhar_painel_bau(self, ecra):
        largura_painel, altura_painel = 560, 260
        x_painel, y_painel = desenhar_painel(ecra, largura_painel, altura_painel)

        meio = largura_painel // 2
        pygame.draw.line(ecra, COR_DIVISORIA_PAINEL, (x_painel + meio, y_painel),
                         (x_painel + meio, y_painel + altura_painel - 1), 2)

        cor_mochila = DOURADO if self.painel_focado == "MOCHILA" else CINZA_INATIVO
        cor_bau = DOURADO if self.painel_focado == "BAU" else CINZA_INATIVO

        desenhar_texto(ecra, self.titulo_mochila(), x_painel + 20, y_painel + 10, self.fonte_titulo, cor_mochila)
        desenhar_texto(ecra, "Bau", x_painel + meio + 20, y_painel + 10, self.fonte_titulo, cor_bau)

        selecionado_mochila = self.indice_selecionado if self.painel_focado == "MOCHILA" else None
        selecionado_bau = self.indice_selecionado if self.painel_focado == "BAU" else None

        desenhar_lista_itens(ecra, self.fonte_texto, self.progresso.inventario,
                             x_painel + 20, y_painel + 45, meio - 30, selecionado_mochila)
        desenhar_lista_itens(ecra, self.fonte_texto, self.bau_aberto_atualmente.itens,
                             x_painel + meio + 20, y_painel + 45, meio - 30, selecionado_bau)

        aviso = f"Acima de {self.progresso.capacidade_maxima}kg você anda lento. Máximo: {self.progresso.limite_de_peso()}kg"
        desenhar_texto(ecra, aviso, x_painel + 20, y_painel + altura_painel - 45, self.fonte_texto, CINZA_INATIVO)
        desenhar_texto(ecra, "[SETAS] Navegar | [ESPAÇO] Transferir | [ESC] Fechar",
                       x_painel + 20, y_painel + altura_painel - 25, self.fonte_texto, CINZA_INATIVO)

    def desenhar_painel_mochila(self, ecra):
        largura_painel, altura_painel = 300, 260
        x_painel, y_painel = desenhar_painel(ecra, largura_painel, altura_painel)

        desenhar_texto(ecra, self.titulo_mochila(), x_painel + 20, y_painel + 10, self.fonte_titulo, DOURADO)

        desenhar_lista_itens(ecra, self.fonte_texto, self.progresso.inventario,
                             x_painel + 20, y_painel + 45, largura_painel - 30, self.indice_selecionado)

        desenhar_texto(ecra, "[SETAS] Navegar | [E/ESC] Fechar",
                       x_painel + 20, y_painel + altura_painel - 25, self.fonte_texto, CINZA_INATIVO)
