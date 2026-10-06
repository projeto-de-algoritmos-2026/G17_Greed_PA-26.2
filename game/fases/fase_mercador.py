import pygame
from algoritmos.huffman import construir_codigos, codificar, decodificar
from algoritmos.troco import troco_guloso
from config import (
    DESCONTO_TROCO,
    FPS,
    KG_POR_COMPRA,
    MOEDAS,
    NIVEL_MAXIMO_DECIFRADOR,
    NIVEL_MAXIMO_SORTE,
    PRECO_DECIFRADOR,
    PRECO_MOCHILA,
    PRECO_SORTE,
    TEMPOS_MINIJOGO,
)
from game.entidades import carregar_animacao
from game.estado import EstadoJogo
from game.fases.fase import Fase
from game.itens import PERGAMINHOS
from ui.cores import (
    BRANCO,
    CINZA_INATIVO,
    COR_BORDA_PAINEL,
    COR_CURSOR,
    COR_FUNDO_MENU,
    COR_FUNDO_PAINEL,
    CORES_RARIDADE,
    DOURADO,
    VERDE,
    VERMELHO,
)
from ui.painel import desenhar_barra, desenhar_lista_itens
from ui.texto import desenhar_texto

# Onde começa a área da direita (fala do mercador em cima, conteúdo embaixo)
X_CONTEUDO = 140
Y_CONTEUDO = 128
LARGURA_CONTEUDO = 480

# retrato do mercador e moedas
QUADRO_MERCADOR = pygame.Rect(24, 44, 96, 150)
ESCALA_MERCADOR = 6
ESCALA_MOEDA = 5


def ampliar(imagem, escala):
    largura, altura = imagem.get_size()
    return pygame.transform.scale(imagem, (largura * escala, altura * escala))


def carregar_retrato(nome):
    quadros = carregar_animacao(nome)

    # mesmo recorte em todos os quadros
    recorte = quadros[0].get_bounding_rect().unionall([quadro.get_bounding_rect() for quadro in quadros])
    return [ampliar(quadro.subsurface(recorte), ESCALA_MERCADOR) for quadro in quadros]


def formatar_moedas(moedas):
    """[100, 100, 25, 10] -> "2x100 + 25 + 10" """
    partes = []
    for moeda in sorted(set(moedas), reverse=True):
        quantidade = moedas.count(moeda)
        if quantidade > 1:
            partes.append(f"{quantidade}x{moeda}")
        else:
            partes.append(str(moeda))
    return " + ".join(partes)


def tempo_do_pagamento(preco):
    moedas = len(troco_guloso(preco, MOEDAS))
    indice = min(max(0, moedas - 2), len(TEMPOS_MINIJOGO) - 1)
    return TEMPOS_MINIJOGO[indice]


def tempo_do_pergaminho(raridade):
    return TEMPOS_MINIJOGO[PERGAMINHOS[raridade]["nivel"] - 1]


class FaseMercador(Fase):
    def __init__(self, progresso):
        super().__init__(progresso, cor_fundo=COR_FUNDO_MENU, musica='assets/sons/intro.mpeg')

        # MENU, VENDENDO, PAGANDO ou PERGAMINHO
        self.estado_fase = "MENU"
        self.indice_selecionado = 0

        # O que o mercador respondeu à última ação (some quando o cursor anda)
        self.resposta = ["Bem-vindo, saqueador! O que vai ser hoje?"]

        # usado na lista de venda: 0 é "Vender tudo"; os itens começam no 1
        self.indice_venda = 0

        # usados enquanto o jogador paga uma compra
        self.preco = 0
        self.acao_da_compra = None
        self.moedas_na_mesa = []
        self.indice_moeda = 0

        # usados enquanto o jogador decifra um pergaminho
        self.pergaminho = None
        self.codigos = {}
        self.bits = ""
        self.palavra_digitada = ""
        self.pergaminho_iniciado = False
        self.pergaminho_lido = False

        # cronometro dos minijogos (segundos)
        self.tempo_total = 0
        self.tempo_restante = 0

        self.quadros_mercador = carregar_retrato("dwarf_m_idle_anim")
        self.quadros_moeda = [ampliar(quadro, ESCALA_MOEDA) for quadro in carregar_animacao("coin_anim")]
        self.tempo_animacao = 0

    # ------------------------------------------------------------------
    # Menu principal do mercador
    # ------------------------------------------------------------------

    def opcoes(self):
        """Cada opção: (texto, preço ou None, fala do mercador, função que executa)."""
        progresso = self.progresso

        return [
            ("Vender itens", None,
             ["Mostre o que trouxe. Eu pago em moedas,", "sempre com o menor número de moedas possível."],
             self.abrir_venda),

            (f"Mochila maior (+{KG_POR_COMPRA}kg)", PRECO_MOCHILA * (progresso.compras_mochila + 1),
             [f"Hoje cabem {progresso.capacidade_maxima}kg na sua mochila.",
              "Com mais espaço você traz mais coisa de cada andar."],
             self.comprar_mochila),

            self.opcao_melhoria("Amuleto da Sorte", progresso.nivel_sorte, NIVEL_MAXIMO_SORTE, PRECO_SORTE,
                                ["Com ele, os baús trazem itens raros", "com mais frequência."],
                                self.comprar_sorte),

            self.opcao_melhoria("Decifrador de Pergaminhos", progresso.nivel_decifrador,
                                NIVEL_MAXIMO_DECIFRADOR, PRECO_DECIFRADOR,
                                ["Lê pergaminhos sozinho. Nível 1 lê os comuns, 2 os raros,",
                                 "3 os épicos e 4 os lendários."],
                                self.comprar_decifrador),

            ("Decifrar pergaminho", None,
             ["Pergaminhos são escritos em código de Huffman.",
              "Sem o Decifrador certo, é uma chance só e contra o relógio."],
             self.abrir_pergaminho),

            ("Próxima masmorra", None,
             ["Pronto para descer mais um andar?", "O que você não vendeu continua na mochila."],
             self.proxima_masmorra),

            ("Encerrar o jogo", None,
             ["Vai se aposentar? Foi um prazer fazer negócio!"],
             self.encerrar),
        ]

    def opcao_melhoria(self, nome, nivel, nivel_maximo, preco_base, fala, acao):
        if nivel >= nivel_maximo:
            return (f"{nome} (nível máximo)", None, ["Você já tem o melhor que eu vendo."], None)
        return (f"{nome} nível {nivel + 1}", preco_base * (nivel + 1), fala, acao)

    def atualizar(self, eventos):
        self.tempo_animacao += 1

        if self.passar_tempo():
            return

        for evento in eventos:
            if evento.type != pygame.KEYDOWN:
                continue

            if self.estado_fase == "MENU":
                self.atualizar_menu(evento)
            elif self.estado_fase == "VENDENDO":
                self.atualizar_venda(evento)
            elif self.estado_fase == "PAGANDO":
                self.atualizar_pagamento(evento)
            elif self.estado_fase == "PERGAMINHO":
                self.atualizar_pergaminho(evento)

    def atualizar_menu(self, evento):
        opcoes = self.opcoes()

        if evento.key in (pygame.K_UP, pygame.K_w):
            self.indice_selecionado = max(0, self.indice_selecionado - 1)
            self.resposta = None
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.indice_selecionado = min(len(opcoes) - 1, self.indice_selecionado + 1)
            self.resposta = None
        elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
            texto, preco, fala, acao = opcoes[self.indice_selecionado]

            if acao is None:
                return
            if preco is None:
                acao()
            elif self.progresso.ouro < preco:
                self.resposta = [f"Isso custa {preco} de ouro e você só tem {self.progresso.ouro}.",
                                 "Venda alguma coisa primeiro!"]
            else:
                self.abrir_pagamento(preco, acao)

    def voltar_ao_menu(self):
        self.estado_fase = "MENU"

    # ------------------------------------------------------------------
    # Cronômetro dos minijogos
    # ------------------------------------------------------------------

    def iniciar_tempo(self, segundos):
        self.tempo_total = segundos
        self.tempo_restante = segundos

    def tempo_correndo(self):
        if self.estado_fase == "PAGANDO":
            return True
        return self.estado_fase == "PERGAMINHO" and self.pergaminho_iniciado and not self.pergaminho_lido

    def passar_tempo(self):
        if not self.tempo_correndo():
            return False

        self.tempo_restante -= 1 / FPS
        if self.tempo_restante > 0:
            return False

        self.tempo_restante = 0
        if self.estado_fase == "PAGANDO":
            self.concluir_pagamento(no_tempo=False)
        else:
            self.conferir_palavra(no_tempo=False)
        return True

    def proxima_masmorra(self):
        self.progresso.andar += 1
        self.proximo_estado = EstadoJogo.MASMORRA

    def encerrar(self):
        self.proximo_estado = EstadoJogo.FIM

    def comprar_mochila(self):
        self.progresso.capacidade_maxima += KG_POR_COMPRA
        self.progresso.compras_mochila += 1

    def comprar_sorte(self):
        self.progresso.nivel_sorte += 1

    def comprar_decifrador(self):
        self.progresso.nivel_decifrador += 1

    # ------------------------------------------------------------------
    # Venda: o mercador paga com o algoritmo do troco
    # ------------------------------------------------------------------

    def abrir_venda(self):
        self.estado_fase = "VENDENDO"
        self.indice_venda = 0
        self.resposta = ["Escolha o que quer vender."]

    def atualizar_venda(self, evento):
        inventario = self.progresso.inventario

        if evento.key == pygame.K_ESCAPE:
            self.voltar_ao_menu()
        elif evento.key in (pygame.K_UP, pygame.K_w):
            self.indice_venda = max(0, self.indice_venda - 1)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.indice_venda = min(len(inventario), self.indice_venda + 1)
        elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.indice_venda == 0:
                self.vender(self.itens_para_vender_tudo())
            else:
                self.vender([inventario[self.indice_venda - 1]])
            self.indice_venda = min(len(inventario), self.indice_venda)

    def itens_para_vender_tudo(self):
        # Pergaminho selado vale quase nada: só é vendido se o jogador escolher ele na lista
        return [item for item in self.progresso.inventario if not item.esta_selado()]

    def vender(self, itens):
        if len(itens) == 0:
            self.resposta = ["Não há nada para vender."]
            return

        total = sum(item.valor for item in itens)
        for item in itens:
            self.progresso.inventario.remove(item)
        self.progresso.ouro += total

        # O mercador entrega o ouro com o menor número de moedas (troco guloso)
        moedas = troco_guloso(total, MOEDAS)
        self.resposta = [
            f"São {total} de ouro: {formatar_moedas(moedas)}.",
            f"Moedas entregues: {len(moedas)}. Sempre pego a maior que cabe!",
        ]

    # ------------------------------------------------------------------
    # Compra: o jogador paga escolhendo as moedas
    # ------------------------------------------------------------------

    def abrir_pagamento(self, preco, acao):
        self.estado_fase = "PAGANDO"
        self.preco = preco
        self.acao_da_compra = acao
        self.moedas_na_mesa = []
        self.indice_moeda = 0
        self.iniciar_tempo(tempo_do_pagamento(preco))
        self.resposta = [
            f"São {preco} de ouro. Você tem {self.tempo_total} segundos para pôr na mesa.",
            f"Com o menor número de moedas, dou {int(DESCONTO_TROCO * 100)}% de desconto!",
            "Se o tempo acabar, cobro o preço cheio.",
        ]

    def atualizar_pagamento(self, evento):
        na_mesa = sum(self.moedas_na_mesa)

        if evento.key == pygame.K_ESCAPE:
            self.voltar_ao_menu()
            self.resposta = ["Mudou de ideia? Sem problema."]
        elif evento.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a):
            self.indice_moeda = max(0, self.indice_moeda - 1)
        elif evento.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d):
            self.indice_moeda = min(len(MOEDAS) - 1, self.indice_moeda + 1)
        elif evento.key == pygame.K_SPACE:
            moeda = MOEDAS[self.indice_moeda]
            if na_mesa + moeda <= self.preco:
                self.moedas_na_mesa.append(moeda)
        elif evento.key == pygame.K_BACKSPACE:
            if self.moedas_na_mesa:
                self.moedas_na_mesa.pop()
        elif evento.key == pygame.K_RETURN:
            if na_mesa == self.preco:
                self.concluir_pagamento()

    def concluir_pagamento(self, no_tempo=True):
        moedas_guloso = troco_guloso(self.preco, MOEDAS)
        usadas = len(self.moedas_na_mesa)

        if not no_tempo:
            desconto = 0
            self.resposta = [
                "O tempo acabou! Cobrei o preço cheio.",
                f"O guloso pagaria com {len(moedas_guloso)} moedas: {formatar_moedas(moedas_guloso)}.",
            ]
        elif usadas <= len(moedas_guloso):
            desconto = int(self.preco * DESCONTO_TROCO)
            self.resposta = [
                f"Perfeito! {usadas} moedas é o menor número possível.",
                f"Devolvo {desconto} de ouro de desconto.",
            ]
        else:
            desconto = 0
            self.resposta = [
                f"Você usou {usadas} moedas. O guloso usaria só {len(moedas_guloso)}:",
                f"{formatar_moedas(moedas_guloso)}. Pegue sempre a maior moeda que cabe!",
            ]

        self.progresso.ouro -= self.preco - desconto
        self.acao_da_compra()
        self.voltar_ao_menu()

    # ------------------------------------------------------------------
    # Pergaminhos: código de Huffman
    # ------------------------------------------------------------------

    def abrir_pergaminho(self):
        selados = [item for item in self.progresso.inventario if item.esta_selado()]
        if len(selados) == 0:
            self.resposta = ["Você não tem nenhum pergaminho selado."]
            return

        self.estado_fase = "PERGAMINHO"
        self.pergaminho = selados[0]
        self.codigos = construir_codigos(self.pergaminho.texto)
        self.bits = codificar(self.pergaminho.texto, self.codigos)
        self.palavra_digitada = ""
        self.pergaminho_iniciado = False
        self.pergaminho_lido = False

        nivel_exigido = PERGAMINHOS[self.pergaminho.raridade]["nivel"]
        if self.progresso.nivel_decifrador >= nivel_exigido:
            valor = self.revelar_pergaminho(acertou=True)
            self.resposta = ["Seu Decifrador leu o pergaminho sozinho.", f"Ele vale {valor} de ouro!"]
        else:
            self.iniciar_tempo(tempo_do_pergaminho(self.pergaminho.raridade))
            self.resposta = [
                f"Seu Decifrador é nível {self.progresso.nivel_decifrador}; este exige nível {nivel_exigido}.",
                f"Você mesmo terá que ler: uma chance só, em {self.tempo_total} segundos.",
                "Se errar ou o tempo acabar, ele passa a valer a metade.",
            ]

    def revelar_pergaminho(self, acertou):
        valor = PERGAMINHOS[self.pergaminho.raridade]["valor"]
        if not acertou:
            valor = valor // 2

        self.pergaminho.valor = valor
        self.pergaminho.decifrado = True
        self.pergaminho_lido = True
        return valor

    def atualizar_pergaminho(self, evento):
        if self.pergaminho_lido:
            if evento.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                self.voltar_ao_menu()
                self.resposta = None

        elif not self.pergaminho_iniciado:
            if evento.key == pygame.K_ESCAPE:
                self.voltar_ao_menu()
                self.resposta = ["Tudo bem, o pergaminho continua selado."]
            elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.pergaminho_iniciado = True
                self.resposta = ["Use a tabela para ler os bits e digite a palavra.", "Valendo!"]

        elif evento.key == pygame.K_BACKSPACE:
            self.palavra_digitada = self.palavra_digitada[:-1]
        elif evento.key == pygame.K_RETURN:
            if self.palavra_digitada:
                self.conferir_palavra()
        elif evento.unicode.isalpha() and len(self.palavra_digitada) < 16:
            self.palavra_digitada += evento.unicode.upper()

    def conferir_palavra(self, no_tempo=True):
        acertou = no_tempo and self.palavra_digitada == self.pergaminho.texto
        valor = self.revelar_pergaminho(acertou)

        if acertou:
            self.resposta = ["Você decifrou sozinho! Impressionante.", f"O pergaminho vale {valor} de ouro!"]
        else:
            motivo = "Errou..." if no_tempo else "O tempo acabou!"
            self.resposta = [f"{motivo} Estava escrito {self.pergaminho.texto}.",
                             f"O pergaminho rasgou: agora vale só {valor} de ouro."]

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        progresso = self.progresso

        desenhar_texto(ecra, "Mercador", 24, 10, self.fonte_titulo, DOURADO)
        situacao = (f"Ouro: {progresso.ouro} | Mochila: {progresso.peso_total()}/{progresso.capacidade_maxima}kg"
                    f" | Andar {progresso.andar}")
        desenhar_texto(ecra, situacao, X_CONTEUDO, 14, self.fonte_texto, BRANCO)

        self.desenhar_mercador(ecra)
        self.desenhar_fala(ecra)

        if self.estado_fase == "MENU":
            self.desenhar_menu(ecra)
            rodape = "[SETAS] Escolher | [ESPAÇO] Confirmar | [F1] Controles"
        elif self.estado_fase == "VENDENDO":
            self.desenhar_venda(ecra)
            rodape = "[SETAS] Escolher | [ESPAÇO] Vender | [ESC] Voltar"
        elif self.estado_fase == "PAGANDO":
            self.desenhar_pagamento(ecra)
            rodape = "[SETAS] Moeda | [ESPAÇO] Pôr | [BACKSPACE] Tirar | [ENTER] Pagar | [ESC] Desistir"
        elif self.pergaminho_lido:
            self.desenhar_pergaminho(ecra)
            rodape = "[ESPAÇO] Voltar"
        elif not self.pergaminho_iniciado:
            self.desenhar_pergaminho_selado(ecra)
            rodape = "[ESPAÇO] Começar | [ESC] Deixar para depois"
        else:
            self.desenhar_pergaminho(ecra)
            rodape = "[LETRAS] Digitar | [BACKSPACE] Apagar | [ENTER] Responder"

        desenhar_texto(ecra, rodape, 24, 340, self.fonte_texto, CINZA_INATIVO)

    def desenhar_mercador(self, ecra):
        pygame.draw.rect(ecra, COR_FUNDO_PAINEL, QUADRO_MERCADOR)

        quadro = self.quadros_mercador[self.tempo_animacao // 10 % len(self.quadros_mercador)]
        ecra.blit(quadro, quadro.get_rect(midbottom=(QUADRO_MERCADOR.centerx, QUADRO_MERCADOR.bottom - 6)))

        pygame.draw.rect(ecra, COR_BORDA_PAINEL, QUADRO_MERCADOR, width=2)

    def desenhar_fala(self, ecra):
        pygame.draw.rect(ecra, COR_FUNDO_PAINEL, (X_CONTEUDO, 44, LARGURA_CONTEUDO, 70))
        pygame.draw.rect(ecra, COR_BORDA_PAINEL, (X_CONTEUDO, 44, LARGURA_CONTEUDO, 70), width=2)

        fala = self.resposta
        if fala is None:
            fala = self.opcoes()[self.indice_selecionado][2]

        for i, linha in enumerate(fala):
            desenhar_texto(ecra, linha, X_CONTEUDO + 12, 52 + i * 18, self.fonte_texto, BRANCO)

    def desenhar_tempo(self, ecra, y):
        segundos = int(self.tempo_restante) + 1 if self.tempo_restante > 0 else 0
        cor = VERMELHO if segundos <= 3 else VERDE

        largura_texto = desenhar_texto(ecra, f"Tempo: {segundos}s", X_CONTEUDO + 12, y, self.fonte_texto, cor)
        x_barra = X_CONTEUDO + 12 + max(largura_texto, 80) + 10
        desenhar_barra(ecra, x_barra, y + 3, X_CONTEUDO + LARGURA_CONTEUDO - x_barra, 8,
                       self.tempo_restante / self.tempo_total, cor)

    def desenhar_menu(self, ecra):
        for i, (texto, preco, fala, acao) in enumerate(self.opcoes()):
            y = Y_CONTEUDO + i * 24

            if i == self.indice_selecionado:
                pygame.draw.rect(ecra, COR_CURSOR, (X_CONTEUDO, y - 2, LARGURA_CONTEUDO, 20))

            # cinza = não dá para escolher agora (nível máximo ou falta ouro)
            sem_ouro = preco is not None and self.progresso.ouro < preco
            cor = CINZA_INATIVO if (acao is None or sem_ouro) else BRANCO

            desenhar_texto(ecra, texto, X_CONTEUDO + 12, y, self.fonte_texto, cor)
            if preco is not None:
                desenhar_texto(ecra, f"${preco}", X_CONTEUDO + 400, y, self.fonte_texto, cor)

    def desenhar_venda(self, ecra):
        inventario = self.progresso.inventario
        total = sum(item.valor for item in self.itens_para_vender_tudo())

        if self.indice_venda == 0:
            pygame.draw.rect(ecra, COR_CURSOR, (X_CONTEUDO, Y_CONTEUDO - 2, LARGURA_CONTEUDO, 18))
        desenhar_texto(ecra, f"Vender tudo (${total})", X_CONTEUDO + 5, Y_CONTEUDO, self.fonte_texto, DOURADO)

        selecionado = self.indice_venda - 1 if self.indice_venda > 0 else None
        desenhar_lista_itens(ecra, self.fonte_texto, inventario, X_CONTEUDO + 5, Y_CONTEUDO + 24,
                             LARGURA_CONTEUDO, selecionado)

    def desenhar_pagamento(self, ecra):
        na_mesa = sum(self.moedas_na_mesa)

        for i, moeda in enumerate(MOEDAS):
            centro_x = X_CONTEUDO + 40 + i * 78
            centro_y = Y_CONTEUDO + 40

            # a moeda escolhida gira
            quadro = self.quadros_moeda[0]
            cor = BRANCO
            if i == self.indice_moeda:
                pygame.draw.rect(ecra, COR_CURSOR, (centro_x - 30, centro_y - 30, 60, 60))
                quadro = self.quadros_moeda[self.tempo_animacao // 6 % len(self.quadros_moeda)]
                cor = DOURADO

            ecra.blit(quadro, quadro.get_rect(center=(centro_x, centro_y - 8)))

            largura_texto = self.fonte_texto.size(str(moeda))[0]
            desenhar_texto(ecra, str(moeda), centro_x - largura_texto // 2, centro_y + 13, self.fonte_texto, cor)

        desenhar_texto(ecra, f"Na mesa: {na_mesa} de {self.preco} ({len(self.moedas_na_mesa)} moedas)",
                       X_CONTEUDO + 12, Y_CONTEUDO + 90, self.fonte_texto, DOURADO)
        if self.moedas_na_mesa:
            desenhar_texto(ecra, formatar_moedas(self.moedas_na_mesa),
                           X_CONTEUDO + 12, Y_CONTEUDO + 110, self.fonte_texto, BRANCO)

        self.desenhar_tempo(ecra, Y_CONTEUDO + 140)

    def desenhar_pergaminho_selado(self, ecra):
        x = X_CONTEUDO + 12
        cor_raridade = CORES_RARIDADE[self.pergaminho.raridade]

        desenhar_texto(ecra, "Pergaminho selado", x, Y_CONTEUDO, self.fonte_titulo, cor_raridade)
        desenhar_texto(ecra, f"Palavra de {len(self.pergaminho.texto)} letras, {len(self.bits)} bits para ler.",
                       x, Y_CONTEUDO + 34, self.fonte_texto, BRANCO)
        desenhar_texto(ecra, f"Você terá {self.tempo_total} segundos.", x, Y_CONTEUDO + 54, self.fonte_texto, BRANCO)
        desenhar_texto(ecra, "A tabela e os bits só aparecem quando você começar.",
                       x, Y_CONTEUDO + 82, self.fonte_texto, CINZA_INATIVO)

    def desenhar_pergaminho(self, ecra):
        x = X_CONTEUDO + 12
        cor_raridade = CORES_RARIDADE[self.pergaminho.raridade]

        desenhar_texto(ecra, "Tabela de Huffman (letra mais comum = código mais curto):",
                       x, Y_CONTEUDO, self.fonte_texto, CINZA_INATIVO)

        # letras de código mais curto primeiro, 4 por linha
        letras = sorted(self.codigos, key=lambda letra: (len(self.codigos[letra]), letra))
        for i, letra in enumerate(letras):
            coluna, linha = i % 4, i // 4
            desenhar_texto(ecra, f"{letra} = {self.codigos[letra]}",
                           x + coluna * 115, Y_CONTEUDO + 22 + linha * 18, self.fonte_texto, BRANCO)

        desenhar_texto(ecra, "Bits do pergaminho:", x, Y_CONTEUDO + 86, self.fonte_texto, CINZA_INATIVO)
        desenhar_texto(ecra, self.bits, x, Y_CONTEUDO + 104, self.fonte_texto, cor_raridade)

        if self.pergaminho_lido:
            mensagem = decodificar(self.bits, self.codigos)
            desenhar_texto(ecra, f"Mensagem: {mensagem}", x, Y_CONTEUDO + 134, self.fonte_titulo, DOURADO)
        else:
            desenhar_texto(ecra, f"Sua resposta: {self.palavra_digitada}_", x, Y_CONTEUDO + 134,
                           self.fonte_titulo, DOURADO)
            self.desenhar_tempo(ecra, Y_CONTEUDO + 170)
