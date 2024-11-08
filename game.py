import numpy as np
import argparse
import sys
import agent
import pyqlearning

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
    def update_status(self, status):
        self.status = status

    # Returns the status of the slot.
    def get_status(self):
        return str(self.status)

    def __str__(self):
        return str(self.status)

# Represents the Connect 4 board.
class Board:

    def __init__(self, headless=False):
        self.headless = headless
        self.reset_board()

    # Prints information about the board.
    def board_info(self):
        if not self.headless:
            print("Board Size: ", self.game_board.shape)
            print(self)

    # Returns a string representation of the board.
    def __str__(self):
        board_str = ""
        shape = self.game_board.shape

        # Printing the top line
        board_str += "-" * (shape[0] * 4 + 1) + "\n"

        # Printing each cell
        for row in range(shape[1]-1, -1, -1):
            row_str = "| "
            for col in range(shape[0]):
                row_str += self.game_board[col][row].get_status() + " | "
            board_str += row_str + "\n"

        # Printing the bottom line
        board_str += "-" * (shape[0] * 4 + 1)

        # Returning the string
        return board_str

    # Resets the board to its initial empty state.
    def reset_board(self):
        self.game_board = np.array([[Slot() for _ in range(6)] for _ in range(7)])

    # Finds the next available slot position for the given column.
    def available_slot_in_col(self, col_index):
        for row in range(6):
            if self.game_board[col_index][row].get_status() == ' ':
                return row
        return None
    
    # Returns True if the gameboard has been completely filled
    def is_full(self):
        return all(self.available_slot_in_col(col) is None for col in range(7))
    

# Contains the game logic for Connect 4.
class Connect4:

    def __init__(self, mode='play', player1='human', player2='random', player1_symbol='o', player2_symbol='x', starting_player='player1', headless=False):
        self.player1_symbol = player1_symbol            # Sets the first player's symbol
        self.player2_symbol = player2_symbol            # Sets the second player's symbol
        self.headless = headless                        # Decides whether to print board
        self.board = Board(headless=self.headless)      # Sets up board
        self.winner = None                              # Stores the winning player's symbol for reference
        self.game_over = False                          # Boolean for tracking if the game ended
        self.starting_player = starting_player          # Storing the first player for use in resetting
        self.mode = mode

        # Sets the starting symbol (Ex. 'o' or 'x')
        self.current_player = self.player1_symbol if starting_player == 'player1' else self.player2_symbol

        # Setting up player 1
        if player1 == 'human':
            self.player1 = agent.HumanPlayer(self.player1_symbol, self.headless)
        elif player1 == 'random':
            self.player1 = agent.RandomAgent(self.player1_symbol, self.headless)
        elif player1 == 'ql':
            self.player1 = agent.QLearningAgent(self.player1_symbol, self.headless, mode=mode)

        # Setting up player 2
        if player2 == 'human':
            self.player2 = agent.HumanPlayer(self.player2_symbol, self.headless)
        elif player2 == 'random':
            self.player2 = agent.RandomAgent(self.player2_symbol, self.headless)
        elif player2 == 'ql':
            self.player2 = agent.QLearningAgent(self.player2_symbol, self.headless, mode=mode)

    # Resets the game to the initial state.
    def reset(self):
        self.board.reset_board()
        self.winner = None
        self.game_over = False
        self.current_player = self.player1_symbol if self.starting_player == 'player1' else self.player2_symbol
        return self.get_state()

    # Executes the given action and updates the game state.
    def step(self, action):
        # Game already ended
        if self.game_over:
            raise Exception("Game is over. Please reset the game.")

        # Adjust for zero-based index
        action -= 1

        # Get the next available slot in the column
        available_row = self.board.available_slot_in_col(action)

        # Validate the action
        if action < 0 or action >= 7:
            raise ValueError("Invalid action. Action must be between 1 and 7.")
        if available_row is None:
            raise ValueError("Invalid action. Column is full.")

        # Place the current player's piece in the slot
        self.board.game_board[action][available_row].update_status(self.current_player)

        # Check for a win condition
        if self.check_win((action, available_row), self.current_player):
            self.winner = self.current_player
            self.game_over = True
            reward = 1 # if self.current_player == self.player1_symbol else -1  # Reward for winning or losing

        # Check for a draw (if the board is full)
        elif self.board.is_full():
            self.game_over = True
            reward = 0  # No reward for a draw

        # No end condition
        else:
            reward = 0 # No immediate reward

        # Prepare the state and info to return
        state = self.get_state()
        done = self.game_over
        info = {'current_player': self.current_player}

        # Switch to the other player if the game is not over
        if not self.game_over:
            if self.current_player == self.player1_symbol:
                self.current_player = self.player2_symbol
            elif self.current_player == self.player2_symbol:
                self.current_player = self.player1_symbol

        return state, reward, done, info

    # Returns the current state of the game as a numpy array.
    def get_state(self):
        state = np.zeros((6, 7))
        for col in range(7):
            for row in range(6):
                status = self.board.game_board[col][row].get_status()
                if status == 'o':
                    state[5 - row][col] = 1  # Flip row index for standard representation
                elif status == 'x':
                    state[5 - row][col] = -1
                else:
                    state[5 - row][col] = 0
        return state

    # Returns a list of valid actions
    def get_valid_actions(self):
        valid_actions = [col + 1 for col in range(7) if self.board.available_slot_in_col(col) is not None]
        return valid_actions

    # Prints the current state of the board to the console.
    def render(self):
        if not self.headless:
            print(self.board)

    # Checks if the current player has won the game after their last move.
    def check_win(self, position, player):
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
                if 0 <= x < 7 and 0 <= y < 6 and board[x][y].get_status() == player:
                    count += 1
                else:
                    break

            # Check in the negative direction
            for step in range(1, 4):
                x = col - dx * step
                y = row - dy * step
                if 0 <= x < 7 and 0 <= y < 6 and board[x][y].get_status() == player:
                    count += 1
                else:
                    break

            # Check if four or more in a row
            if count >= 4:
                return True

        return False
    
    def play_game(self):
        
        # Displaying board if necessary
        if not self.headless:
            self.render()

        state = self.reset()
        done = False
        while not done:

            # Getting the next move if playing
            if self.current_player == self.player1_symbol:
                action = self.player1.next_move(self.get_valid_actions(), state)
            else:
                action = self.player2.next_move(self.get_valid_actions(), state)

            # Making the next move
            next_state, reward, done, curr_player = self.step(action)

            # Learning from the action (if applicable)
            if type(self.player1) == agent.QLearningAgent() and self.mode == 'train':
                self.player1.learn(state, action, reward, next_state, done)
            
            # Updating the state space
            state = next_state

            # Rendering accordingly
            if not self.headless:
                self.render()

        # Outputting message as necessary
        if not self.headless:
            if self.winner is None:
                print("It's a draw.")
            else:
                print(f"Congratulations! Player {self.winner} is the winner!")


def main():
    parser = argparse.ArgumentParser(description='Connect4 Game')

    # Choosing whether to play or train
    parser.add_argument('--mode', type=str, default='play', choices=['play', 'train'],
                        help='Mode to run the game: "play" for playing mode, "train" for training mode.')
    
    # Choosing players' information
    parser.add_argument('--player1', type=str, default='human', choices=['human', 'random', 'heuristic', 'ql', 'dql'],
                        help='Choose who is playing as the first player: "human", "random", "heuristic", "ql", or "dql".')
    parser.add_argument('--player2', type=str, default='random', choices=['human', 'random', 'heuristic', 'ql', 'dql'],
                        help='Choose who is playing as the second player: "human", "random", "heuristic", "ql" or "dql".')
    parser.add_argument('--p1_symbol', type=str, default='o',
                        help='Choose your symbol: "o", "x", or another character.')
    parser.add_argument('--p2_symbol', type=str, default='x',
                        help='Choose your symbol: "o", "x", or another character.')
    
    # Choosing starting conditions
    parser.add_argument('--start', type=str, default='player1', choices=['player1', 'player2'],
                        help='Choose who starts first: "player1" or "player2".')
    parser.add_argument('--headless', action='store_true',
                        help='Run the game in headless mode (no console output). Useful for training mode.')

    # ------- Validation -------

    # Display help message if no arguments given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    # Checking that the symbols are single characters and not the same
    if len(args.p1_symbol) != 1 or len(args.p2_symbol) != 1:
        print("ERROR: Please only use single characters for the p1_symbol and p2_symbol.")
        sys.exit()
    elif args.p1_symbol == args.p2_symbol:
        print("ERROR: p1_symbol cannot equal p2_symbol.")
        sys.exit()

    # Ensuring that training is only done on a RL model
    rl_models = ['ql', 'dql']
    if args.mode == 'train' and args.player1 not in rl_models and args.player2 not in rl_models:
        print('ERROR: Training is only available if a RL model (i.e. "ql" or "dql") is selected.')
        sys.exit()

    # -------------------------

    # Init with given args
    game = Connect4(mode=args.mode, player1=args.player1, player2=args.player2, player1_symbol=args.p1_symbol, 
                    player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless)

    if args.mode == 'play':
        game.play_game()
    elif args.mode == 'train':
        for _ in range(1000):
            game.play_game()

if __name__ == '__main__':
    main()
