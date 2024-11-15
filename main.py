import argparse
import sys
from stable_baselines3 import DQN  # Import DQN algorithm
from game import Connect4
# from stable_baselines3.common.env_checker import check_env

def main():
    parser = argparse.ArgumentParser(description='Connect4 Game')

    # Choosing whether to play or train
    parser.add_argument('--mode', type=str, default='play', choices=['play', 'train'],
                        help='Mode to run the game: "play" for playing mode, "train" for training mode.')
    
    # Traning conditions
    parser.add_argument('--save_rate', type=int, default=1000,
                        help='Give a number representing the amount of games to run in between saving the models (i.e. a model will be saved ever __ iteration).')
    parser.add_argument('--headless', action='store_true',
                        help='Run the game in headless mode (no console output). Useful for training mode.')
    parser.add_argument('--episodes', type=int, default=10_000,
                        help='Give a number representing the number of games during training.')
    
    # Choosing players' information
    parser.add_argument('--player1', type=str, default='human',
                        help='Choose who is playing as the first player: "human", "random", "heuristic", "dql", or the model file.')
    parser.add_argument('--player2', type=str, default='random',
                        help='Choose who is playing as the second player: "human", "random", "heuristic", "dql", or the model file.')
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

    # If training Deep Q-Learning Agent
    if args.mode == 'train' and (args.player1 == 'dql' or args.player2 == 'dql'):
        # Initialize environment
        env = Connect4(mode='train', player1=args.player1, player2=args.player2, player1_symbol=args.p1_symbol,
                       player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless)
        # Create the DQN agent, good parameters
        model = DQN(
            'MlpPolicy', 
            env, 
            learning_rate=0.0001,
            buffer_size=100000,
            learning_starts=1000,
            batch_size=64,
            gamma=0.99,
            verbose=1
        )
        # Train the agent
        model.learn(total_timesteps=500000)
        # Save the agent
        model.save('dql-model.zip')
    else:
        # Init with given args
        game = Connect4(mode=args.mode, player1=args.player1, player2=args.player2, player1_symbol=args.p1_symbol,
                        player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless, episodes=args.episodes, 
                    save_rate=args.save_rate)

        # Running play mode or training mode
        if args.mode == 'play':
            game.play_game()
        elif args.mode == 'train':
            game.train_game(args.episodes)

if __name__ == '__main__':
    # env = Connect4()
    # check_env(env, warn=True)
    main()
