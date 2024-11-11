import random
import pickle
import sys
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
            print(f"Agent '{self.symbol}' chooses column {action + 1}")
        return action


# class HeuristicAgent(Player):
#     def next_move(self, moves, curr_state):


class RLAgent(Player):
    def learn(self, total_timesteps=10000):
        pass


class QLearningAgent(RLAgent):
    def __init__(self, symbol, headless, mode, game):
        super().__init__(symbol, headless)

        if mode == 'play':
            self.agent = PPO.load("test1_100000", env=game)
        else:
            self.agent = PPO("MlpPolicy", game, verbose=5)

    def next_move(self, moves, curr_state):
        action, log_prob = self.agent.predict(curr_state)
        print(action, log_prob)
        return action
    
    def learn(self):
        timesteps = 100000
        self.agent.learn(total_timesteps=timesteps)
        self.agent.save("test1_" + str(timesteps))

class DeepQLearningAgent(RLAgent):
    def __init__(self, symbol, headless, mode, game):
        super().__init__(symbol, headless)
        self.mode = mode
        if mode == 'play':
            self.agent = DQN.load('dql-model.zip', env=game)
        else:
            self.agent = DQN('MlpPolicy', game, verbose=1)

    def next_move(self, moves, curr_state):
        action, _ = self.agent.predict(curr_state)
        if action not in moves:
            action = random.choice(moves)
        return action

    def learn(self, total_timesteps=10000):
        self.agent.learn(total_timesteps=total_timesteps)
        self.agent.save('dql-model.zip')
