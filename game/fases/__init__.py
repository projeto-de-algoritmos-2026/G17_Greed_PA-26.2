from game.estado import EstadoJogo
from game.fases.menu import Menu
from game.fases.fase_masmorra import FaseMasmorra
from game.fases.resultado import Resultado
from game.fases.fase_mercador import FaseMercador
from game.fases.fim import Fim

# Qual classe cuida de cada estado do jogo
FASES = {
    EstadoJogo.MENU: Menu,
    EstadoJogo.MASMORRA: FaseMasmorra,
    EstadoJogo.RESULTADO: Resultado,
    EstadoJogo.MERCADOR: FaseMercador,
    EstadoJogo.FIM: Fim,
}
