<h1><font size="6"><b>Nightfall Looter</b></font><br></h1>
<h3><b>Número da Lista:</b> [PREENCHER]<br></h3>
<h3><i>Conteúdo da disciplina:</i> Algoritmos Gulosos<br></h3>
<h3>Alunos</h3>

| Matrícula | Aluno                            |
|-----------|----------------------------------|
| 251013660 | Matheus Moretti Soares           |
| 251019771 | Daniel Filipe Borges de Oliveira |

---

## Sobre

**Nightfall Looter** é um jogo 2D educativo sobre **algoritmos gulosos**. O jogador alterna entre duas fases, quantas vezes quiser:

- 🌙 **Masmorra** — explore as salas, abra os baús e escolha o que levar. A mochila é uma só e tem limite de peso (30kg no início): nada entra além dele, e o último terço é a zona pesada — com a mochila ali o personagem anda mais devagar.
- 🏪 **Mercador** — venda o que trouxe, compre melhorias (mochila maior, amuleto da sorte, decifrador de pergaminhos), decifre pergaminhos e decida se desce mais um andar ou encerra o jogo. O que não for vendido continua na mochila.

Entre uma fase e outra, o jogo compara a sua mochila com a que o algoritmo guloso montaria com a mesma capacidade e paga um bônus de ouro a quem chega a pelo menos 80% do valor dele — com um extra para quem consegue ganhar dele.

12 ITENS DIFERENTES E 4 TIPOS DE PERGAMINHOS! 
### Algoritmos implementados

| Algoritmo | Onde aparece no jogo | Arquivo |
|---|---|---|
| **Mochila gulosa (Knapsack 0/1)** | Tela de resultado: é o adversário do jogador. Ordena os itens do andar por valor/peso e pega cada item inteiro que ainda couber. Com itens inteiros o guloso nem sempre é ótimo — dá para ganhar dele! | `algoritmos/knapsack.py` |
| **Mochila fracionária** | Tela de resultado: é o "teto" do placar — o valor que daria se todo item pudesse ser cortado em pedaços, caso em que o guloso é sempre ótimo e ninguém passa dele. Na masmorra ela aparece nos itens a granel (pó, elixir), que podem ser levados aos poucos, 1kg por vez. | `algoritmos/knapsack.py` |
| **Troco (moedas)** | O mercador paga suas vendas com o menor número de moedas; nas compras, quem paga com o menor número de moedas dentro do tempo (12 a 18s) ganha 10% de desconto. | `algoritmos/troco.py` |
| **Código de Huffman** | Pergaminhos encontrados nos baús estão codificados. O Decifrador lê sozinho os pergaminhos até a raridade do seu nível; acima disso, o jogador decodifica os bits usando a tabela e tem uma única chance, contra o relógio (12 a 18s, conforme a raridade) — se errar ou o tempo acabar, o pergaminho passa a valer metade. | `algoritmos/huffman.py` |

## Instalação

Linguagem: Python<br>
Biblioteca: Pygame (`pygame-ce`)<br>

**Pré-requisitos:** É necessário ter o Python e o gerenciador de pacotes `pip` instalados no seu computador.

**1. Instale a linguagem Python:** Acesse o [Site Oficial do Python](https://www.python.org/downloads/) e faça o download para seu sistema operacional.

**OBS:**
Para verificar a instalação abra o terminal e rode:
```bash
python --version
```
*(Se o comando acima não funcionar, tente digitar `python3 --version`)*.

**2. Verifique a instalação do Pip**
```bash
pip --version
```
*(Se precisar usar o `python3`, verifique com `pip3 --version`)*.

---

Siga o passo a passo abaixo para rodar a aplicação no seu ambiente local.

**1. Clone o repositório:**
```bash
git clone https://github.com/projeto-de-algoritmos-2026/G17_Greed_PA-26.2
```

**2. Entre na pasta do projeto e crie o ambiente virtual (venv):**
```bash
cd G17_Greed_PA-26.2

python -m venv venv
```

**3. Ative o ambiente virtual:**

Windows:
```bash
.\venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

**4. Instale as dependências:**
```bash
pip install -r requirements.txt
```

## Uso

**1. Com o ambiente virtual ativado, rode o jogo a partir da raiz do projeto:**
```bash
python main.py
```

**2. Jogue:**
#### Fase Tutorial
- Na **masmorra**, abra todos os baús para a escada aparecer e desça por ela.
- Na tela de **resultado**, veja como a sua mochila se saiu contra o algoritmo guloso.
- No **mercador**, venda, compre melhorias, decifre pergaminhos e escolha entre continuar ou encerrar.

**Controles** (a tecla `F1` mostra esta lista dentro do jogo):

| Tecla | Ação |
|---|---|
| Setas / WASD | mover e navegar nos menus |
| Espaço | abrir baú, transferir item, usar escada |
| Enter | confirmar |
| E | abrir a mochila |
| Tab | trocar entre mochila e baú |
| Backspace | apagar (moeda ou letra) |
| Esc | fechar painel / voltar |
| F1 | controles |
| F11 | tela cheia |

**3. Testes dos algoritmos:**
```bash
pytest
```

## Outros

### 🛠️ Tecnologias e Bibliotecas Utilizadas

Para garantir um desenvolvimento ágil, com foco total na lógica dos algoritmos, adotamos uma stack enxuta, sem framework e sem comunicação via API — o projeto é um **monolito local**, rodando inteiramente em um único processo Python:

* **Python:** linguagem principal do projeto, usada tanto na lógica dos algoritmos quanto na interface do jogo.
* **Pygame (pygame-ce):** biblioteca utilizada para renderização gráfica, captura de input (teclado) e controle do game loop. Não se trata de um framework — apenas uma ferramenta de baixo nível para desenho e eventos, sobre a qual toda a arquitetura do jogo foi construída do zero.

### 🎨 Arte

* **Jogador, baús, escada, mercador e moedas:** pacote [16x16 DungeonTileset II](https://0x72.itch.io/dungeontileset-ii), de 0x72, em domínio público (CC0). Os arquivos e os créditos estão em `assets/sprites/0x72/`.
* **Piso e paredes:** arte própria do grupo, em `assets/sprites/PNG/`.

> Observação: o projeto foi estruturado desde o início pensando em uma futura migração para a web via **Pygbag** (compilação para WebAssembly), mantendo os módulos de algoritmos independentes da camada visual.

## Vídeo de Apresentação

[Link do Vídeo Gravado no Teams](LINK_DO_VIDEO)
