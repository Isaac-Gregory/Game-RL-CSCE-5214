import game
from stable_baselines3.common.callbacks import BaseCallback

def output_stats(wins, losses, ties, num_total_plays, num_games, title):
    width = 40

    win_ratio = f'\tWin Ratio: \t | {wins/num_games}'
    loss_ratio = f'\tLoss Ratio: \t | {losses/num_games}'
    tie_ratio = f'\tTie Ratio: \t | {ties/num_games}'
    avg_plays = f'\tAvg Moves: \t | {num_total_plays/num_games}'

    final_str = ("-"*width + '\n' + 
                f'| {title:<{width-4}} |\n' + 
                f"| {win_ratio:<{width-13}} |\n" +
                f"| {loss_ratio:<{width-12}} |\n" +
                f"| {tie_ratio:<{width-13}} |\n" +
                f"| {avg_plays:<{width-13}} |\n" +
                "-"*width)

    print(final_str)

def get_game_stats(self, num_games):
    wins = 0
    losses = 0
    ties = 0
    num_total_moves = 0

    for i in range(num_games):
        num_total_moves += self.play_game()

        if self.winner is None:
            ties += 1
        elif self.winner == self.agent_symbol:
            wins += 1
        else:
            losses += 1

    output_stats(wins, losses, ties, num_total_moves, num_games, "Model vs. Model Evaluation")

class StatTracker(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        # Tracking total win/losses/ties
        self.num_agent_wins = 0
        self.num_opponent_wins = 0
        self.num_ties = 0

        # Tracking direction of win
        self.num_agent_v_wins = 0
        self.num_agent_h_wins = 0
        self.num_agent_du_wins = 0
        self.num_agent_dd_wins = 0

        # Tracking opponent's direction for wins
        self.num_opponent_v_wins = 0
        self.num_opponent_h_wins = 0
        self.num_opponent_du_wins = 0
        self.num_opponent_dd_wins = 0

        # Wins as p1 vs p2
        self.num_agent_p1_wins = 0
        self.num_agent_p2_wins = 0
        self.num_opponent_p1_wins = 0
        self.num_opponent_p2_wins = 0

    def _on_step(self) -> bool:
        # Accessing step information
        dones = self.locals['dones']
        infos = self.locals['infos']

        # info = {'agent_player_num': player_num, 'agent_win': agent_win, 'tie': tie, 'win_dir': four_dir}

        for i, done in enumerate(dones):
            if done:
                info = infos[i]
                # Check for agent win
                if info['agent_win']:
                    self.num_agent_wins += 1

                    # Check for player 1 vs 2 win
                    if info['agent_player_num'] == '1':
                        self.num_agent_p1_wins += 1
                    else:
                        self.num_agent_p2_wins += 1

                    # Check for vertical win
                    if info['win_dir'] == 'v':
                        self.num_agent_v_wins += 1

                    # Check for horizontal win
                    elif info['win_dir'] == 'h':
                        self.num_agent_h_wins += 1

                    # Check for upward diagonal
                    elif info['win_dir'] == 'du':
                        self.num_agent_du_wins += 1

                    # Check for downward diagonal
                    elif info['win_dir'] == 'dd':
                        self.num_agent_dd_wins += 1

                # Otherwise, if a tie
                elif info['tie']:
                    self.num_ties += 1

                # Otherwise, opponent win
                else:
                    self.num_opponent_wins += 1

                    # Check for player 1 vs 2 win
                    if info['agent_player_num'] == '1':
                        self.num_opponent_p2_wins += 1
                    else:
                        self.num_opponent_p1_wins += 1

                    # Check for vertical win
                    if info['win_dir'] == 'v':
                        self.num_opponent_v_wins += 1

                    # Check for horizontal win
                    elif info['win_dir'] == 'h':
                        self.num_opponent_h_wins += 1

                    # Check for upward diagonal
                    elif info['win_dir'] == 'du':
                        self.num_opponent_du_wins += 1

                    # Check for downward diagonal
                    elif info['win_dir'] == 'dd':
                        self.num_opponent_dd_wins += 1

        return True
    
    def reset_stats(self):
        # Tracking total win/losses/ties
        self.num_agent_wins = 0
        self.num_opponent_wins = 0
        self.num_ties = 0

        # Tracking direction of win
        self.num_agent_v_wins = 0
        self.num_agent_h_wins = 0
        self.num_agent_du_wins = 0
        self.num_agent_dd_wins = 0

        # Tracking opponent's direction for wins
        self.num_opponent_v_wins = 0
        self.num_opponent_h_wins = 0
        self.num_opponent_du_wins = 0
        self.num_opponent_dd_wins = 0

        # Wins as p1 vs p2
        self.num_agent_p1_wins = 0
        self.num_agent_p2_wins = 0
        self.num_opponent_p1_wins = 0
        self.num_opponent_p2_wins = 0

    def output_info(self):
        width = 40
        final_str = "-"*width + '\n'

        final_str +=    f'\tAgent Wins: \t | {self.num_agent_wins}' + '\n'
        final_str +=    f'\tOpp Wins: \t | {self.num_opponent_wins}' + '\n'
        final_str +=    f'\tTotal Ties: \t | {self.num_ties}' + '\n'
        
        final_str += '\n'

        final_str +=    f'\tA-V Wins: \t | {self.num_agent_v_wins}' + '\n'
        final_str +=    f'\tA-H Wins: \t | {self.num_agent_h_wins}' + '\n'
        final_str +=    f'\tA-DU Wins: \t | {self.num_agent_du_wins}' + '\n'
        final_str +=    f'\tA-DD Wins: \t | {self.num_agent_dd_wins}' + '\n'

        final_str += '\n'

        final_str +=    f'\tO-V Wins: \t | {self.num_opponent_v_wins}' + '\n'
        final_str +=    f'\tO-H Wins: \t | {self.num_opponent_h_wins}' + '\n'
        final_str +=    f'\tO-DU Wins: \t | {self.num_opponent_du_wins}' + '\n'
        final_str +=    f'\tO-DD Wins: \t | {self.num_opponent_dd_wins}' + '\n'
        
        final_str += '\n'

        final_str +=    f'\tA P1 Wins: \t | {self.num_agent_p1_wins}' + '\n'
        final_str +=    f'\tA P2 Wins: \t | {self.num_agent_p2_wins}' + '\n'

        final_str += '\n'

        final_str +=    f'\tO P1 Wins: \t | {self.num_opponent_p1_wins}' + '\n'
        final_str +=    f'\tO P2 Wins: \t | {self.num_opponent_p2_wins}' + '\n'

        final_str += "-"*width

        print(final_str)

        return final_str

    # def _on_rollout_end(self):
    #     self.output_info()