import random

# Template class to act as a parent to the different possible agents
class Player():
    def __init__(self, symbol, headless):
        self.symbol = symbol
        self.headless = headless

    def next_move(self, moves, curr_state, reward):
        pass

class HumanPlayer(Player):
    def next_move(self, moves, curr_state, reward):
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
    def next_move(self, moves, curr_state, reward):
        action = random.choice(moves)
        if not self.headless:
            print(f"Agent '{self.symbol}' chooses column {action}")
        return action
    
# class HeuristicAgent(Player):
#     def next_move(self, moves, curr_state, reward):
        

# class QLearningAgent(Player):
#     def next_move(self, moves, curr_state, reward):
        

# class DeepQLearningAgent(Player):
#     def next_move(self, moves, curr_state, reward):
        
