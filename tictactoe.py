class TicTacToe:
    def __init__(self, size=3):
        self.size = size
        self.grid = {i: {j: " " for j in range(size)} for i in range(size)}
        self.turn = 0  # 0 for player 1 (X) and 1 for player 2 (O)

    def place(self, x, y):
        if x < 0 or x >= self.size or y < 0 or y >= self.size:  # Check grid boundaries
            return False
        if self.grid[x][y] != " ":  # Check if cell is already occupied
            return False
        # Determine the piece based on whose turn it is
        piece = "X" if self.turn == 0 else "O"
        # Place the piece
        self.grid[x][y] = piece
        # Check for a win after the piece is placed
        if self.check_winner(x, y, piece):
            self.print_board()  # Print the final winning board
            winner = self.turn  # Capture the winner before toggling the turn
            self.reset_game()  # Optional: reset game after a win
            return winner
        # Check for Cat's Game (draw)
        if self.check_draw():
            self.print_board()  # Print the final board
            self.reset_game()  # Optional: reset game after a draw
            return "Draw"
        # Toggle the turn
        self.turn = 1 - self.turn
        self.print_board()  # Print board after every move
        return None  # Indicate ongoing game

    def check_winner(self, x, y, piece):
        # Check the row and column of the last move for a win
        if all(self.grid[x][j] == piece for j in range(self.size)) or all(self.grid[i][y] == piece for i in range(self.size)):
            return True
        # Check diagonals only if x and y are on a diagonal
        if x == y and all(self.grid[i][i] == piece for i in range(self.size)):  # Check the main diagonal
            return True
        if x + y == self.size - 1 and all(self.grid[i][self.size-i-1] == piece for i in range(self.size)):  # Check the anti-diagonal
            return True
        return False

    def check_draw(self):
        # Check if all cells are filled
        return all(self.grid[i][j] != " " for i in range(self.size) for j in range(self.size))

    def reset_game(self):
       # Resets the game to the initial state
        self.grid = {i: {j: " " for j in range(self.size)} for i in range(self.size)}
        self.turn = 0  # Optionally reset the turn to player 0

    def print_board(self):
        for row in range(self.size):
            print('|'.join(self.grid[row].values()))
            if row < self.size - 1:
                print("-" * (self.size * 2 - 1))  # Print a line between rows
