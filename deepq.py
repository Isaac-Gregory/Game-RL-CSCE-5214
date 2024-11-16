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
    
    # Major rewards/penalties for game-ending states
    if creates_sequence(self, action, row, agent_symbol, 4):  # Agent wins
        return 10.0
    
    # Check if this move blocked an immediate opponent win
    if blocks_immediate_win(self, action, row, opponent_symbol):
        base_reward += 5.0  # Significant reward for preventing loss
    
    # Reward for creating winning opportunities
    if creates_sequence(self, action, row, agent_symbol, 3):
        base_reward += 2.0  # Three in a row is very good
    elif creates_sequence(self, action, row, agent_symbol, 2):
        base_reward += 0.5  # Two in a row is decent
        
    # Penalty for allowing opponent threats
    if opponent_can_create_sequence(self, opponent_symbol, 3):
        base_reward -= 3.0  # Heavily penalize allowing three in a row
    elif opponent_can_create_sequence(self, opponent_symbol, 2):
        base_reward -= 0.8  # Penalize allowing two in a row
    
    # Strategic position rewards
    if creates_fork(self, action, row, agent_symbol):
        base_reward += 3.0  # Multiple winning threats is very good
    
    # Center control is important
    if action == 3:
        base_reward += 0.3
    elif action in [2, 4]:  # Adjacent to center
        base_reward += 0.2
        
    # Lower rows are generally better
    row_multiplier = (row + 1) / 6  # 1/6 for bottom row, 1 for top row
    base_reward *= (2 - row_multiplier)  # Reduces reward for higher plays
    
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
        return self.get_state(), 0, True, False, {}

    # Heavily penalize invalid moves
    if action not in self.get_valid_actions():
        return self.get_state(), -10, True, False, {}

    # Agent's turn
    available_row = self.board.available_slot_in_col(action)
    self.board.game_board[action][available_row].update_status(self.agent_symbol)
    
    # Calculate reward for agent's move
    reward = calculate_reward(
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
        return self.get_state(), 10.0, True, False, {}
    
    # Check for draw
    if self.board.is_full():
        self.game_over = True
        return self.get_state(), 0, True, False, {}

    # Opponent's turn
    opponent_action = self.opponent.next_move(self.get_valid_actions(), self.get_state())
    opponent_row = self.board.available_slot_in_col(opponent_action)
    self.board.game_board[opponent_action][opponent_row].update_status(self.opponent_symbol)

    # Check for opponent win
    if self.check_win((opponent_action, opponent_row), self.opponent_symbol):
        self.winner = self.opponent_symbol
        self.game_over = True
        return self.get_state(), -10.0, True, False, {}
    
    # Game continues
    return self.get_state(), reward, False, False, {}