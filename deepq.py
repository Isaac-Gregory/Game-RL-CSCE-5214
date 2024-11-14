import game

def creates_sequence(self, col, row, symbol, length):
    """Check if the move creates a sequence of given length"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # vertical, horizontal, diagonals
    
    for dx, dy in directions:
        count = 1  # Count the current piece
        
        # Check forward direction
        for i in range(1, length):
            new_col = col + (dx * i)
            new_row = row + (dy * i)
            if (0 <= new_col < 7 and 0 <= new_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == symbol):
                count += 1
            else:
                break
                
        # Check backward direction
        for i in range(1, length):
            new_col = col - (dx * i)
            new_row = row - (dy * i)
            if (0 <= new_col < 7 and 0 <= new_row < 6 and 
                self.board.game_board[new_col][new_row].get_status() == symbol):
                count += 1
            else:
                break
                
        if count >= length:
            return True
    return False

def opponent_can_create_sequence(self, opponent_symbol, length):
    """Check if opponent can create a sequence of given length in their next move"""
    for col in self.get_valid_actions():
        row = self.board.available_slot_in_col(col)
        if row is not None:
            # Temporarily place opponent's piece
            self.board.game_board[col][row].update_status(opponent_symbol)
            
            # Check if this creates a sequence
            has_sequence = creates_sequence(self, col, row, opponent_symbol, length)
            
            # Remove the temporary piece
            self.board.game_board[col][row].update_status(' ')
            
            if has_sequence:
                return True
    return False

def calculate_reward(self, action, row, agent_symbol, opponent_symbol):
    base_reward = 0
    
    # Reward for potential winning sequences
    for length in [2, 3]:
        if creates_sequence(self, action, row, agent_symbol, length):
            base_reward += 0.1 * length  # 0.2 for 2-in-a-row, 0.3 for 3-in-a-row
    
    # Penalty for allowing opponent sequences
    for length in [2, 3]:
        if opponent_can_create_sequence(self, opponent_symbol, length):
            base_reward -= 0.2 * length  # -0.3 for 2-in-a-row, -0.45 for 3-in-a-row
    
    # Position-based rewards
    if row == 0:  # Bottom row plays are generally good
        base_reward += 0.1
    if action == 3:  # Center column control is important
        base_reward += 0.05
        
    # Additional strategic rewards
    if blocks_immediate_win(self, action, row, opponent_symbol):
        base_reward += 1.5  # Big reward for blocking opponent's winning move
        
    if creates_fork(self, action, row, agent_symbol):
        base_reward += 0.8  # Reward for creating multiple winning threats
        
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
        if creates_sequence(self, col, row, symbol, 3):
            winning_threats += 1
            if winning_threats >= 2:
                return True
    
    return False

def DQNStep(self, action):
    if self.game_over:
        state = self.get_state()
        return state, 0, True, False, {}

    # Invalid action handling with increased penalty
    if action not in self.get_valid_actions():
        return self.get_state(), -1, False, False, {}

    # Agent's turn
    available_row = self.board.available_slot_in_col(action)
    self.board.game_board[action][available_row].update_status(self.agent_symbol)
    
    # Calculate intermediate reward using our new reward function
    intermediate_reward = calculate_reward(
        self, 
        action, 
        available_row,
        self.agent_symbol,
        self.opponent_symbol
    )

    # Check for agent win
    if self.check_win((action, available_row), self.agent_symbol):
        self.winner = self.agent_symbol
        self.game_over = True
        return self.get_state(), 3.0 + intermediate_reward, True, False, {}
    
    # Check for draw
    if self.board.is_full():
        self.game_over = True
        return self.get_state(), intermediate_reward, True, False, {}

    # Opponent's turn
    opponent_action = self.opponent.next_move(self.get_valid_actions(), self.get_state())
    opponent_row = self.board.available_slot_in_col(opponent_action)
    self.board.game_board[opponent_action][opponent_row].update_status(self.opponent_symbol)

    # Check for opponent win
    if self.check_win((opponent_action, opponent_row), self.opponent_symbol):
        self.winner = self.opponent_symbol
        self.game_over = True
        # Bigger penalty for losing after making a move that got a good intermediate reward
        return self.get_state(), -5.0 + (intermediate_reward * 0.5), True, False, {}
    
    # Check for draw after opponent's move
    if self.board.is_full():
        self.game_over = True
        return self.get_state(), intermediate_reward, True, False, {}

    # Game continues - return intermediate reward
    return self.get_state(), intermediate_reward, False, False, {}