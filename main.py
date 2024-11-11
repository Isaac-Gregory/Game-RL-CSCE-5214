import argparse
import sys
from game import Connect4
import agent
from stable_baselines3.common.env_checker import check_env


def main():
    parser = argparse.ArgumentParser(description='Connect4 Game')

    # Choosing whether to play or train
    parser.add_argument('--mode', type=str, default='play', choices=['play', 'train'],
                        help='Mode to run the game: "play" for playing mode, "train" for training mode.')

    # Choosing players' information
    parser.add_argument('--player1', type=str, default='human', choices=['human', 'random', 'heuristic', 'ql', 'dql'],
                        help='Choose who is playing as the first player: "human", "random", "heuristic", "ql", or "dql".')
    parser.add_argument('--player2', type=str, default='random', choices=['human', 'random', 'heuristic', 'ql', 'dql'],
                        help='Choose who is playing as the second player: "human", "random", "heuristic", "ql" or "dql".')
    parser.add_argument('--p1_symbol', type=str, default='o',
                        help='Choose your symbol: "o", "x", or another character.')
    parser.add_argument('--p2_symbol', type=str, default='x',
                        help='Choose your symbol: "o", "x", or another character.')

    # Choosing starting conditions
    parser.add_argument('--start', type=str, default='player1', choices=['player1', 'player2'],
                        help='Choose who starts first: "player1" or "player2".')
    parser.add_argument('--headless', action='store_true',
                        help='Run the game in headless mode (no console output). Useful for training mode.')

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

    # Ensuring that training is only done on a RL model
    rl_models = ['ql', 'dql']
    if args.mode == 'train' and args.player1 not in rl_models and args.player2 not in rl_models:
        print('ERROR: Training is only available if a RL model (i.e. "ql" or "dql") is selected.')
        sys.exit()

    # -------------------------

    # Init with given args
    game = Connect4(mode=args.mode, player1=args.player1, player2=args.player2, player1_symbol=args.p1_symbol,
                    player2_symbol=args.p2_symbol, starting_player=args.start, headless=args.headless)

    # Running play mode or training mode
    if args.mode == 'play':
        game.play_game()
    elif args.mode == 'train':
        if isinstance(game.player1, agent.RLAgent):
            game.player1.learn(total_timesteps=10000)
        elif isinstance(game.player2, agent.RLAgent):
            game.player2.learn(total_timesteps=10000)
        else:
            for _ in range(1):
                game.train_game()


if __name__ == '__main__':
    # env = Connect4()
    # check_env(env, warn=True)
    main()
