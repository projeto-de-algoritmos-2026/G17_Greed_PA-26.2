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

    Foram escolhidos para a melhor mochila NÃO ser óbvia: não cabe tudo,
    e quem pensar um pouco consegue ganhar do algoritmo guloso.
    """
    return [
        [
            Item("Espada Longa", 5, 50),
            Item("Poção de Vida", 1, 20),
            Item("Adaga", 2, 30),
        ],
        [
            Item("Armadura Pesada", 15, 200, "RARO"),
            Item("Capacete de Ferro", 3, 40),
            Item("Anel de Prata", 1, 60, "RARO"),
            criar_pergaminho("COMUM", "MAPA"),
        ],
        [
            Item("Saco de Moedas", 14, 180, "RARO"),
            Item("Escudo Reforçado", 4, 90, "RARO"),
            Item("Rubi", 1, 100, "EPICO"),
        ],
    ]
