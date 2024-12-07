import tkinter as tk
from tkinter import messagebox
from game import Connect4

# First pop-up menu used for selecting options for game play
class Connect4Options(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4 Options")
        self.geometry("500x300")
        self.create_widgets()

        # Setting default values for parameters
        self.player_option = '1'
        self.opponent_option = 'random'

    def create_widgets(self):
        # Creating frame
        self.board_frame = tk.Frame(self, width=500, height=300, bg="lightgray")
        self.board_frame.pack_propagate(False)
        self.board_frame.pack(padx=10, pady=10)

        # Storing the selected value from the left buttons
        var_left = tk.StringVar()

        # Creating buttons for finding the player 
        self.radio1 = tk.Radiobutton(self.board_frame, text="Player 1", variable=var_left, value="1", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_left: self.on_select(var_left))
        self.radio2 = tk.Radiobutton(self.board_frame, text="Player 2", variable=var_left, value="2", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_left: self.on_select(var_left))

        # Setting buttons to the left side of the menu
        self.radio1.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        self.radio2.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        # Storing the selected value from the right buttons
        var_right = tk.StringVar()

        # Creating radio buttons for selecting opponent
        self.radio3 = tk.Radiobutton(self.board_frame, text="Human", variable=var_right, value="3", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))
        self.radio4 = tk.Radiobutton(self.board_frame, text="Random", variable=var_right, value="4", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))
        self.radio5 = tk.Radiobutton(self.board_frame, text="RL Agent", variable=var_right, value="5", indicatoron=False, font=("Arial", 16), width=20, height=2, command=lambda var=var_right: self.on_select(var_right))

        # Setting buttons to the right side of the menu
        self.radio3.grid(row=0, column=1, padx=10, pady=5, sticky="W")
        self.radio4.grid(row=1, column=1, padx=10, pady=5, sticky="W")
        self.radio5.grid(row=2, column=1, padx=10, pady=5, sticky="W")

        # Adding start button for once options are set
        start_button = tk.Button(self.board_frame, text="Start Game", width=20, height=2, font=("Arial", 16), command=self.start_clicked)
        start_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Animates buttons and changes menu options
    def on_select(self, var):
        selected_option = var.get()  # Gets the value of the selected option

        # Updating button color and options
        if selected_option == "1":
            self.radio1.config(bg="lightgray")
            self.radio2.config(bg="white")

            # Updating to be the first player
            self.player_option = '1'

        elif selected_option == "2":
            self.radio1.config(bg="white")
            self.radio2.config(bg="lightgray")

            # Updating to be the second player
            self.player_option = '2'

        elif selected_option == "3":
            self.radio3.config(bg="lightgray")
            self.radio4.config(bg="white")
            self.radio5.config(bg="white")

            # Opponent is human
            self.opponent_option = 'human'

        elif selected_option == "4":
            self.radio3.config(bg="white")
            self.radio4.config(bg="lightgray")
            self.radio5.config(bg="white")

            # Opponent is random agent
            self.opponent_option = 'random'

        elif selected_option == "5":
            self.radio3.config(bg="white")
            self.radio4.config(bg="white")
            self.radio5.config(bg="lightgray")

            # Opponent is an RL model
            self.opponent_option = 'models/spaced14.zip'

    # Stopping current window now that parameters are set
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

        # Parameters for choosing the game play
        self.player_option = player_option
        self.agent_needed = agent_needed

        # Creating the window
        self.create_widgets()

        # Letting opponent move first if necessary
        if self.player_option != '1' and agent_needed:
            self.first_move()
    
    def create_widgets(self):
        # Creating frame
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
        # Getting row and validating action
        available_row = self.game.board.available_slot_in_col(action)
        if available_row is None:
            messagebox.showerror("Invalid Move", "Column is full!")
            return

        # Taking the selected action/move
        self.game.step(action)
        self.draw_board()

        # Check for win or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Updating the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

        # Opponent's turn
        if self.player_option == '1':
            opp_action = self.game.player2.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player2_symbol))
        else:
            opp_action = self.game.player1.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player1_symbol))
        self.game.step(opp_action)

        # Redrawing the board
        self.draw_board()

        # Check for win or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Updating the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

    # Called for when the opponent gets the first move
    def first_move(self):

        # Opponent's turn first
        opp_action = self.game.player1.next_move(self.game.get_valid_actions(), self.game.get_state(self.game.player1_symbol))
        self.game.step(opp_action)

        # Redrawing the board
        self.draw_board()

        # Check for win or tie
        if self.game.game_over:
            if self.game.winner is None:
                messagebox.showinfo("Game Over", "It's a tie!")
            else:
                messagebox.showinfo("Game Over", f"Player {self.game.winner} wins!")
            self.reset_game()
            return
        else:
            # Updating the player turn label
            current_player = self.game.current_player
            self.status_label.config(text=f"Current Player: {current_player}")

    def human_game(self, action):
        # Getting the row
        available_row = self.game.board.available_slot_in_col(action)

        # Validating the action
        if available_row is None:
            messagebox.showerror("Invalid Move", "Column is full!")
            return

        # Choosing the next move
        self.game.step(action)

        # Redrawing the board
        self.draw_board()

        # Check for win or tie
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

    # Set everything back to the starting state
    def reset_game(self):
        self.game.reset()
        self.draw_board()
        self.status_label.config(text="Current Player: o")
        if self.player_option != '1' and self.agent_needed: self.first_move()

# Running Connect 4 using Tkinter
if __name__ == "__main__":
    # Running the options menu
    options = Connect4Options()
    options.mainloop()

    # Setting up players
    player1 = 'human' if options.player_option == '1' else options.opponent_option
    player2 = options.opponent_option if options.player_option == '1' else 'human'

    # Special case for human vs human
    if player1 == 'human' and player2 == 'human':
        agent_needed = False
    else:
        agent_needed = True

    # Creating the Connect 4 game
    game = Connect4(mode='play', player1=player1, player2=player2, player1_symbol='o', player2_symbol='x', headless=True)

    # Initializing the Tkinter app an running it
    app = Connect4App(game, options.player_option, agent_needed)
    app.mainloop()
