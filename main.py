import tkinter as tk
from tkinter import messagebox
import random
import time

# ---------------------------
# SUDOKU GENERATOR
# ---------------------------
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)

    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_board():
    board = [[0] * 9 for _ in range(9)]

    def fill():
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if fill():
                                return True
                            board[row][col] = 0
                    return False
        return True

    fill()
    return board


def remove_numbers(board, difficulty):
    attempts = {
        "Easy": 30,
        "Medium": 40,
        "Hard": 50,
        "Expert": 60
    }

    remove = attempts[difficulty]

    while remove > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            remove -= 1

    return board


# ---------------------------
# MAIN GAME CLASS
# ---------------------------
class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Sudoku Game")

        self.cells = []
        self.solution = []
        self.board = []

        self.timer_running = False
        self.start_time = None

        self.score = 0

        self.build_ui()
        self.new_game()

    # ---------------------------
    # UI
    # ---------------------------
    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(pady=10)

        self.timer_label = tk.Label(top, text="Time: 00:00", font=("Arial", 14))
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.score_label = tk.Label(top, text="Score: 0", font=("Arial", 14))
        self.score_label.pack(side=tk.LEFT, padx=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # Difficulty dropdown
        tk.Label(btn_frame, text="Difficulty:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        self.difficulty_var = tk.StringVar(value="Medium")
        difficulty_menu = tk.OptionMenu(
            btn_frame,
            self.difficulty_var,
            "Easy",
            "Medium",
            "Hard",
            "Expert",
            command=self.change_difficulty
        )
        difficulty_menu.config(font=("Arial", 11))
        difficulty_menu.pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Hint", command=self.give_hint).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Solve", command=self.show_solution).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Rules", command=self.show_rules).pack(side=tk.LEFT, padx=5)

        grid = tk.Frame(self.root)
        grid.pack()

        for r in range(9):
            row_cells = []
            for c in range(9):
                e = tk.Entry(grid, width=2, font=("Arial", 18), justify="center")
                e.grid(row=r, column=c, padx=2, pady=2)

                e.bind("<KeyRelease>", lambda ev, row=r, col=c: self.check_input(row, col))
                e.bind("<FocusIn>", lambda ev, row=r, col=c: self.highlight(row, col))

                row_cells.append(e)
            self.cells.append(row_cells)

    def change_difficulty(self, value):
        self.new_game()

    # ---------------------------
    # TIMER
    # ---------------------------
    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            mins, secs = elapsed // 60, elapsed % 60
            self.timer_label.config(text=f"Time: {mins:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)

    # ---------------------------
    # NEW GAME
    # ---------------------------
    def new_game(self):
        difficulty = self.difficulty_var.get()

        self.timer_running = False
        self.start_time = None

        self.timer_label.config(text="Time: 00:00")
        self.score = 0
        self.score_label.config(text="Score: 0")

        full = generate_board()
        self.solution = [row[:] for row in full]
        puzzle = [row[:] for row in full]
        self.board = remove_numbers(puzzle, difficulty)

        for r in range(9):
            for c in range(9):
                val = self.board[r][c]
                cell = self.cells[r][c]
                cell.config(state="normal")
                cell.delete(0, tk.END)

                if val != 0:
                    cell.insert(0, str(val))
                    cell.config(state="disabled", disabledforeground="black", bg="#f1f2f6")
                else:
                    cell.config(state="normal", fg="black", bg="white")

    # ---------------------------
    # INPUT CHECK
    # ---------------------------
    def check_input(self, r, c):
        if not self.timer_running:
            self.start_timer()

        val = self.cells[r][c].get()

        if val == "":
            self.cells[r][c].config(fg="black")
            return

        if not val.isdigit() or not (1 <= int(val) <= 9):
            self.cells[r][c].delete(0, tk.END)
            return

        if int(val) == self.solution[r][c]:
            self.cells[r][c].config(fg="green")
            self.score += 10
        else:
            self.cells[r][c].config(fg="red")
            self.score -= 5

        self.score_label.config(text=f"Score: {self.score}")

        if self.check_win():
            self.timer_running = False
            messagebox.showinfo("🎉", f"You Win!\nDifficulty: {self.difficulty_var.get()}")

    # ---------------------------
    # HIGHLIGHT
    # ---------------------------
    def highlight(self, r, c):
        for i in range(9):
            for j in range(9):
                current_state = self.cells[i][j]["state"]
                if current_state == "disabled":
                    self.cells[i][j].config(bg="#f1f2f6")
                else:
                    self.cells[i][j].config(bg="white")

        for i in range(9):
            if self.cells[r][i]["state"] != "disabled":
                self.cells[r][i].config(bg="#dfe6e9")
            if self.cells[i][c]["state"] != "disabled":
                self.cells[i][c].config(bg="#dfe6e9")

    # ---------------------------
    # HINT
    # ---------------------------
    def give_hint(self):
        for r in range(9):
            for c in range(9):
                if self.cells[r][c]["state"] == "normal" and self.cells[r][c].get() == "":
                    self.cells[r][c].insert(0, str(self.solution[r][c]))
                    self.cells[r][c].config(fg="blue")
                    self.score -= 10
                    self.score_label.config(text=f"Score: {self.score}")
                    return

    # ---------------------------
    def check_win(self):
        for r in range(9):
            for c in range(9):
                val = self.cells[r][c].get()
                if val == "" or not val.isdigit() or int(val) != self.solution[r][c]:
                    return False
        return True

    def show_solution(self):
        for r in range(9):
            for c in range(9):
                self.cells[r][c].config(state="normal")
                self.cells[r][c].delete(0, tk.END)
                self.cells[r][c].insert(0, str(self.solution[r][c]))
                self.cells[r][c].config(fg="blue")
        self.timer_running = False

    def show_rules(self):
        messagebox.showinfo(
            "Sudoku Rules",
            "Grid Structure: The standard puzzle is a 9x9 grid, divided into nine 3x3, non-overlapping boxes.\n\n"
            "Row Rule: Each of the nine horizontal rows must contain all digits from 1 to 9 without repetition.\n\n"
            "Column Rule: Each of the nine vertical columns must contain all digits from 1 to 9 without repetition.\n\n"
            "Box Rule: Each of the nine 3x3 boxes must contain all digits from 1 to 9 without repetition."
        )


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()
