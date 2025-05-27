import tkinter as tk
import random

class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.visible = [['-' for _ in range(cols)] for _ in range(rows)]
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
        if self.board[row][col] == 'M':
            return False  # Hit a mine
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

    def is_won(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.visible[r][c] == '-' and (r, c) not in self.mine_positions:
                    return False
        return True


class MinesweeperAI:
    def __init__(self, game, gui):
        self.game = game
        self.gui = gui

    def play_step(self):
        if self.game.is_won():
            self.gui.update_status("AI won the game!")
            return

        # Escolher célula aleatória não revelada
        hidden_cells = [(r, c) for r in range(self.game.rows)
                        for c in range(self.game.cols)
                        if self.game.visible[r][c] == '-']

        if not hidden_cells:
            self.gui.update_status("No safe moves left!")
            return

        row, col = random.choice(hidden_cells)

        if not self.game.reveal(row, col):
            self.gui.update_board()
            self.gui.update_status("Hit a mine! Game over.")
            return

        self.gui.update_board()
        self.gui.window.after(2000, self.play_step)


class MinesweeperGUI:
    def __init__(self, game):
        self.game = game
        self.window = tk.Tk()
        self.window.title("Minesweeper AI")
        self.buttons = [[None for _ in range(game.cols)] for _ in range(game.rows)]
        self.real_labels = [[None for _ in range(game.cols)] for _ in range(game.rows)]

        self.status_label = tk.Label(self.window, text="AI is playing...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Tabuleiro visível (jogo)
        self.frame = tk.LabelFrame(self.window, text="Tabuleiro visível", padx=5, pady=5)
        self.frame.pack()

        for r in range(game.rows):
            for c in range(game.cols):
                btn = tk.Label(self.frame, text='-', width=4, height=2, font=("Courier", 14), relief="raised", borderwidth=1)
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

        # Tabuleiro real (debug)
        self.real_frame = tk.LabelFrame(self.window, text="Tabuleiro real (debug)", padx=5, pady=5)
        self.real_frame.pack(pady=10)

        for r in range(game.rows):
            for c in range(game.cols):
                val = self.game.board[r][c]
                lbl = tk.Label(self.real_frame, text=val, width=4, height=2, font=("Courier", 14), relief="solid", borderwidth=1, bg="#f0f0f0")
                lbl.grid(row=r, column=c)
                self.real_labels[r][c] = lbl

        self.ai = MinesweeperAI(game, self)
        self.window.after(1000, self.ai.play_step)
        self.window.mainloop()

    def update_board(self):
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                value = self.game.visible[r][c]
                self.buttons[r][c]['text'] = value
                if value != '-':
                    self.buttons[r][c]['relief'] = 'sunken'

    def update_status(self, message):
        self.status_label.config(text=message)


if __name__ == "__main__":
    game = Minesweeper(5, 5, 5)
    gui = MinesweeperGUI(game)
