import game

def creates_sequence(self, col, row, symbol, length, spaces_allowed=False) -> tuple[bool, str]:
    """Check if the move creates a sequence of given length"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # vertical, horizontal, diagonals
    directions_str = ['v','h','du','dd']
    
    for j, (dx, dy) in enumerate(directions):
        count = 1  # Count the current piece
        
        # Check forward direction
        for i in range(1, length):
            new_col = col + (dx * i)
            new_row = row + (dy * i)
            next_col = col + (dx * (i+1))
            next_row = row + (dy * (i+1))
            if (0 <= new_col < 7 and 0 <= new_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == symbol):
                count += 1
            elif (spaces_allowed and 0 <= next_col < 7 and 0 <= next_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == ' ' and
                self.board.game_board[next_col][next_row].get_status() == symbol):
                count += 1
                break
            else:
                break
                
        # Check backward direction
        for i in range(1, length):
            new_col = col - (dx * i)
            new_row = row - (dy * i)
            next_col = col - (dx * (i+1))
            next_row = row - (dy * (i+1))
            if (0 <= new_col < 7 and 0 <= new_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == symbol):
                count += 1
            elif (spaces_allowed and 0 <= next_col < 7 and 0 <= next_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == ' ' and
                self.board.game_board[next_col][next_row].get_status() == symbol):
                count += 1
                break
            else:
                break
                
        if count >= length:
            return (True, directions_str[j])
    return (False, directions_str[j])

def opponent_can_create_sequence(self, opponent_symbol, length, spaces_allowed=False):
    """Check if opponent can create a sequence of given length in their next move"""
    for col in self.get_valid_actions():
        row = self.board.available_slot_in_col(col)
        if row is not None:
            # Temporarily place opponent's piece
            self.board.game_board[col][row].update_status(opponent_symbol)
            
            # Check if this creates a sequence
            has_sequence, dir = creates_sequence(self, col, row, opponent_symbol, length, spaces_allowed)
            
            # Remove the temporary piece
            self.board.game_board[col][row].update_status(' ')
            
            if has_sequence:
                return True
    return False

def calculate_reward(self, action, row, agent_symbol, opponent_symbol):
    base_reward = 0
    
    # Major rewards/penalties for game-ending states
    four_connection, four_dir = creates_sequence(self, action, row, agent_symbol, 4)
    if four_connection:  # Agent wins
        print('FOUR CONNECTION: +5 or +25 and ', four_dir)
        if four_dir == 'v':
            return 5.0
        else:
            return 15.0
    
    # Check if this move blocked an immediate opponent win
    if blocks_immediate_win(self, action, row, opponent_symbol):
        print('BLOCK WIN: +3.0')
        base_reward += 3.0  # Significant reward for preventing loss
    
    # Reward for creating winning opportunities
    three_connection, three_dir = creates_sequence(self, action, row, agent_symbol, 3, True)
    two_connection, two_dir = creates_sequence(self, action, row, agent_symbol, 2)
    if three_connection:
        print('THREE CONNECTION: +1 or +3 and ', three_dir)
        if three_dir == 'v':
            base_reward += 1.0  # Three in a row is very good
        else:
            base_reward += 3.0  # Three in a row is very good
    elif two_connection:
        print('TWO CONNECTION: +0.5 and ', two_dir)
        base_reward += 0.5  # Two in a row is decent
        
    # Penalty for allowing opponent threats
    opp_three_conn, opp_three_dir = creates_sequence(self, action, row, opponent_symbol, 3, True)
    opp_two_conn, opp_two_dir = creates_sequence(self, action, row, opponent_symbol, 2)
    if opp_three_conn:
        print('OPPONENT 3-SEQUENCE: -3.0 and ', opp_three_dir)
        base_reward -= 3.0  # Heavily penalize allowing three in a row
    elif opp_two_conn:
        print('OPPONENT 2-SEQUENCE: -0.8 and ', opp_two_dir)
        base_reward -= 0.8  # Penalize allowing two in a row
    
    # # Strategic position rewards
    # if creates_fork(self, action, row, agent_symbol):
    #     base_reward += 3.0  # Multiple winning threats is very good
    
    # Center control is important
    if action == 4:
        base_reward += 0.2
    elif action in [3, 5]:  # Adjacent to center
        base_reward += 0.1
        
    # # Lower rows are generally better
    # row_multiplier = (row + 1) / 6  # 1/6 for bottom row, 1 for top row
    # base_reward *= (2 - row_multiplier)  # Reduces reward for higher plays
    
    return base_reward

def blocks_immediate_win(self, col, row, opponent_symbol):
    """Check if the move blocks an immediate win for the opponent"""
    # Temporarily remove our piece
    self.board.game_board[col][row].update_status(' ')
    
    # Check if opponent would win by playing here
    self.board.game_board[col][row].update_status(opponent_symbol)
    would_win = self.check_win((col, row), opponent_symbol)
    
    # Restore our piece
    self.board.game_board[col][row].update_status(self.agent_symbol)
    
    return would_win

def creates_fork(self, col, row, symbol):
    """Check if the move creates multiple winning threats"""
    winning_threats = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dx, dy in directions:
        three_connected, three_dir = creates_sequence(self, col, row, symbol, 3)
        if three_connected:
            winning_threats += 1
            if winning_threats >= 2:
                return True
    
    return False

def DQNStep(self, action):
    print(self.get_state())
    if self.game_over:
        print("GAME OVER")
        return self.get_state(), 0, True, False, {}

    # Heavily penalize invalid moves
    if action not in self.get_valid_actions():
        print("INVALID ACTION")
        return self.get_state(), -10, True, False, {}

    # Agent's turn
    available_row = self.board.available_slot_in_col(action)
    self.board.game_board[action][available_row].update_status(self.agent_symbol)
    

    # Check for agent win
    if self.check_win((action, available_row), self.agent_symbol):
        self.winner = self.agent_symbol
        self.game_over = True
        print("AGENT WIN")
        print(self.get_state())
        return self.get_state(), 10.0, True, False, {}
    
    # Check for draw
    if self.board.is_full():
        self.game_over = True
        print("DRAW")
        return self.get_state(), 0, True, False, {}

    # Opponent's turn
    opponent_action = self.opponent.next_move(self.get_valid_actions(), self.get_state())
    opponent_row = self.board.available_slot_in_col(opponent_action)
    self.board.game_board[opponent_action][opponent_row].update_status(self.opponent_symbol)
    
    # Calculate reward for agent's move
    reward = calculate_reward(
        self, 
        action, 
        available_row,
        self.agent_symbol,
        self.opponent_symbol
    )

    # Check for opponent win
    if self.check_win((opponent_action, opponent_row), self.opponent_symbol):
        self.winner = self.opponent_symbol
        self.game_over = True
        print("OPPONENT WIN")
        print(self.get_state())
        return self.get_state(), -20.0, True, False, {}
    
    print('REWARD:', reward)
    # Game continues
    return self.get_state(), reward, False, False, {}