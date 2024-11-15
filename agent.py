import random
import pickle
import sys
import numpy as np
# from stable_baselines3 import PPO
# from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning
# from stable_baselines3.common.logger import configure
# from stable_baselines3 import DQN
from DQN.ddqn import DQNAgent
import tensorflow as tf

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
        self.error()
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
        return
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.num_actions)  # Exploration through randomness
        else:
            return np.argmax(self.q_table[curr_state]) # Exploitation (choosing best action)
        
    # Define function to update Q-values
    def learn(self, state, action, reward, next_state):
        return
        best_next_action = np.argmax(self.q_table[next_state])  # Best action for next state
        td_target = reward + self.gamma * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error

        # # Print the learned Q-table and policy
        # print("Learned Q-table:\n", self.q_table)
        # print("Learned Policy:")
        # for state in range(self.num_states):
        #     print(f"State {state}: Action {np.argmax(self.q_table[state])}")
    
    def error(self):
        print("ERROR: This feature is no longer setup.")
        sys.exit()

# class DeepQLearningAgent(RLAgent):
#     def __init__(self, symbol, headless, mode, game, gamma=0.9, alpha=0.1, epsilon=0.2):
#         super().__init__(symbol, headless)

#         if mode == 'play':
#             with open('dql-model.pkl', 'r') as f:
#                 self.agent = pickle.load(f)
#         else:
#             print(game.action_space.n)
#             self.agent = DQNAgent(input_dims=game.observation_space.shape, n_actions=game.action_space.n, lr=0.001, gamma=0.99, epsilon=1.0, 
#                                   eps_dec=0.995, eps_min=0.01, mem_size=1000000, batch_size=64)
        

#     # Define function to choose an action using epsilon-greedy policy
#     def next_move(self, moves, curr_state):
#         state = self.agent.preprocess_board(curr_state)
#         return self.agent.choose_action(state)
        
#     # Define function to update Q-values
#     def learn(self, episode, prev_state, action, reward, next_state, done=False, info=[{}]):
#         prev_state = self.agent.preprocess_board(prev_state)
#         next_state = self.agent.preprocess_board(next_state)
#         self.agent.store_transition(state=prev_state, action=action, reward=reward, state_=next_state, done=done)
#         self.agent.learn()

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
        # batch_size = 32
        self.agent.memorize(np.reshape(prev_state, [1, 42]), action, reward, np.reshape(next_state, [1, 42]), done)
        # if len(self.agent.memory) > batch_size:
        #     self.agent.replay(batch_size)

    