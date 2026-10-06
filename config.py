#dimensoes

# janela (o que aparece no monitor)
LARGURA = 800
ALTURA = 600
FPS = 60

# tela virtual (onde o jogo é desenhado antes de ser esticado para a janela)
LARGURA_VIRTUAL = 640
ALTURA_VIRTUAL = 360

TAMANHO_PISO = 16

COLUNAS = LARGURA_VIRTUAL // TAMANHO_PISO   # 640//16 = 40
LINHAS = ALTURA_VIRTUAL // TAMANHO_PISO     # 360//16 = 22 (sobram 8px embaixo)

FONTE = 'assets/fonts/DigitalDisco.ttf'

#gameplay

VELOCIDADE_JOGADOR = TAMANHO_PISO // 8  #pixel por frame
VELOCIDADE_LENTA = VELOCIDADE_JOGADOR // 2

# A mochila é uma só: cabe até a capacidade e nada além disso.
# É esse mesmo número que o algoritmo guloso usa na tela de resultado.
CAPACIDADE_INICIAL = 30  # kg que cabem na mochila
DIVISOR_ZONA_PESADA = 3  # o último 1/3 da mochila é a zona pesada: o jogador anda lento

CHANCE_PERGAMINHO = 20   # % de chance de um baú ter um pergaminho

#resultado

APROVEITAMENTO_MINIMO = 0.8  # abaixo de 80% do valor do guloso não há bônus
BONUS_MAXIMO_OURO = 60       # bônus de quem empata com o guloso
BONUS_VENCEU_GULOSO = 60     # bônus extra de quem ganha do guloso

#mercador

MOEDAS = [100, 50, 25, 10, 5, 1]

KG_POR_COMPRA = 5
PRECO_MOCHILA = 235      # multiplicado por (compras já feitas + 1)
PRECO_SORTE = 340        # multiplicado por (nível atual + 1)
PRECO_DECIFRADOR = 165   # multiplicado por (nível atual + 1)

NIVEL_MAXIMO_SORTE = 3
NIVEL_MAXIMO_DECIFRADOR = 4

DESCONTO_TROCO = 0.10    # desconto de quem paga com o menor número de moedas

# Tempo máximo (segundos) dos dois minijogos do mercador: quanto mais difícil, mais tempo.
# Pergaminho: comum, raro, épico, lendário. Pagamento: pelo número de moedas que o guloso usaria.
TEMPOS_MINIJOGO = [12, 14, 16, 18]
