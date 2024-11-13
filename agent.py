import random
import pickle
import sys
import numpy as np
from stable_baselines3 import PPO
from pyqlearning.qlearning.greedy_q_learning import QLearning

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

class QLearningAgent(RLAgent):
    def __init__(self, symbol, headless, mode, game, gamma=0.9, alpha=0.1, epsilon=0.2):
        super().__init__(symbol, headless)

        if mode == 'play':
            with open('ql-model.pkl', 'r') as f:
                self.q_table = pickle.load(f)
        else:
            self.num_actions = game.action_space.n
            self.num_states = 10**7
            self.q_table = np.zeros((self.num_actions, self.num_states))
            self.gamma = gamma
            self.alpha = alpha
            self.epsilon = epsilon

    # Define function to choose an action using epsilon-greedy policy
    def next_move(self, moves, curr_state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.num_actions)  # Exploration through randomness
        else:
            return np.argmax(self.q_table[curr_state]) # Exploitation (choosing best action)
        
    # Define function to update Q-values
    def learn(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])  # Best action for next state
        td_target = reward + self.gamma * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error

        # # Print the learned Q-table and policy
        # print("Learned Q-table:\n", self.q_table)
        # print("Learned Policy:")
        # for state in range(self.num_states):
        #     print(f"State {state}: Action {np.argmax(self.q_table[state])}")

# class DeepQLearningAgent(RLAgent):
#     def next_move(self, moves, curr_state):
        
