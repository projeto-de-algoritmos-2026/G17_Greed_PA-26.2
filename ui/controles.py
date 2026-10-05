from ui.cores import CINZA_INATIVO, DOURADO
from ui.painel import desenhar_painel, ALTURA_LINHA
from ui.texto import desenhar_texto

# (tecla, o que faz) — atualizar aqui quando um comando mudar
CONTROLES = [
    ("Setas / WASD", "mover e navegar nos menus"),
    ("Espaço", "abrir baú, transferir item, usar escada"),
    ("Enter", "confirmar"),
    ("E", "abrir a mochila"),
    ("Tab", "trocar entre mochila e baú"),
    ("Backspace", "apagar (moeda ou letra)"),
    ("Esc", "fechar painel / voltar"),
    ("F1", "mostrar estes controles"),
    ("F11", "tela cheia"),
]


def desenhar_controles(ecra, fonte_titulo, fonte_texto):
    largura, altura = 460, 270
    x, y = desenhar_painel(ecra, largura, altura)

    desenhar_texto(ecra, "Controles", x + 20, y + 12, fonte_titulo, DOURADO)

    for i, (tecla, acao) in enumerate(CONTROLES):
        y_linha = y + 48 + i * ALTURA_LINHA
        desenhar_texto(ecra, tecla, x + 20, y_linha, fonte_texto, DOURADO)
        desenhar_texto(ecra, acao, x + 150, y_linha, fonte_texto)

    desenhar_texto(ecra, "[F1 / ESC] Fechar", x + 20, y + altura - 26, fonte_texto, CINZA_INATIVO)
