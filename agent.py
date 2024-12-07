import random
import numpy as np
from DQN.ddqn import DQNAgent
from stable_baselines3 import PPO, DQN

# Template class to act as a parent to the different possible agents
class Player():
    def __init__(self, symbol, headless):
        self.symbol = symbol
        self.headless = headless

    def next_move(self, moves, curr_state):
        pass


class HumanPlayer(Player):
    def next_move(self, moves, curr_state):
        # Allows a human player to select a column interactively.
        # Ensures the move is valid before proceeding.
        valid = False
        while not valid:
            try:
                action = int(input(f"Player '{self.symbol}', choose a column (1-7): "))
                action -= 1 # Convert to 0-based index for internal logic.
                if action in moves:
                    valid = True
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please enter an integer between 1 and 7.")
        return action


class RandomAgent(Player):
    def next_move(self, moves, curr_state):
        action = random.choice(moves)
        if not self.headless:
            print(f"Random Agent '{self.symbol}' chooses column {action + 1}")
        return action


# class HeuristicAgent(Player):
#     def next_move(self, moves, curr_state):



class RLAgent(Player):
    def learn(self, state, action1, reward1, next_state1):
        pass

class DeepQLearningAgent(RLAgent):
    def __init__(self, symbol, headless, mode, game, model_file=None):
        super().__init__(symbol, headless)

        self.agent = DQNAgent(42, 7)
        if model_file != None:
            self.agent.load(model_file)

    # Define function to choose an action using epsilon-greedy policy
    def next_move(self, moves, curr_state):
        state = np.reshape(curr_state, [1, 42])
        return self.agent.act(state)
        
    # Define function to update Q-values
    def learn(self, episode, prev_state, action, reward, next_state, done, info=[{}]):
        self.agent.memorize(np.reshape(prev_state, [1, 42]), action, reward, np.reshape(next_state, [1, 42]), done)


class DeepQLearningAgentSB(RLAgent):
    def __init__(self, symbol, headless, mode, model=None):
        super().__init__(symbol, headless)
        self.mode = mode
        if model is not None:
            self.agent = DQN.load(model)
        else:
            print("No previous model found, using random actions")
            self.agent = None

    def next_move(self, moves, curr_state):
        if self.mode == 'train' and not hasattr(self, 'agent'):
            return random.choice(moves)
        action, _ = self.agent.predict(curr_state)
        if action not in moves:
            action = random.choice(moves)
        return action

    def learn(self):
        pass  # Training handled in main.py
