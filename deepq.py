import game
def DQNStep(self, action):
    if self.game_over:
        state = self.get_state()
        done = True
        info = {}
        truncated = False
        reward = 0
        return state, reward, done, truncated, info

        # Agent's turn
    if action not in self.get_valid_actions():
        reward = -1  # Penalty for invalid action
        done = False
        state = self.get_state()
        info = {}
        truncated = False
        return state, reward, done, truncated, info

        # Apply agent's action
    available_row = self.board.available_slot_in_col(action)
    self.board.game_board[action][available_row].update_status(self.agent_symbol)

    # Check for win/draw
    if self.check_win((action, available_row), self.agent_symbol):
        self.winner = self.agent_symbol
        self.game_over = True
        reward = 1  # Agent wins
        done = True
        state = self.get_state()
        info = {}
        truncated = False
        return state, reward, done, truncated, info
    elif self.board.is_full():
        self.game_over = True
        reward = 0  # Draw
        done = True
        state = self.get_state()
        info = {}
        truncated = False
        return state, reward, done, truncated, info

    # Opponent's turn
    opponent_action = self.opponent.next_move(self.get_valid_actions(), self.get_state())
    available_row = self.board.available_slot_in_col(opponent_action)
    self.board.game_board[opponent_action][available_row].update_status(self.opponent_symbol)

    # Check for win/draw
    if self.check_win((opponent_action, available_row), self.opponent_symbol):
        self.winner = self.opponent_symbol
        self.game_over = True
        reward = -1  # Agent loses
        done = True
        state = self.get_state()
        info = {}
        truncated = False
        return state, reward, done, truncated, info
    elif self.board.is_full():
        self.game_over = True
        reward = 0  # Draw
        done = True
        state = self.get_state()
        info = {}
        truncated = False
        return state, reward, done, truncated, info

    # Continue game
    reward = 0
    done = False
    state = self.get_state()
    info = {}
    truncated = False
    return state, reward, done, truncated, info