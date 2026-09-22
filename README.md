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

**Nightfall Looter** é um jogo 2D desenvolvido para aplicar, na prática, algoritmos clássicos de otimização em um ciclo de gameplay dia/noite:
### Escopo Principal
- 🌙 **Noite** — o personagem invade masmorras e castelos abandonados, saqueando baús e decidindo o que carregar na mochila usando o algoritmo da **Mochila (Knapsack)**.
- ☀️ **Dia** — com o loot em mãos, o personagem viaja entre cidades para vender seus itens, com a rota calculada pelo **Algoritmo do Caminhoneiro**.
### Escopo Opcional
- 🏪 **Cidade** *(bônus)* — os itens são vendidos ao melhor preço possível entre as cidades visitadas, usando um algoritmo de **Compra e Venda Ótima (CMP)**.
- 📜 **Pergaminhos** *(bônus)* — itens especiais encontrados na masmorra são codificados com **Huffman** e precisam ser decodificados antes da venda.

- Atualmente Implementados: Knapsack & Algoritmo do Caminhoneiro

**Em breve: CMP (Compra e Venda) e Huffman...**

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
cd nightfall-looter

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
- Durante a **noite**, explore a masmorra e abra os baús — o jogo sugere a combinação ótima de itens para levar na mochila.
- Ao amanhecer, visualize o **mapa** e a rota calculada até as cidades vizinhas.
- Nas **cidades**, venda seu loot e, se tiver pergaminhos, decodifique-os antes de negociar.

## Outros

### 🛠️ Tecnologias e Bibliotecas Utilizadas

Para garantir um desenvolvimento ágil, com foco total na lógica dos algoritmos, adotamos uma stack enxuta, sem framework e sem comunicação via API — o projeto é um **monolito local**, rodando inteiramente em um único processo Python:

* **Python:** linguagem principal do projeto, usada tanto na lógica dos algoritmos quanto na interface do jogo.
* **Pygame (pygame-ce):** biblioteca utilizada para renderização gráfica, captura de input (teclado/mouse) e controle do game loop. Não se trata de um framework — apenas uma ferramenta de baixo nível para desenho e eventos, sobre a qual toda a arquitetura do jogo foi construída do zero.

> Observação: o projeto foi estruturado desde o início pensando em uma futura migração para a web via **Pygbag** (compilação para WebAssembly), mantendo os módulos de algoritmos independentes da camada visual.

## Vídeo de Apresentação

[Link do Vídeo Gravado no Teams](LINK_DO_VIDEO)
