from game.entidades import Item
from game.itens import criar_pergaminho

# Primeiro andar: sempre igual, para o jogador aprender o jogo.
# Legenda: # parede   . chão   J jogador   B baú
ANDAR_1 = [
    "########################################",
    "########################################",
    "########################################",
    "########################............####",
    "###..........###########............####",
    "###.......B..###########.........B..####",
    "###.................................####",
    "###.................................####",
    "###..J.......#######..##............####",
    "###..........#######..##............####",
    "###..........#######..###################",
    "###..........#######..###################",
    "####################..###################",
    "####################..###################",
    "###############.............############",
    "###############.............############",
    "###############.............############",
    "###############..........B..############",
    "###############.............############",
    "###############.............############",
    "########################################",
    "########################################",
]


def itens_andar_1():
    """Itens de cada baú do andar 1, na ordem em que os B aparecem no mapa.

    Foram escolhidos para a melhor mochila NÃO ser óbvia: são 52kg para uma
    mochila de 30kg. O guloso enche 29kg ($432): ele pega o Escudo cedo e depois
    não sobra espaço para o Saco de Moedas. Quem pensar um pouco passa dele
    (Armadura + Saco + Anel + Rubi = 30kg, $455).
    """
    return [
        [
            Item("Espada Longa", 6, 45),
            Item("Poção de Vida", 2, 22),
            Item("Adaga", 3, 30),
        ],
        [
            Item("Armadura Pesada", 15, 200, "RARO"),
            Item("Capacete de Ferro", 4, 34),
            Item("Anel de Prata", 1, 30, "RARO"),
            criar_pergaminho("COMUM", "MAPA"),
        ],
        [
            Item("Saco de Moedas", 13, 170, "RARO"),
            Item("Escudo Reforçado", 7, 95, "RARO"),
            Item("Rubi", 1, 55, "EPICO"),
        ],
    ]
