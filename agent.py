import random
import numpy as np
from DQN.ddqn import DQNAgent

# Template class to act as a parent to the different possible agents
class Player():
    def __init__(self, symbol, headless):
        self.symbol = symbol
        self.headless = headless

    def next_move(self, moves, curr_state):
        pass

class HumanPlayer(Player):
    def next_move(self, moves, curr_state):
        valid = False
        while not valid:
            try:
                action = int(input(f"Player '{self.symbol}', choose a column (1-7): "))
                action -= 1
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
            print(f"Agent '{self.symbol}' chooses column {action}")
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

    