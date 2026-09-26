import pygame
import random
from game.fases.fase import Fase
from game.entidades import Jogador, Parede, Bau, Item, Escada
from ui.cores import (
    BRANCO,
    CINZA_INATIVO,
    COR_BORDA_PAINEL,
    COR_CURSOR,
    COR_DIVISORIA_PAINEL,
    COR_FUNDO_MASMORRA,
    COR_FUNDO_PAINEL,
    DOURADO,
)
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
        self.fonte_titulo = pygame.font.Font('assets/fonts/DigitalDisco.ttf', 32)
        self.fonte_texto = pygame.font.Font('assets/fonts/DigitalDisco.ttf', 24)

        self.grupo_baus = pygame.sprite.Group()
        self.grupo_paredes = pygame.sprite.Group()


        self.estado_fase = "EXPLORANDO"
        self.bau_aberto_atualmente = None

        self.painel_focado = "MOCHILA"
        self.indice_selecionado = 0

        self.matriz_mapa = [[1 for _ in range(COLUNAS)] for _ in range(LINHAS)]

        arvore = celulaBSP(0, 0, COLUNAS, LINHAS)
        arvore.dividir(3)
        arvore.aplicar_matriz(self.matriz_mapa)

        self.salas_geradas = arvore.obter_salas()
        self.construir_mapa()

        self.escada_gerada = False
        self.grupo_escada = pygame.sprite.GroupSingle()

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
                itens_sorteados = self.gerar_loot_aleatorio()
                bau = Bau(cx * TAMANHO_PISO, cy * TAMANHO_PISO, itens_sorteados)
                self.grupo_sprites.add(bau)
                self.grupo_baus.add(bau)

    def atualizar(self, eventos):
        if self.estado_fase == "EXPLORANDO":
            super().atualizar(eventos)

            for evento in eventos:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    if self.escada_gerada and pygame.sprite.spritecollideany(self.jogador, self.grupo_escada):
                        print("Avançando para a próxima fase!!!")
                        #COLOCAR FUNCAO DE AVANÇAR
                    else:
                        self.tentar_abrir_baus()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_e:
                    self.ver_mochila()

        elif self.estado_fase == "LOTEANDO":
            for evento in eventos:
                #  ESC sai da tela do bau
                if evento.type == pygame.KEYDOWN:
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                        self.estado_fase = "EXPLORANDO"
                        self.bau_aberto_atualmente = None

                        self.gerar_escada() # so gera se todos baus foram explorados

                    elif evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT or evento.key == pygame.K_TAB:
                        self.painel_focado = "MOCHILA" if self.painel_focado == "BAU" else "BAU"
                        self.indice_selecionado = 0  #basicamente o cursor
                    elif evento.key == pygame.K_UP:
                        self.indice_selecionado = max(0, self.indice_selecionado - 1)
                    elif evento.key == pygame.K_DOWN:
                        lista_atual = self.bau_aberto_atualmente.itens if self.painel_focado == "BAU" else self.jogador.inventario
                        self.indice_selecionado = min(max(0, len(lista_atual) -1), self.indice_selecionado + 1)
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
                        if len(self.jogador.inventario) > 0:
                            self.indice_selecionado = min(len(self.jogador.inventario) - 1, self.indice_selecionado + 1)

    def tentar_abrir_baus(self):
        baus_proximos = pygame.sprite.spritecollide(self.jogador, self.grupo_baus, False)
        for bau in baus_proximos:
            if isinstance(bau, Bau):
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


    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)

        if self.estado_fase == "LOTEANDO":

            largura_painel, altura_painel = 700, 450
            x_painel = (800 - largura_painel) // 2
            y_painel = (600 - altura_painel) // 2

            painel = pygame.Surface((largura_painel, altura_painel))
            painel.fill(COR_FUNDO_PAINEL)
            # borda do painel
            pygame.draw.rect(painel, COR_BORDA_PAINEL, painel.get_rect(), width=3)

            meio = largura_painel//2
            pygame.draw.line(painel, COR_DIVISORIA_PAINEL, (meio,0), (meio, altura_painel),2)
            ecra.blit(painel, (x_painel, y_painel))

            cor_mochila = DOURADO if self.painel_focado == "MOCHILA" else CINZA_INATIVO
            cor_bau = DOURADO if self.painel_focado == "BAU" else CINZA_INATIVO

            txt_mochila = self.fonte_titulo.render(
                f"Mochila ({self.jogador.carga_atual}/{self.jogador.capacidade_maxima}kg)", True, cor_mochila)
            txt_bau = self.fonte_titulo.render(
                "Bau", True, cor_bau)

            ecra.blit(txt_mochila, (x_painel + 20, y_painel + 20))
            ecra.blit(txt_bau, (x_painel + meio + 20, y_painel + 20))

            for i, item in enumerate(self.jogador.inventario):
                y_item = y_painel + 80 + (i*35)
                #cursor
                if self.painel_focado == "MOCHILA" and i == self.indice_selecionado:
                    pygame.draw.rect(ecra, COR_CURSOR, (x_painel + 15, y_item -2, 320, 30))
                txt_item = self.fonte_texto.render(f"{item.nome} ({item.peso}kg) ${item.valor}", True, BRANCO)
                ecra.blit(txt_item, (x_painel + 20, y_item))

            if self.bau_aberto_atualmente:
                for i, item in enumerate(self.bau_aberto_atualmente.itens):
                    y_item = y_painel + 80 + (i * 35)
                    # cursor retangular destacando
                    if self.painel_focado == "BAU" and i == self.indice_selecionado:
                        pygame.draw.rect(ecra, COR_CURSOR, (x_painel + meio + 15, y_item - 2, 270, 30))

                    txt_item = self.fonte_texto.render(f"{item.nome} ({item.peso}kg) ${item.valor}", True,
                                                       BRANCO)
                    ecra.blit(txt_item, (x_painel + meio + 20, y_item))

            rodape = self.fonte_texto.render("[SETAS] Navegar | [ESPAÇO] Transferir | [ESC] Fechar", True, CINZA_INATIVO)
            x_rodape = x_painel + (largura_painel-rodape.get_width()) // 2
            ecra.blit(rodape, (x_rodape, y_painel + altura_painel - 35))

        elif self.estado_fase == "INVENTARIO":
            largura_painel, altura_painel = 400, 450
            x_painel = (800 - largura_painel) // 2
            y_painel = (600 - altura_painel) // 2

            painel = pygame.Surface((largura_painel, altura_painel))
            painel.fill(COR_FUNDO_PAINEL)
            pygame.draw.rect(painel, COR_BORDA_PAINEL, painel.get_rect(), width=3)
            ecra.blit(painel, (x_painel, y_painel))

            txt_mochila = self.fonte_titulo.render(
                f"Mochila ({self.jogador.carga_atual}/{self.jogador.capacidade_maxima}kg)", True, DOURADO)
            ecra.blit(txt_mochila, (x_painel + 20, y_painel + 20))

            for i, item in enumerate(self.jogador.inventario):
                y_item = y_painel + 80 + (i * 35)
                # fundo do cursor
                if i == self.indice_selecionado:
                    pygame.draw.rect(ecra, COR_CURSOR, (x_painel + 15, y_item - 2, 370, 30))

                txt_item = self.fonte_texto.render(f"{item.nome} ({item.peso}kg) ${item.valor}", True, BRANCO)
                ecra.blit(txt_item, (x_painel + 20, y_item))

            rodape = self.fonte_texto.render("[SETAS] Navegar | [E/ESC] Fechar", True, CINZA_INATIVO)
            x_rodape = x_painel + (largura_painel - rodape.get_width()) // 2
            ecra.blit(rodape, (x_rodape, y_painel + altura_painel - 35))

    def transferir_item(self):
        if self.painel_focado == "BAU" and len(self.bau_aberto_atualmente.itens) > 0:
            item = self.bau_aberto_atualmente.itens[self.indice_selecionado]

            if self.jogador.carga_atual + item.peso <= self.jogador.capacidade_maxima:
                self.bau_aberto_atualmente.itens.pop(self.indice_selecionado)
                self.jogador.inventario.append(item)
                self.jogador.carga_atual += item.peso
                # ajusta o cursor
                self.indice_selecionado = max(0, min(self.indice_selecionado, len(self.bau_aberto_atualmente.itens) - 1))
                self.bau_aberto_atualmente.atualizar_cor()

        elif self.painel_focado == "MOCHILA" and len(self.jogador.inventario) > 0:
            item = self.jogador.inventario[self.indice_selecionado]
            self.jogador.inventario.pop(self.indice_selecionado)
            self.bau_aberto_atualmente.itens.append(item)
            self.jogador.carga_atual -= item.peso
            self.indice_selecionado = max(0, min(self.indice_selecionado, len(self.jogador.inventario) - 1))
            self.bau_aberto_atualmente.atualizar_cor()

    def gerar_loot_aleatorio(self):
        #colocar todos os itens do jogo
        catalogo = [
            {"nome": "Poção de Vida", "peso": 1, "valor": 20, "chance": 50},
            {"nome": "Adaga", "peso": 2, "valor": 30, "chance": 40},
            {"nome": "Capacete de Ferro", "peso": 3, "valor": 40, "chance": 30},
            {"nome": "Espada Longa", "peso": 5, "valor": 50, "chance": 20},
            {"nome": "Rubi", "peso": 1, "valor": 100, "chance": 10},
            {"nome": "Coroa de Ouro", "peso": 3, "valor": 150, "chance": 5}
            #{"nome": " ", "peso": , "valor": , "chance":},
            #{"nome": " ", "peso": , "valor": , "chance":},
            #{"nome": " ", "peso": , "valor": , "chance":}
        ]

        qtd_itens = random.randint(1, 3)
        pesos_probabilidade = [item["chance"] for item in catalogo]

        escolhas = random.choices(catalogo, weights=pesos_probabilidade, k=qtd_itens)

        loot = []
        for escolha in escolhas:
            novo_item = Item(escolha["nome"], escolha["peso"], escolha["valor"])
            loot.append(novo_item)

        return loot

    def gerar_escada(self):
        if self.escada_gerada:
            return
        #verifica se ja viu todos os baus
        todos_abertos = True
        for bau in self.grupo_baus:
            if not bau.aberto:
                todos_abertos = False
                break
        if todos_abertos:
            pisos_livres = []
            for y in range(LINHAS):
                for x in range(COLUNAS):
                    if self.matriz_mapa[y][x] == 0:
                        pisos_livres.append((x, y))

            if pisos_livres:
                x_escolhido, y_escolhido = random.choice(pisos_livres)

                # Importa a escada lá no topo do arquivo se necessário: from game.entidades import Escada
                escada = Escada(x_escolhido * TAMANHO_PISO, y_escolhido * TAMANHO_PISO)
                self.grupo_sprites.add(escada)
                self.grupo_escada.add(escada)
                self.escada_gerada = True
                print("ESCADA GERADA")