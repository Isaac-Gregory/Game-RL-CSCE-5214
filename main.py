import argparse
import sys
from stable_baselines3 import DQN  # Import DQN algorithm
from game import Connect4
from math import floor
from evaluate import get_game_stats, StatTracker
# from stable_baselines3.common.env_checker import check_env

def main():
    parser = argparse.ArgumentParser(description='Connect4 Game')

    # Choosing whether to play or train
    parser.add_argument('--mode', type=str, default='play', choices=['play', 'train', 'evaluate'],
                        help='Mode to run the game: "play" for playing mode, "train" for training mode.')
    
    # Training conditions
    parser.add_argument('--save_rate', type=int, default=1000,
                        help='Give a number representing the amount of games to run in between saving the models (i.e. a model will be saved ever __ iteration).')
    parser.add_argument('--headless', action='store_true',
                        help='Run the game in headless mode (no console output). Useful for training mode.')
    parser.add_argument('--episodes', type=int, default=10_000,
                        help='Give a number representing the number of games during training.')
    parser.add_argument('--iterative', action='store_true',
                        help='Trains model against newest saved model.')
    
    # Choosing players' information
    parser.add_argument('--player1', type=str, default='human',
                        help='Choose who is playing as the first player: "human", "random", "heuristic", "dql", "dqlsb", or the model file.')
    parser.add_argument('--player2', type=str, default='random',
                        help='Choose who is playing as the second player: "human", "random", "heuristic", "dql", "dqlsb", or the model file.')
    parser.add_argument('--p1_symbol', type=str, default='o',
                        help='Choose your symbol: "o", "x", or another character.')
    parser.add_argument('--p2_symbol', type=str, default='x',
                        help='Choose your symbol: "o", "x", or another character.')
    parser.add_argument('--start', type=str, default='player1', choices=['player1', 'player2'],
                        help='Choose who starts first: "player1" or "player2".')

    # ------- Validation -------

    # Display help message if no arguments given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    if args.mode == 'evaluate':
        args.headless = True

    # Checking that the symbols are single characters and not the same
    if len(args.p1_symbol) != 1 or len(args.p2_symbol) != 1:
        print("ERROR: Please only use single characters for the p1_symbol and p2_symbol.")
        sys.exit()

    elif args.p1_symbol == args.p2_symbol:
        print("ERROR: p1_symbol cannot equal p2_symbol.")
        sys.exit()

    if args.save_rate > args.episodes:
        print("ERROR: Saving rate exceeds the number of training episodes.")
        sys.exit()

    # -------------------------

    # Init with given args
    tracker = StatTracker()
    game = Connect4(mode=args.mode, player1=args.player1, player2=args.player2, player1_symbol=args.p1_symbol,
                    player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless, episodes=args.episodes, 
                    save_rate=args.save_rate)

    # If training Deep Q-Learning Agent
    if args.mode == 'train' and not (args.player1 == 'dql' or args.player2 == 'dql'):
        # Create the DQN agent, good parameters
        model = DQN(
            'MlpPolicy', 
            game, 
            learning_rate=0.001,
            buffer_size=100000,
            learning_starts=1000,
            batch_size=64,
            gamma=0.99,
            verbose=1,
            exploration_fraction=0.5,
        )
        
        for i in range(floor(args.episodes/args.save_rate)):
            # Train the agent
            model.learn(total_timesteps=args.save_rate, callback=tracker)

            # Save the agent
            new_model_str = f'models/new{i+1}-v2.zip'
            model.save(new_model_str)

            # Updating players for iterative strategy
            if args.iterative:
                new_game = Connect4(mode=args.mode, player1=new_model_str, player2=new_model_str, player1_symbol=args.p1_symbol,
                    player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless, episodes=args.episodes, 
                    save_rate=args.save_rate)
                model.set_env(new_game)
        
            output_str = tracker.output_info()
            with open('output.txt', "a") as file:
                file.write(output_str + "\n")
            tracker.reset_stats()

    elif args.mode == 'train' and (args.player1 == 'dql' or args.player2 == 'dql'):
        print("Training for 'dql' is no longer supported.")
        sys.exit()
        game.train_game(args.episodes)

    elif args.mode == 'play':
        # Running play mode
        game.play_game()

    elif args.mode == 'evaluate':
        get_game_stats(game, args.episodes)

if __name__ == '__main__':
    # env = Connect4()
    # check_env(env, warn=True)
    main()
