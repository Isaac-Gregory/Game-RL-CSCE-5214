import game

def creates_sequence(self, col, row, symbol, length, spaces_allowed=0) -> tuple[bool, str]:
    """Check if the move creates a sequence of given length"""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # vertical, horizontal, diagonals
    directions_str = ['v','h','du','dd']
    reach = length + spaces_allowed
    
    # Checking in each direction
    for j, (dx, dy) in enumerate(directions):
        count = 1  # Counting the current piece

        # Checking forwards and backwards
        for multiplier in [1, -1]:
            spaces_used = 0
            
            for i in range(1, reach):
                # Calculating new position to check
                new_col = col + ((dx * i)*multiplier)
                new_row = row + ((dy * i)*multiplier)

                # Ensuring position is in range
                if 0 <= new_col < 7 and 0 <= new_row < 6:
                    status = self.board.game_board[new_col][new_row].get_status()
                    if status == symbol:
                        count += 1
                    elif status == ' ' and spaces_used < spaces_allowed:
                        spaces_used += 1 # Allowing a single space
                    else:
                        break
                # Out of range, means that it went too far
                else:
                    break
                    
            if count >= length:
                return (True, directions_str[j])
        
    return (False, None)


def opponent_can_create_sequence(self, opponent_symbol, length, spaces_allowed=0):
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
    return -0.5
    
    # Major rewards/penalties for game-ending states
    four_connection, four_dir = creates_sequence(self, action, row, agent_symbol, 4)
    if four_connection:  # Agent wins
        if four_dir in 'v':
            return 5.0
        else:
            return 15.0
    
    # Check if this move blocked an immediate opponent win
    if blocks_immediate_win(self, action, row, opponent_symbol):
        base_reward += 3.0  # Significant reward for preventing loss
    
    # Reward for creating winning opportunities
    three_connection, three_dir = creates_sequence(self, action, row, agent_symbol, 3, 1)
    two_connection, two_dir = creates_sequence(self, action, row, agent_symbol, 2)
    if three_connection:
        if three_dir == 'v':
            base_reward += 1.0  # Three in a row is very good
        else:
            base_reward += 3.0  # Three in a row is very good
    elif two_connection:
        base_reward += 0.5  # Two in a row is decent
        
    # Penalty for allowing opponent threats
    opp_three_conn, opp_three_dir = creates_sequence(self, action, row, opponent_symbol, 3, 1)
    opp_two_conn, opp_two_dir = creates_sequence(self, action, row, opponent_symbol, 2)
    if opp_three_conn:
        base_reward -= 3.0  # Heavily penalize allowing three in a row
    elif opp_two_conn:
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

# Training step where the agent has the first move
def dqn_step_agent_opp(self, action):
    # Ensuring the game didn't already end
    if self.game_over:
        return get_step_info(self, 0, action, None, True)

    # Agent moves before opponent
    agent_reward, curr_action, curr_row = agent_step(self, action)
    self.render()

    # Checking if game ended after agent move
    if self.game_over:
        return get_step_info(self, agent_reward, curr_action, curr_row)
    
    # Opponent move
    opp_reward, curr_action, curr_row = opponent_step(self)
    self.render()

    # Game continues
    return get_step_info(self, agent_reward + opp_reward, curr_action, curr_row)

# Training step where the opponent has the first move
def dqn_step_opp_agent(self, action):
    # Ensuring the game didn't already end
    if self.game_over:
        return get_step_info(self, 0, action, None, True)

    # Opponent moves before agent
    opp_reward, curr_action, curr_row = opponent_step(self)
    self.render()

    # Checking if game ended after agent move
    if self.game_over:
        return get_step_info(self, opp_reward, curr_action, curr_row)
    
    # Agent moves
    agent_reward, curr_action, curr_row = agent_step(self, action)
    self.render()

    # Game continues
    return get_step_info(self, agent_reward + opp_reward, curr_action, curr_row)

def agent_step(self, action) -> float:
    self.current_player = self.agent_symbol

    # Heavily penalize invalid moves
    if action not in self.get_valid_actions():
        return (-10, action, None)

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
        reward += 10.0
    
    # Check for draw
    if self.board.is_full():
        self.game_over = True
        reward = 0
    
    return (reward, action, available_row)

def opponent_step(self):
    self.current_player = self.opponent_symbol
    reward = 0

    # Opponent's turn
    opponent_action = self.opponent.next_move(self.get_valid_actions(), self.get_state())
    opponent_row = self.board.available_slot_in_col(opponent_action)
    self.board.game_board[opponent_action][opponent_row].update_status(self.opponent_symbol)
    
    # Check for opponent win
    if self.check_win((opponent_action, opponent_row), self.opponent_symbol):
        self.winner = self.opponent_symbol
        self.game_over = True
        reward = -20.0
    
    # Check for draw
    if self.board.is_full():
        self.game_over = True
        reward = 0
    
    return (reward, opponent_action, opponent_row)

def get_step_info(self, reward, action, row, override=False):
    # Getting win direction
    if action is not None and row is not None:
        four_connection, four_dir = creates_sequence(self, action, row, self.agent_symbol, 4)
        if not four_connection:
            four_connection, four_dir = creates_sequence(self, action, row, self.opponent_symbol, 4)
    else:
        four_connection = True
        four_dir = None
    
    # Validating win
    if four_connection is False and self.winner is not None:
        status = self.board.game_board[action][row].get_status()
        print("ERROR: Win detected, but four connected pieces not found.", four_connection, self.winner, status)

    # Getting the agent's player number
    player_num = '1' if self.training_agent_is_p1 else '2'

    # Getting whether the agent was the winner
    agent_win = True if self.winner == self.agent_symbol else False

    # Getting whether it was a tie
    tie = True if self.winner == None else False

    # Adding info to a dictionary
    info = {'agent_player_num': player_num, 'agent_win': agent_win, 'tie': tie, 'win_dir': four_dir}

    # Override used to ensure the game hits the end state
    if override:
        return self.get_state(self.agent_symbol), reward, True, False, info
    
    # Otherwise return like normal
    return self.get_state(self.agent_symbol), reward, self.game_over, False, info