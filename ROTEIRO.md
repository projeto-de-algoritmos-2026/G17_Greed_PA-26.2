# Roteiro da apresentação — Nightfall Looter (5 min)

Um joga, o outro fala. Quem fala não mexe no teclado.
Deixem o jogo aberto no menu antes de começar a gravar.

| Tempo | Quem fala | Tela | Assunto |
|---|---|---|---|
| 0:00 – 0:30 | Daniel | Menu | O que é o jogo |
| 0:30 – 1:30 | Daniel | Masmorra (andar 1) | A mochila |
| 1:30 – 2:30 | Daniel | Resultado | Knapsack 0/1 e fracionária |
| 2:30 – 3:20 | Matheus | Mercador: vender e comprar | Troco |
| 3:20 – 4:20 | Matheus | Mercador: pergaminho | Huffman |
| 4:20 – 5:00 | Matheus | Código / testes | Fechamento |

---

## 1. Abertura (30s) — Daniel

- "Nightfall Looter é um jogo educativo sobre algoritmos gulosos."
- "O jogador alterna entre masmorra, onde enche a mochila, e mercador, onde vende e compra melhorias."
- "São quatro algoritmos: mochila 0/1 gulosa, mochila fracionária, troco e Huffman."

## 2. Masmorra (1 min) — Daniel

- "Cada baú tem itens com peso e valor. A mochila aguenta 30kg e o andar tem 52kg: não dá para levar tudo."
- "É o problema da mochila: o jogador decide o que levar."
- Mostrar a barra de peso: "No último terço a mochila fica pesada e o personagem anda lento."
- "O andar 1 é fixo, serve de tutorial. Os seguintes são gerados por BSP com itens sorteados."

**Quem joga:** pegar Armadura Pesada + Saco de Moedas + Anel de Prata + Rubi (30kg, $455) e o pergaminho. Descer a escada.

## 3. Resultado (1 min) — Daniel

- "Aqui o jogo roda o guloso com a mesma capacidade: ordena por valor/kg e pega cada item inteiro que ainda couber."
- "Ele fez $432 e nós $455. Com itens inteiros o guloso não é ótimo: ele pegou o Escudo cedo e ficou sem espaço para o Saco de Moedas."
- Apontar a terceira barra: "O teto é a mochila fracionária. Se desse para cortar os itens, o guloso seria ótimo, e ninguém passa desse valor."
- "No jogo isso aparece nos itens a granel, que saem 1kg por vez."
- "As colunas de baixo mostram só a diferença entre as duas mochilas."

## 4. Troco (50s) — Matheus

- Vender tudo: "O mercador paga com o menor número de moedas usando o troco guloso: sempre a maior moeda que cabe."
- "Com as moedas 100, 50, 25, 10, 5 e 1 o guloso é ótimo."
- Comprar "Mochila maior": "Na compra é o jogador que monta o pagamento, contra o relógio. Se usar o mesmo número de moedas do guloso, ganha 10% de desconto."

**Quem joga:** pagar 235 com 100 + 100 + 25 + 10 e apertar Enter.

## 5. Huffman (1 min) — Matheus

- Abrir "Decifrar pergaminho": "Os pergaminhos estão codificados em Huffman."
- "O algoritmo junta sempre as duas letras menos frequentes, usando uma fila de prioridade. A letra mais comum fica com o código mais curto."
- Mostrar a tabela: "Nenhum código é começo de outro, então dá para ler os bits sem separador."
- "O jogador tem uma chance e um tempo limite. Se errar, o pergaminho vale metade. A melhoria Decifrador lê sozinha."

**Quem joga:** apertar Espaço para começar e digitar MAPA (12 segundos).

## 6. Fechamento (40s) — Matheus

- "Os algoritmos ficam em `algoritmos/`, como funções puras, sem pygame. As fases só chamam e desenham."
- "Temos testes com pytest para os três arquivos, incluindo os casos em que o guloso falha."
- Resumo final:

| Problema | O guloso é ótimo? |
|---|---|
| Mochila 0/1 | Não — por isso dá para ganhar dele |
| Mochila fracionária | Sim |
| Troco (moedas do jogo) | Sim |
| Huffman | Sim |

- "É isso, obrigado."

---

## Se sobrar ou faltar tempo

- **Faltando:** cortar a fala do BSP (parte 2) e a da fila de prioridade (parte 5).
- **Sobrando:** mostrar o teste `test_guloso_nem_sempre_e_otimo_com_moedas_estranhas` — com moedas 1, 3 e 4 o guloso usa 3 moedas para pagar 6, e o melhor seria 3 + 3.
