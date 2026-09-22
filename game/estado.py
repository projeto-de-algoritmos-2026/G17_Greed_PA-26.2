# Enum/classe de estados do jogo (NOITE, DIA, CIDADE)
#auto() serve para preencher com valor de forma inteira e sequencial
#https://docs.python.org/pt-br/3/library/enum.html#enum.auto

from enum import Enum, auto

class EstadoJogo(Enum):
    MENU = auto()
    NOITE = auto()  #masmorra knapsack
    DIA = auto()    #viagem caminhoneiro
    CIDADE = auto() #venda CMP/HUFFMAN
    FIM = auto()