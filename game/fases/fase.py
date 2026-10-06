import pygame
from ui.texto import carregar_fonte

class Fase:
    musica_tocando = None  # para não recomeçar a música quando a próxima fase usa a mesma

    def __init__(self, progresso, cor_fundo, musica):
        self.progresso = progresso
        self.proximo_estado = None  # a fase põe aqui um EstadoJogo quando quer trocar de fase

        self.musica_ambiente = musica
        self.cor_fundo = cor_fundo
        self.grupo_sprites = pygame.sprite.Group()

        self.fonte_titulo = carregar_fonte(20)
        self.fonte_texto = carregar_fonte(14)

        self.tocar_musica()

    def tocar_musica(self):
        if Fase.musica_tocando == self.musica_ambiente:
            return

        pygame.mixer.music.load(self.musica_ambiente)
        pygame.mixer.music.set_volume(0.195)
        pygame.mixer.music.play(-1)
        Fase.musica_tocando = self.musica_ambiente

    def atualizar(self, eventos):
        self.grupo_sprites.update()

    def desenhar(self, ecra):
        ecra.fill(self.cor_fundo)
        self.grupo_sprites.draw(ecra)
