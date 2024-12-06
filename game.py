import numpy as np
import agent
import gymnasium as gym
from gymnasium import spaces
import time
import deepq
import os
from random import choice

# Constants/rewards for reinforcement training
LOSING_RW = -10
WINNING_RW = 10
TIE_RW = 0
MOVE_RW = -0.1

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
class Connect4(gym.Env):

    def __init__(self, mode='play', player1='human', player2='random', player1_symbol='o', player2_symbol='x', 
                starting_player='player1', headless=False, episodes=10_000, save_rate=1000):
        # Setting up gym environment
        super().__init__()
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(6, 7), dtype=int)
        
        # Setting game information
        self.player1_symbol = player1_symbol            # Sets the first player's symbol
        self.player2_symbol = player2_symbol            # Sets the second player's symbol
        self.headless = headless                        # Decides whether to print board
        self.board = Board(headless=self.headless)      # Sets up board
        self.winner = None                              # Stores the winning player's symbol for reference
        self.game_over = False                          # Boolean for tracking if the game ended
        self.starting_player = starting_player          # Storing the first player for use in resetting
        self.mode = mode                                # String storing either "play" or "train"
        self.episodes = episodes                        # Number of episodes to run for
        self.save_rate = save_rate                      # Saving rate for the RL models during training
        self.training_agent_is_p1 = False               # Value used for swapping agent between player 1 and 2 during training

        # Sets the starting symbol (Ex. 'o' or 'x')
        self.current_player = self.player1_symbol if starting_player == 'player1' else self.player2_symbol

        # Setting up player 1
        if player1 == 'human':
            self.player1 = agent.HumanPlayer(self.player1_symbol, self.headless)
        elif player1 == 'random':
            self.player1 = agent.RandomAgent(self.player1_symbol, self.headless)
        elif player1 == 'ql':
            self.player1 = agent.QLearningAgent(self.player1_symbol, self.headless, mode=mode, game=self)
        elif player1 == 'dql':
            self.player1 = agent.DeepQLearningAgent(self.player1_symbol, self.headless, mode=mode, game=self)
        elif player1 == 'dqlsb':
            self.player1 = agent.DeepQLearningAgentSB(self.player1_symbol, self.headless, mode=self.mode)
        else: # Model file given
            self.player1 = agent.DeepQLearningAgentSB(self.player1_symbol, self.headless, mode=mode, model=player1)


        # Setting up player 2
        if player2 == 'human':
            self.player2 = agent.HumanPlayer(self.player2_symbol, self.headless)
        elif player2 == 'random':
            self.player2 = agent.RandomAgent(self.player2_symbol, self.headless)
        elif player2 == 'ql':
            self.player2 = agent.QLearningAgent(self.player2_symbol, self.headless, mode=mode, game=self)
        elif player2 == 'dql':
            self.player2 = agent.DeepQLearningAgent(self.player2_symbol, self.headless, mode=mode, game=self)
        elif player2 == 'dqlsb':
            self.player2 = agent.DeepQLearningAgentSB(self.player2_symbol, self.headless, mode=self.mode)
        else: # Model file given
            self.player2 = agent.DeepQLearningAgentSB(self.player2_symbol, self.headless, mode=mode, model=player2)

        # For training with DQN
        if mode == 'train' and (isinstance(self.player1, agent.RLAgent) or isinstance(self.player2, agent.RLAgent)):
            if isinstance(self.player1, agent.RLAgent):
                self.agent_symbol = self.player1_symbol
                self.opponent_symbol = self.player2_symbol
                self.opponent = self.player2
            elif isinstance(self.player2, agent.RLAgent):
                self.agent_symbol = self.player2_symbol
                self.opponent_symbol = self.player1_symbol
                self.opponent = self.player1

    # Resets the game to the initial state.
    def reset(self, seed=None, options=None):
        # Resetting gym
        super().reset(seed=seed, options=options)

        # Resetting board
        self.board.reset_board()
        self.winner = None
        self.game_over = False
        self.current_player = self.player1_symbol if self.starting_player == 'player1' else self.player2_symbol

        # Stochastically choosing if agent is p1 or p2 for training
        if self.mode == 'train':
            self.training_agent_is_p1 = choice([True, False])

        # Returning reset state
        return self.get_state(), {}

    # Executes the given action and updates the game state.
    def step(self, action):

        # Setting training flag to avoid consequtive calling of self.mode == 'train'
        training_mode = True if self.mode == 'train' else False

        # Special function for trying out training deep q
        if training_mode: #and ('dql' in [self.player1, self.player2]):
            if self.training_agent_is_p1:
                return deepq.dqn_step_agent_opp(self, action)
            else:
                return deepq.dqn_step_opp_agent(self, action)

        
        # ------------ Early Ending Conditions ------------

        # Game already ended (training mode)
        if training_mode and self.game_over:
            # Prepare the state and info to return
            state = self.get_state()
            done = True
            info = {'current_player': self.current_player}
            truncated = False # Choosing to not limiting the number of steps

            return state, LOSING_RW, done, truncated, info
        
        # Game ended (not training)
        elif self.game_over:
            raise Exception("Game is over. Please reset the game.")

        # Addressing full columns (training)
        if self.mode == 'train' and action not in self.get_valid_actions():
            # Prepare the state and info to return
            state = self.get_state()
            done = False
            info = {'current_player': self.current_player}
            truncated = False # Choosing to not limiting the number of steps

            return state, MOVE_RW, done, truncated, info
        
        # -------------------------------------------------


        # Get the next available slot in the column
        available_row = self.board.available_slot_in_col(action)

        # Validate the action
        if action < 0 or action >= 7:
            raise ValueError(f"Invalid action. Action must be between 1 and 7. Was given {action}.")
        if available_row is None:
            raise ValueError("Invalid action. Column is full.")

        # Place the current player's piece in the slot
        self.board.game_board[action][available_row].update_status(self.current_player)


        # -------------- Reward Assignments ---------------

        # Check for a win condition
        if self.check_win((action, available_row), self.current_player):
            self.winner = self.current_player
            self.game_over = True
            reward = WINNING_RW

        # Check for a draw (if the board is full)
        elif self.board.is_full():
            self.game_over = True
            reward = TIE_RW

        else:
            # Decling award (want system to minimize movement)
            reward = MOVE_RW

        # -------------------------------------------------


        # Prepare the state and info to return
        state = self.get_state()
        done = self.game_over
        info = {'current_player': self.current_player}
        truncated = False # Choosing to not limiting the number of steps

        # Switch to the other player if the game is not over
        if not self.game_over:
            if self.current_player == self.player1_symbol:
                self.current_player = self.player2_symbol
            elif self.current_player == self.player2_symbol:
                self.current_player = self.player1_symbol

        return state, reward, done, truncated, info

    # Returns the current state of the game as a numpy array.
    def get_state(self, symbol=None):
        # Default symbol
        if symbol is None: symbol = self.player1_symbol

        # Getting state accordingly
        state = np.zeros((6, 7), dtype=int)

        # Looping through entire table
        for col in range(7):
            for row in range(6):

                # Getting current symbol at each location
                status = self.board.game_board[col][row].get_status()

                # Comparing
                if status == symbol:
                    state[5 - row][col] = 1  # Flip row index for standard representation
                elif status == ' ':
                    state[5 - row][col] = 0  # Flip row index for standard representation
                else:
                    state[5 - row][col] = -1
        return state

    # Returns a list of valid actions
    def get_valid_actions(self):
        valid_actions = [col for col in range(7) if self.board.available_slot_in_col(col) is not None]
        return valid_actions

    # Prints the current state of the board to the console or file
    def render(self, file=None):
        if not self.headless:
            if file == None:
                print(self.board)
            else:
                file.write(self.board.__str__())

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
        self.render()

        # Resetting for a new game
        self.reset()

        # Looping through the game
        num_plays = 0
        done = False
        while not done:
            # Tracking plays for stats
            num_plays += 1

            # Getting the next move if playing
            if self.current_player == self.player1_symbol:
                action = self.player1.next_move(self.get_valid_actions(), self.get_state(self.player1_symbol))

                # Making the next move
                next_state, reward, done, truncated, info = self.step(action)

            else:
                action = self.player2.next_move(self.get_valid_actions(), self.get_state(self.player2_symbol))

                # Making the next move
                next_state, reward, done, truncated, info = self.step(action)  

            # Rendering accordingly
            self.render()

        # Outputting message as necessary
        if not self.headless:
            if self.winner is None:
                print("It's a draw.")
            else:
                print(f"Congratulations! Player {self.winner} is the winner!")

        return num_plays

    def train_game(self, episodes=10000):

        # Setting flags for if a player is a RL model
        p1_is_rl = True if isinstance(self.player1, agent.RLAgent) else False
        p2_is_rl = True if isinstance(self.player2, agent.RLAgent) else False
        
        # Tracking the time for output
        start_time = time.time()
        curr_time = time.time()

        # Create models directory if it doesn't exist
        if not os.path.exists('models'):
            os.makedirs('models')

        # Opening the file
        # Redirecting standard output to output.txt for logging
        with open('output.txt', 'a') as _logger:

            # Looping through each episode/game
            for ep in range(1,episodes+1):

                # Outputting current results to console and file
                prev_time = curr_time
                curr_time = time.time()
                update_str = f"Episode: {ep}\tTime Elapsed: {curr_time-start_time:.2f}\tTime of Last Episode: {curr_time-prev_time:.2f}\n"
                print(update_str)
                _logger.write(update_str)

                # Displaying board if necessary
                self.render(_logger)

                # Resetting
                self.reset()
                prev_action = None

                # Running each game
                while not self.game_over:
                    
                    # Getting current state and actions
                    state = self.get_state()
                    actions = self.get_valid_actions()
                    action = -1
                    prev_action = action

                    # Getting the next move if playing
                    if self.current_player == self.player1_symbol:

                        action = self.player1.next_move(actions, state)

                        # Making the next move
                        next_state, reward, done, truncated, info = self.step(action)

                        # Learning from the action (if applicable)
                        if p1_is_rl:
                            self.player1.learn(ep, state, action, reward, next_state, done)

                    else:

                        action = self.player2.next_move(actions, state)

                        # Making the next move
                        next_state, reward, done, truncated, info = self.step(action)

                        # Learning from the action (if applicable)
                        if p2_is_rl:
                            self.player2.learn(ep, state, action, reward, next_state, done)

                    # Rendering accordingly
                    self.render(_logger)

                # If other player won, notify losing RL model
                state = self.get_state()
                if self.current_player == self.player1_symbol and p1_is_rl:
                    self.player1.learn(ep, state, prev_action, LOSING_RW, state, True)
                elif self.current_player == self.player2_symbol and p2_is_rl:
                    self.player2.learn(ep, state, prev_action, LOSING_RW, state, True)

                # Updating the model weights after each game
                batch_size = 32
                if p1_is_rl: 
                    self.player1.agent.update_target_model()
                    if len(self.player1.agent.memory) > batch_size:
                        self.player1.agent.replay(batch_size)
                if p2_is_rl: 
                    self.player2.agent.update_target_model()
                    if len(self.player2.agent.memory) > batch_size:
                        self.player2.agent.replay(batch_size)

                # Rendering accordingly
                self.render(_logger)

                # Outputting message as necessary
                if not self.headless:
                    if self.winner is None:
                        print("It's a draw.")
                    else:
                        print(f"Congratulations! Player {self.winner} is the winner!")

                # Saving models occasionally
                if ep % self.save_rate == 0:
                    if p1_is_rl:
                        self.player1.agent.save("models/p1_dql_" + str(ep) + ".weights.h5")

                    if p2_is_rl:
                        self.player2.agent.save("models/p2_dql_" + str(ep) + ".weights.h5")
    
    def close(self):
        pass