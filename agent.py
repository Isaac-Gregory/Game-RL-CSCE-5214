import random
import pickle
import sys

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
    def learn(self, state, action, reward, next_state, done):
        pass

class QLearningAgent(RLAgent):
    def __init__(self, symbol, headless, mode):
        super().__init__(symbol, headless)

        if mode == 'play':
            with open('ql-model.pkl', 'r') as f:
                self.agent = pickle.load(f)
        else:
            # self.agent = pyqlearning.QLearningAgent(42, 7)
            print("ERROR: RL Agent not yet implemented!")
            sys.exit()

    def next_move(self, moves, curr_state):
        return self.agent.act(curr_state)
    
    def learn(self, state, action, reward, next_state, done):
        self.agent.learn(state, action, reward, next_state, done)

# class DeepQLearningAgent(RLAgent):
#     def next_move(self, moves, curr_state):
        
