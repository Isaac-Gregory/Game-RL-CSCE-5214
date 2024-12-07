import tkinter as tk
from tkinter import messagebox
from game import Connect4

class Connect4Options(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4 Options")
        self.geometry("500x300")
        self.create_widgets()

        self.player_option = '1'
        self.opponent_option = 'random'

    def create_widgets(self):
        self.board_frame = tk.Frame(self, width=500, height=300, bg="lightgray")
        self.board_frame.pack_propagate(False)
        self.board_frame.pack(padx=10, pady=10)

        # Storing the selected value
        var_left = tk.StringVar()

        # Creating buttons for finding the player 
        self.radio1 = tk.Radiobutton(self.board_frame, text="Player 1", variable=var_left, value="1", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_left: self.on_select(var_left))
        self.radio2 = tk.Radiobutton(self.board_frame, text="Player 2", variable=var_left, value="2", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_left: self.on_select(var_left))

        # Using pack to control positioning with side and padding
        # Using grid to control position in rows and columns
        self.radio1.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        self.radio2.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        # Storing the selected value
        var_right = tk.StringVar()

        # Create radio buttons with no indicator, and use background color to indicate selection
        self.radio3 = tk.Radiobutton(self.board_frame, text="Human", variable=var_right, value="3", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))
        self.radio4 = tk.Radiobutton(self.board_frame, text="Random", variable=var_right, value="4", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))
        self.radio5 = tk.Radiobutton(self.board_frame, text="RL Agent", variable=var_right, value="5", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))

        # Using pack to control positioning with side and padding
        # Using grid to control position in rows and columns
        self.radio3.grid(row=0, column=1, padx=10, pady=5, sticky="W")
        self.radio4.grid(row=1, column=1, padx=10, pady=5, sticky="W")
        self.radio5.grid(row=2, column=1, padx=10, pady=5, sticky="W")

        start_button = tk.Button(self.board_frame, text="Start Game", width=20, height=2, font=("Arial", 16), command=self.start_clicked)
        start_button.grid(row=3, column=0, columnspan=2, pady=20)

    def on_select(self, var):
        selected_option = var.get()  # Gets the value of the selected option
        # Update button color based on the selection
        if selected_option == "1":
            self.radio1.config(bg="lightgray")
            self.radio2.config(bg="white")
            self.player_option = '1'
        elif selected_option == "2":
            self.radio1.config(bg="white")
            self.radio2.config(bg="lightgray")
            self.player_option = '2'
        elif selected_option == "3":
            self.radio3.config(bg="lightgray")
            self.radio4.config(bg="white")
            self.radio5.config(bg="white")
            self.opponent_option = 'human'
        elif selected_option == "4":
            self.radio3.config(bg="white")
            self.radio4.config(bg="lightgray")
            self.radio5.config(bg="white")
            self.opponent_option = 'random'
        elif selected_option == "5":
            self.radio3.config(bg="white")
            self.radio4.config(bg="white")
            self.radio5.config(bg="lightgray")
            self.opponent_option = 'models/spaced14.zip'

    def start_clicked(self):
        self.destroy()
        self.quit()


# Integrating the game with Tkinter for deployment
class Connect4App(tk.Tk):
    def __init__(self, game, player_option, agent_needed):
        super().__init__()
        self.game = game
        self.title("Connect 4")
        self.geometry("800x700")
        self.player_option = player_option
        self.agent_needed = agent_needed
        self.create_widgets()
        if self.player_option != '1' and agent_needed:
            self.first_move()
    
    def create_widgets(self):
        self.board_frame = tk.Frame(self)
        self.board_frame.pack()

        make_move = self.human_game if not agent_needed else self.make_move

        # Creating buttons for input to each column
        self.column_buttons = []
        for col in range(7):
            button = tk.Button(self.board_frame, text=f"Col {col+1}", width=7, height=2,
                               command=lambda col=col: make_move(col))
            button.grid(row=0, column=col)
            self.column_buttons.append(button)

        # Displaying the current player
        self.status_label = tk.Label(self, text="Current Player: o", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Creating canvas
        self.canvas = tk.Canvas(self, width=700, height=700)
        self.canvas.pack()

        # Drawing the initial board
        self.draw_board()

    def draw_board(self):
        # Emptying canvas
        self.canvas.delete("all")

        # Looping through each slot in the board
        for row in range(6):
            for col in range(7):
                # Calculating postions
                x = col * 100 + 50
                y = (5 - row) * 100 + 50

                # Creating circles to represent the slots
                self.canvas.create_oval(x-40, y-40, x+40, y+40, outline="black", fill="white", width=2)

                # Updating the circles with colors accordingly
                status = self.game.board.game_board[col][row].get_status()
                if status == 'o':      # 'o' is red
                    self.canvas.create_oval(x-40, y-40, x+40, y+40, outline="black", fill="red", width=2)
                elif status == 'x':    # 'x' is yellow
                    self.canvas.create_oval(x-40, y-40, x+40, y+40, outline="black", fill="yellow", width=2)

    # Similar to the play_game function in game.py
    def make_move(self, action):
        # Get the valid row for the chosen column
        available_row = self.game.board.available_slot_in_col(action)
        if available_row is None:
            messagebox.showerror("Invalid Move", "Column is full!")
            return

        # Make the move for the current player
        self.game.step(action)
        self.draw_board()

        # Check for winner or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Update the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

        # Opponent's turn
        if self.player_option == '1':
            opp_action = self.game.player2.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player2_symbol))
        else:
            opp_action = self.game.player1.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player1_symbol))
        self.game.step(opp_action)

        # Redraw the board
        self.draw_board()

        # Check for winner or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Update the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

    # Similar to the play_game function in game.py
    def first_move(self):

        # Opponent's turn
        opp_action = self.game.player1.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player1_symbol))
        self.game.step(opp_action)

        # Draw the board
        self.draw_board()

        # Check for winner or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Update the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

    def human_game(self, action):
        # Get the valid row for the chosen column
        available_row = self.game.board.available_slot_in_col(action)
        if available_row is None:
            messagebox.showerror("Invalid Move", "Column is full!")
            return

        # Make the move for the current player
        self.game.step(action)
        self.draw_board()

        # Check for winner or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Update the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

    def reset_game(self):
        self.game.reset()
        self.draw_board()
        self.status_label.config(text="Current Player: o")
        if self.player_option != '1' and self.agent_needed: self.first_move()

# Example setup to run the game with Tkinter
if __name__ == "__main__":
    options = Connect4Options()
    options.mainloop()

    player1 = 'human' if options.player_option == '1' else options.opponent_option
    player2 = options.opponent_option if options.player_option == '1' else 'human'

    if player1 == 'human' and player2 == 'human':
        agent_needed = False
    else:
        agent_needed = True

    # Create the Connect 4 game instance
    game = Connect4(mode='play', player1=player1, player2=player2, player1_symbol='o', player2_symbol='x', headless=True)

    # Initialize the Tkinter app with the Connect 4 game instance
    app = Connect4App(game, options.player_option, agent_needed)
    app.mainloop()
