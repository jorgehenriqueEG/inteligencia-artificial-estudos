💣 Minesweeper com IA usando Python + Tkinter

Este projeto é uma implementação interativa do jogo Campo Minado (Minesweeper) com uma Inteligência Artificial que joga sozinha, explicando seu raciocínio a cada jogada. A interface gráfica foi construída com Tkinter.
🚀 Funcionalidades

    Jogo clássico de Campo Minado, com bandeiras, explosões e vitória ao limpar o tabuleiro.

    Interface visual com botões grandes, cores e emojis para facilitar a experiência.

    IA jogadora que:

        Analisa o tabuleiro e identifica jogadas seguras e minas certas.

        Usa probabilidade para decidir jogadas quando não há certeza.

        Exibe o raciocínio de cada jogada em tempo real.

    Contador de tempo e minas restantes.

    Visualização opcional do tabuleiro real (debug) com todas as minas e números.

🧠 Inteligência Artificial

A IA segue três passos principais:

    Jogadas Certas: Identifica células seguras e minas com base no número de vizinhos escondidos e bandeiras.

    Probabilidade: Se não há jogadas seguras, estima a chance de cada célula conter uma mina.

    Decisão: Escolhe a célula com menor probabilidade de conter mina e joga nela.

Ela também registra o motivo da decisão para fins de análise no painel lateral da interface.
🛠️ Tecnologias usadas

    Python 3

    Tkinter (GUI)

    Estruturas como listas, conjuntos e recursão (flood fill)

📷 Interface

    Tabuleiro principal com botões.

    Painel lateral com raciocínio da IA.

    Tabuleiro real (para debug).

    Indicadores de tempo e minas restantes.

📁 Organização

O código está dividido em três classes principais:

    Minesweeper: Lógica principal do jogo.

    MinesweeperAI: Inteligência Artificial que joga automaticamente.

    MinesweeperGUI: Interface gráfica e interações com o jogador.

▶️ Como executar

Salve o código como minesweeper_ai.py e execute com Python 3:

python minesweeper_ai.py
