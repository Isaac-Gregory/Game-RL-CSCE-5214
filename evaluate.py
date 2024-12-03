import game

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

def get_game_stats(self, num_games, agent_symbol):
    wins = 0
    losses = 0
    ties = 0
    num_total_moves = 0

    for i in range(num_games):
        num_total_moves += self.play_game()

        if self.winner is None:
            ties += 1
        elif self.winner == agent_symbol:
            wins += 1
        else:
            losses += 1

    output_stats(wins, losses, ties, num_total_moves, num_games, "Model vs. Model Evaluation")

