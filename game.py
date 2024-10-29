import numpy as np
import argparse
import sys

# Possible launch arguments:
# --mode: Mode to run the game ("play" for playing mode, "train" for training mode). Default is "play".
# --player: Choose your symbol ("o" or "x"). Default is "o".
# --start: Choose who starts first ("o" or "x"). Default is "o".
# --headless: Run the game in headless mode (no console output). Useful for training mode.
# Running the script without args displays help

# Represents a slot in the Connect 4 board.
class Slot:

    def __init__(self):
        self.status = ' '

    # Updates the status of the slot with the given player symbol.
    def UpdateStatus(self, status):
        self.status = status

    # Returns the status of the slot.
    def GetStatus(self):
        return str(self.status)

    def __str__(self):
        return str(self.status)

# Represents the Connect 4 board.
class Board:

    def __init__(self, headless=False):
        self.headless = headless
        self.ResetBoard()

    # Prints information about the board.
    def BoardInfo(self):
        if not self.headless:
            print("Board Size: ", self.game_board.shape)
            print(self)

    # Returns a string representation of the board.
    def __str__(self):
        board_str = ""
        shape = self.game_board.shape

        board_str += "-" * (shape[0] * 4 + 1) + "\n"
        for row in range(shape[1]-1, -1, -1):
            row_str = "| "
            for col in range(shape[0]):
                row_str += self.game_board[col][row].GetStatus() + " | "
            board_str += row_str + "\n"
        board_str += "-" * (shape[0] * 4 + 1)
        return board_str

    # Resets the board to its initial empty state.
    def ResetBoard(self):
        self.game_board = np.array([[Slot() for _ in range(6)] for _ in range(7)])

    # Finds the next available slot position for the given column.
    def AvailableSlotInCol(self, col_index):
        for row in range(6):
            if self.game_board[col_index][row].GetStatus() == ' ':
                return row
        return None

# Contains the game logic for Connect 4.
class Connect4:

    def __init__(self, player_symbol='o', opponent='agent', starting_player='o', headless=False):
        self.headless = headless
        self.board = Board(headless=self.headless)
        self.player_symbol = player_symbol
        self.opponent_symbol = 'x' if player_symbol == 'o' else 'o'
        self.current_player = starting_player  # 'o' or 'x'
        self.winner = None
        self.game_over = False
        self.opponent = opponent  # 'agent' or 'human'

    # Resets the game to the initial state.
    def reset(self):
        self.board.ResetBoard()
        self.winner = None
        self.game_over = False
        self.current_player = 'o'  # Reset to 'o' or could be set to starting player
        return self.get_state()

    # Executes the given action and updates the game state.
    def step(self, action):
        if self.game_over:
            raise Exception("Game is over. Please reset the game.")

        # Adjust for zero-based index
        action -= 1

        # Validate the action
        if action < 0 or action >= 7:
            raise ValueError("Invalid action. Action must be between 1 and 7.")
        if self.board.AvailableSlotInCol(action) is None:
            raise ValueError("Invalid action. Column is full.")

        # Get the next available slot in the column
        row = self.board.AvailableSlotInCol(action)

        # Place the current player's piece in the slot
        self.board.game_board[action][row].UpdateStatus(self.current_player)

        # Check for a win condition
        if self.CheckWin((action, row), self.current_player):
            self.winner = self.current_player
            self.game_over = True
            reward = 1 if self.current_player == self.player_symbol else -1  # Reward for winning or losing
        else:
            # Check for a draw (if the board is full)
            if all(self.board.AvailableSlotInCol(col) is None for col in range(7)):
                self.game_over = True
                reward = 0  # No reward for a draw
            else:
                reward = 0  # No immediate reward

        # Prepare the state and info to return
        state = self.get_state()
        done = self.game_over
        info = {'current_player': self.current_player}

        # Switch to the other player if the game is not over
        if not self.game_over:
            self.current_player = 'x' if self.current_player == 'o' else 'o'

        return state, reward, done, info

    # Returns the current state of the game as a numpy array.
    def get_state(self):
        state = np.zeros((6, 7))
        for col in range(7):
            for row in range(6):
                status = self.board.game_board[col][row].GetStatus()
                if status == 'o':
                    state[5 - row][col] = 1  # Flip row index for standard representation
                elif status == 'x':
                    state[5 - row][col] = -1
                else:
                    state[5 - row][col] = 0
        return state

    # Returns a list of valid actions
    def get_valid_actions(self):
        valid_actions = [col + 1 for col in range(7) if self.board.AvailableSlotInCol(col) is not None]
        return valid_actions

    # Prints the current state of the board to the console.
    def render(self):
        if not self.headless:
            print(self.board)

    # Checks if the current player has won the game after their last move.
    def CheckWin(self, position, player):
        col, row = position
        board = self.board.game_board

        # Directions to check: horizontal, vertical, and two diagonals
        directions = [
            (1, 0),  # Horizontal to the right
            (0, 1),  # Vertical upwards
            (1, 1),  # Diagonal up-right
            (1, -1), # Diagonal down-right
        ]

        for dx, dy in directions:
            count = 1  # Include the current piece

            # Check in the positive direction
            for step in range(1, 4):
                x = col + dx * step
                y = row + dy * step
                if 0 <= x < 7 and 0 <= y < 6 and board[x][y].GetStatus() == player:
                    count += 1
                else:
                    break

            # Check in the negative direction
            for step in range(1, 4):
                x = col - dx * step
                y = row - dy * step
                if 0 <= x < 7 and 0 <= y < 6 and board[x][y].GetStatus() == player:
                    count += 1
                else:
                    break

            # Check if four or more in a row
            if count >= 4:
                return True

        return False

    # Prompt human to move
    def human_move(self):
        valid = False
        while not valid:
            try:
                action = int(input(f"Player '{self.player_symbol}', choose a column (1-7): "))
                if action in self.get_valid_actions():
                    valid = True
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please enter an integer between 1 and 7.")
        return action

    def agent_move(self):
        # Placeholder method for agent's move
        valid_actions = self.get_valid_actions()
        action = np.random.choice(valid_actions)
        return action

def main():
    parser = argparse.ArgumentParser(description='Connect4 Game')
    parser.add_argument('--mode', type=str, default='play', choices=['play', 'train'],
                        help='Mode to run the game: "play" for playing mode, "train" for training mode.')
    parser.add_argument('--player', type=str, default='o', choices=['o', 'x'],
                        help='Choose your symbol: "o" or "x".')
    parser.add_argument('--start', type=str, default='o', choices=['o', 'x'],
                        help='Choose who starts first: "o" or "x".')
    parser.add_argument('--headless', action='store_true',
                        help='Run the game in headless mode (no console output). Useful for training mode.')

    # Display help message if no arguments given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    # Init with given args
    game = Connect4(player_symbol=args.player, opponent='agent' if args.mode == 'train' else 'human',
                    starting_player=args.start, headless=args.headless)

    if args.mode == 'play':
        # Playing mode: human vs agent
        if not game.headless:
            game.render()
        while not game.game_over:
            if game.current_player == game.player_symbol:
                # Human player turn
                action = game.human_move()
            else:
                # Agent turn
                action = game.agent_move()
                if not game.headless:
                    print(f"Agent '{game.current_player}' chooses column {action}")
            state, reward, done, info = game.step(action)
            if not game.headless:
                game.render()
            if done:
                if not game.headless:
                    if game.winner == game.player_symbol:
                        print("Congratulations! You win!")
                    elif game.winner == game.opponent_symbol:
                        print("You lose. The agent wins.")
                    else:
                        print("It's a draw.")
                break
    elif args.mode == 'train':
        # Implement training logic here
        print("Implement training logic here")

if __name__ == '__main__':
    main()
