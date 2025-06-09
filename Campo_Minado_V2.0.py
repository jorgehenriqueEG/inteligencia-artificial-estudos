import tkinter as tk
import random
import time

class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.visible = [['-' for _ in range(cols)] for _ in range(rows)]
        self.flags = set()
        self.mine_positions = set()
        self._place_mines()
        self._calculate_numbers()

    def _place_mines(self):
        while len(self.mine_positions) < self.mines:
            r, c = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))
        for r, c in self.mine_positions:
            self.board[r][c] = 'M'

    def _calculate_numbers(self):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == 'M':
                    continue
                count = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] == 'M':
                        count += 1
                self.board[r][c] = str(count)

    def reveal(self, row, col):
        if (row, col) in self.flags or self.visible[row][col] != '-':
            return True
        if self.board[row][col] == 'M':
            self.visible[row][col] = 'M'
            return False
        self._flood_fill(row, col)
        return True

    def _flood_fill(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols) or self.visible[row][col] != '-':
            return
        self.visible[row][col] = self.board[row][col]
        if self.board[row][col] == '0':
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                self._flood_fill(row + dr, col + dc)

    def toggle_flag(self, row, col):
        if self.visible[row][col] != '-':
            return
        if (row, col) in self.flags:
            self.flags.remove((row, col))
        else:
            self.flags.add((row, col))

    def is_won(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.visible[r][c] == '-' and (r, c) not in self.mine_positions:
                    return False
        return True

    def mines_left(self):
        return self.mines - len(self.flags)

class MinesweeperAI:
    def __init__(self, game, gui):
        self.game = game
        self.gui = gui
        self.reason = ""

    def play_step(self):
        if self.game.is_won():
            self.gui.update_status(" IA venceu!")
            return

        safe_moves, mine_moves, reasoning = self.find_safe_and_mine_moves()
        if safe_moves:
            row, col = safe_moves[0]
            self.reason = f"Escolheu ({row},{col}) porque é seguro ({reasoning.get((row, col), '')})"
            self.game.reveal(row, col)
            self.gui.update_board()
            self.gui.update_ai_reason(self.reason)
            self.gui.window.after(1000, self.play_step)
            return
        elif mine_moves:
            row, col = mine_moves[0]
            self.reason = f"Colocou bandeira em ({row},{col}) porque é certamente mina ({reasoning.get((row, col), '')})"
            self.game.toggle_flag(row, col)
            self.gui.update_board()
            self.gui.update_ai_reason(self.reason)
            self.gui.window.after(1000, self.play_step)
            return

        hidden_cells = [(r, c) for r in range(self.game.rows)
                        for c in range(self.game.cols)
                        if self.game.visible[r][c] == '-' and (r, c) not in self.game.flags]
        if not hidden_cells:
            self.gui.update_status("sem movimentos seguros restantes!")
            return

        min_prob = 1.1
        best_cells = []
        for cell in hidden_cells:
            prob = self.estimate_mine_probability(cell)
            if prob < min_prob:
                min_prob = prob
                best_cells = [cell]
            elif prob == min_prob:
                best_cells.append(cell)
        row, col = random.choice(best_cells)
        self.reason = f"Escolheu ({row},{col}) por menor probabilidade estimada de mina: {min_prob:.2%}"
        if not self.game.reveal(row, col):
            self.gui.update_board(exploded=(row, col))
            self.gui.update_status("acertou a mina, fim de jogo.")
            self.gui.update_ai_reason(self.reason + " (explodiu!)")
            return
        self.gui.update_board()
        self.gui.update_ai_reason(self.reason)
        self.gui.window.after(1000, self.play_step)

    def find_safe_and_mine_moves(self):
        safe_moves = []
        mine_moves = []
        reasoning = {}
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                val = self.game.visible[r][c]
                if val not in '12345678':
                    continue
                num = int(val)
                neighbors = [(r+dr, c+dc) for dr, dc in directions
                             if 0 <= r+dr < self.game.rows and 0 <= c+dc < self.game.cols]
                hidden = [cell for cell in neighbors if self.game.visible[cell[0]][cell[1]] == '-' and cell not in self.game.flags]
                flagged = [cell for cell in neighbors if cell in self.game.flags]
                if len(flagged) == num and hidden:
                    for cell in hidden:
                        safe_moves.append(cell)
                        reasoning[cell] = f"todas as minas já marcadas ao redor"
                if len(flagged) + len(hidden) == num and hidden:
                    for cell in hidden:
                        mine_moves.append(cell)
                        reasoning[cell] = f"todas as células escondidas ao redor são minas"
        return safe_moves, mine_moves, reasoning

    def estimate_mine_probability(self, cell):
        total_hidden = sum(
            1 for r in range(self.game.rows) for c in range(self.game.cols)
            if self.game.visible[r][c] == '-' and (r, c) not in self.game.flags
        )
        if total_hidden == 0:
            return 1
        return self.game.mines_left() / total_hidden

class MinesweeperGUI:
    def __init__(self, game):
        self.game = game
        self.window = tk.Tk()
        self.window.title("Minesweeper AI")
        self.window.geometry("700x500")
        self.start_time = time.time()
        self.timer_running = True
        self.exploded_cell = None

        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0)

        top_frame = tk.Frame(self.window)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)

        self.status_label = tk.Label(top_frame, text="IA ESTÁ JOGANDO...", font=("Arial", 14))
        self.status_label.grid(row=0, column=0, sticky="w", padx=10)

        self.timer_label = tk.Label(top_frame, text="Tempo: 0s", font=("Arial", 14))
        self.timer_label.grid(row=0, column=1)

        self.mines_label = tk.Label(top_frame, text=f"Minas restantes: {self.game.mines_left()}", font=("Arial", 14))
        self.mines_label.grid(row=0, column=2, sticky="e", padx=10)

        self.frame = tk.LabelFrame(self.window, text="Tabuleiro", padx=5, pady=5)
        self.frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.frame.rowconfigure(tuple(range(game.rows)), weight=1)
        self.frame.columnconfigure(tuple(range(game.cols)), weight=1)

        self.buttons = [[None for _ in range(game.cols)] for _ in range(game.rows)]
        for r in range(game.rows):
            for c in range(game.cols):
                btn = tk.Label(self.frame, text='-', width=8, height=15, font=("Courier", 30), relief="raised", borderwidth=2, bg="#bdbdbd")
                btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, row=r, col=c: self.on_left_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self.on_right_click(row, col))
                self.buttons[r][c] = btn

        side_frame = tk.LabelFrame(self.window, text="Raciocínio da IA", padx=5, pady=5)
        side_frame.grid(row=1, column=1, sticky="ns", padx=5, pady=10)
        side_frame.rowconfigure(0, weight=1)
        self.ai_reason_text = tk.Text(side_frame, width=30, height=20, font=("Arial", 10), state="disabled", wrap="word")
        self.ai_reason_text.grid(row=0, column=0, sticky="nsew")

        self.real_frame = tk.LabelFrame(self.window, text="Tabuleiro real (debug)", padx=5, pady=5)
        self.real_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.real_labels = [[None for _ in range(game.cols)] for _ in range(game.rows)]
        for r in range(game.rows):
            for c in range(game.cols):
                val = self.game.board[r][c]
                lbl = tk.Label(self.real_frame, text=val, width=4, height=2, font=("Courier", 14), relief="solid", borderwidth=1, bg="#f0f0f0")
                lbl.grid(row=r, column=c)
                self.real_labels[r][c] = lbl

        self.update_board()
        self.update_timer()
        self.ai = MinesweeperAI(game, self)
        self.window.after(1000, self.ai.play_step)
        self.window.mainloop()

    def on_left_click(self, row, col):
        if self.game.visible[row][col] != '-' or (row, col) in self.game.flags:
            return
        if not self.game.reveal(row, col):
            self.update_board(exploded=(row, col))
            self.update_status("Você perdeu! (explodiu uma mina)")
            self.timer_running = False
        else:
            self.update_board()
            if self.game.is_won():
                self.update_status("Você venceu!")
                self.timer_running = False

    def on_right_click(self, row, col):
        self.game.toggle_flag(row, col)
        self.update_board()

    def update_board(self, exploded=None):
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                btn = self.buttons[r][c]
                value = self.game.visible[r][c]
                if (r, c) in self.game.flags and value == '-':
                    btn['text'] = '🚩'
                    btn['bg'] = "#ffe066"
                    btn['relief'] = "raised"
                elif value == '-':
                    btn['text'] = '-'
                    btn['bg'] = "#bdbdbd"
                    btn['relief'] = "raised"
                elif value == 'M':
                    if exploded and (r, c) == exploded:
                        btn['text'] = '💥'
                        btn['bg'] = "#ff4d4d"
                    else:
                        btn['text'] = '💣'
                        btn['bg'] = "#ffb3b3"
                    btn['relief'] = "sunken"
                else:
                    btn['text'] = value if value != '0' else ''
                    btn['bg'] = "#00FF22"
                    btn['relief'] = "sunken"
        self.mines_label.config(text=f"Minas restantes: {self.game.mines_left()}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Tempo: {elapsed}s")
            self.window.after(1000, self.update_timer)

    def update_ai_reason(self, reason):
        self.ai_reason_text.config(state="normal")
        self.ai_reason_text.insert("end", reason + "\n")
        self.ai_reason_text.see("end")
        self.ai_reason_text.config(state="disabled")

if __name__ == "__main__":
    game = Minesweeper(8, 10, 15)
    gui = MinesweeperGUI(game)

# ignora a bandeira , ou deixo escondido  (linha 36)
# acertou a mina (linha 39)
# IA: lógica básica de dedução (linha 61)
# Se não sabe, escolhe aleatório (linha 77)
# Probabilidade simples: tenta escolher a célula com menor risco (heurística) (linha 80)
# Heurística simples: minas restantes dividido por células escondidas restantes (linha 117)
# Se o número de bandeiras é igual ao número, o resto é seguro (linha 143)
# Se número de bandeiras + células escondidas == número, todas escondidas são minas (linha 146)
# se nescessario posso deixar em ingles ou portugues fica ao criterio de quem for usar 
# Se não houver células escondidas, não há jogadas seguras (linha 152)
# criar um método para estimar a probabilidade de mina (linha 155)
# criar um banco de dados para armazenar as jogadas (linha 158)
# criar um sql para melhorar a performance (linha 161)
# criar um método para salvar o jogo (linha 164)
# criar um método para carregar o jogo (linha 167)
# criar um método para reiniciar o jogo (linha 170)
# criar um método para salvar o jogo em um arquivo (linha 173)
# tlvz criar um sql para salvar e melhorar a performace (discutir com o povo dps)
# analisar o desempenho da IA (e discutir melhorias)
# procurar um metodo de aprendizado de máquina para melhorar a IA 
# entender o que é um algoritmo de aprendizado de máquina
# e como ele pode ser aplicado ao jogo de campo minado
# discutir com o professor sobre a possibilidade de usar aprendizado de máquina
# e como isso pode ser implementado no jogo de campo minado

