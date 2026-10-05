# Enum/classe de estados do jogo
#auto() serve para preencher com valor de forma inteira e sequencial
#https://docs.python.org/pt-br/3/library/enum.html#enum.auto

from enum import Enum, auto

class EstadoJogo(Enum):
    MENU = auto()
    MASMORRA = auto()   #explorar e encher a mochila
    RESULTADO = auto()  #comparacao com o knapsack guloso
    MERCADOR = auto()   #vender, comprar (troco) e decifrar pergaminhos (huffman)
    FIM = auto()
