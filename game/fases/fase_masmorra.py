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
    VERDE,
    VERMELHO,
)
from ui.painel import desenhar_barra, desenhar_painel, desenhar_lista_itens
from ui.texto import desenhar_texto, desenhar_texto_centralizado, desenhar_texto_direita
from config import TAMANHO_PISO, COLUNAS, LINHAS

# painel de mochila/bau
ALTURA_PAINEL = 268
ALTURA_RODAPE = 56
Y_LISTA = 52
ITENS_NO_PAINEL = 7  # itens visiveis


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
        self.aviso = None

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

        # desenhado por ultimo, na frente dos baus
        x, y = self.posicao_jogador
        self.jogador = Jogador(x * TAMANHO_PISO, y * TAMANHO_PISO, self.grupo_paredes, self.progresso)

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
            self.jogador.update()

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
                    self.aviso = None

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
                        ultimo = max(0, len(self.lista_focada()) - 1)
                        self.indice_selecionado = min(ultimo, self.indice_selecionado + 1)
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

    def lista_focada(self):
        if self.painel_focado == "BAU":
            return self.bau_aberto_atualmente.itens
        return self.progresso.inventario

    def tentar_abrir_baus(self):
        baus_proximos = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
        for bau in baus_proximos:
            if not bau.aberto:
                bau.abrir()
            self.bau_aberto_atualmente = bau
            self.estado_fase = "LOTEANDO"
            self.painel_focado = "BAU"
            self.indice_selecionado = 0
            self.aviso = None
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

        espaco_livre = self.progresso.espaco_livre()
        if destino is mochila and peso_movido > espaco_livre:
            self.aviso = f"Não cabe: precisa de {peso_movido}kg e só restam {espaco_livre}kg na mochila."
            return

        adicionar_item(destino, retirar_item(origem, self.indice_selecionado))
        self.indice_selecionado = max(0, min(self.indice_selecionado, len(origem) - 1))
        self.bau_aberto_atualmente.atualizar_imagem()

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
        titulo = f"Mochila {self.progresso.peso_total()}/{self.progresso.capacidade_maxima}kg"
        if self.progresso.esta_pesado():
            titulo += " LENTO"
        return titulo

    def dica_da_mochila(self):
        progresso = self.progresso

        if self.aviso:
            return self.aviso, VERMELHO

        if self.estado_fase == "LOTEANDO" and self.lista_focada():
            item = self.lista_focada()[self.indice_selecionado]
            if item.a_granel:
                return f"A granel: cada [ESPAÇO] leva 1kg (${item.valor // item.peso} por kg).", BRANCO

        if progresso.esta_pesado():
            return f"Mochila pesada: acima de {progresso.peso_leve()}kg você anda LENTO.", VERMELHO
        return f"Cabem {progresso.capacidade_maxima}kg. Acima de {progresso.peso_leve()}kg você anda lento.", CINZA_INATIVO

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)
        self.jogador.desenhar(ecra)

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
        largura_painel = 560
        x_painel, y_painel = desenhar_painel(ecra, largura_painel, ALTURA_PAINEL)

        meio = largura_painel // 2
        largura_coluna = meio - 40

        y_rodape = y_painel + ALTURA_PAINEL - ALTURA_RODAPE
        pygame.draw.line(ecra, COR_DIVISORIA_PAINEL, (x_painel + meio, y_painel + 2),
                         (x_painel + meio, y_rodape), 2)

        cor_mochila = DOURADO if self.painel_focado == "MOCHILA" else CINZA_INATIVO
        cor_bau = DOURADO if self.painel_focado == "BAU" else CINZA_INATIVO

        selecionado_mochila = self.indice_selecionado if self.painel_focado == "MOCHILA" else None
        selecionado_bau = self.indice_selecionado if self.painel_focado == "BAU" else None

        self.desenhar_coluna_mochila(ecra, x_painel + 20, y_painel, largura_coluna, cor_mochila, selecionado_mochila)

        x_bau = x_painel + meio + 20
        desenhar_texto(ecra, "Baú", x_bau, y_painel + 10, self.fonte_titulo, cor_bau)
        self.desenhar_itens(ecra, self.bau_aberto_atualmente.itens, x_bau, y_painel + Y_LISTA,
                            largura_coluna, selecionado_bau)

        self.desenhar_rodape(ecra, x_painel, y_rodape, largura_painel,
                             "[SETAS] Navegar   [TAB] Trocar de lado   [ESPAÇO] Transferir   [ESC] Fechar")

    def desenhar_painel_mochila(self, ecra):
        largura_painel = 400
        x_painel, y_painel = desenhar_painel(ecra, largura_painel, ALTURA_PAINEL)

        self.desenhar_coluna_mochila(ecra, x_painel + 20, y_painel, largura_painel - 40, DOURADO,
                                     self.indice_selecionado)

        self.desenhar_rodape(ecra, x_painel, y_painel + ALTURA_PAINEL - ALTURA_RODAPE, largura_painel,
                             "[SETAS] Navegar   [E / ESC] Fechar")

    def desenhar_coluna_mochila(self, ecra, x, y_painel, largura, cor_titulo, selecionado):
        progresso = self.progresso
        pesado = progresso.esta_pesado()

        desenhar_texto(ecra, "Mochila", x, y_painel + 10, self.fonte_titulo, cor_titulo)
        desenhar_texto_direita(ecra, f"{progresso.peso_total()}/{progresso.capacidade_maxima}kg",
                               x + largura, y_painel + 10, self.fonte_titulo, VERMELHO if pesado else BRANCO)

        y_barra = y_painel + 36
        desenhar_barra(ecra, x, y_barra, largura, 6, progresso.peso_total() / progresso.capacidade_maxima,
                       VERMELHO if pesado else VERDE)

        # inicio da zona pesada
        x_risco = x + largura * progresso.peso_leve() // progresso.capacidade_maxima
        pygame.draw.line(ecra, BRANCO, (x_risco, y_barra - 2), (x_risco, y_barra + 7))

        self.desenhar_itens(ecra, progresso.inventario, x, y_painel + Y_LISTA, largura, selecionado)

    def desenhar_itens(self, ecra, itens, x, y, largura, selecionado):
        if len(itens) == 0:
            desenhar_texto(ecra, "(vazio)", x, y, self.fonte_texto, CINZA_INATIVO)
            return

        desenhar_lista_itens(ecra, self.fonte_texto, itens, x, y, largura + 10, selecionado, ITENS_NO_PAINEL)

    def desenhar_rodape(self, ecra, x_painel, y_rodape, largura_painel, teclas):
        pygame.draw.line(ecra, COR_DIVISORIA_PAINEL, (x_painel + 2, y_rodape),
                         (x_painel + largura_painel - 3, y_rodape), 2)

        dica, cor = self.dica_da_mochila()
        desenhar_texto_centralizado(ecra, dica, y_rodape + 9, self.fonte_texto, cor)
        desenhar_texto_centralizado(ecra, teclas, y_rodape + 31, self.fonte_texto, CINZA_INATIVO)
