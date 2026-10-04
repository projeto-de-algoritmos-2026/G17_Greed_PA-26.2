import pygame

def extrair_sprite(caminho_imagem, x_origem, y_origem, tamanho=16):
    #carrega os sprites e converte para o display
    spritesheet = pygame.image.load(caminho_imagem).convert_alpha()

    #define o retângulo de recorte (x, y, largura, altura)
    # se o chão que vc quer for o 1º sprite da 2ª linha, seria (0, 16, 16, 16)
    rect_recorte = pygame.Rect(x_origem, y_origem, tamanho, tamanho)

    return spritesheet.subsurface(rect_recorte)