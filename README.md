# Connect4 Reinforcement Learning

This project implements a Connect4 game environment and trains various agents (specifically Deep Q-Learning) to play the game optimally.

## Project Overview

The project includes:
- A Connect4 game environment compatible with OpenAI Gymnasium
- Multiple agents:
  - Random Agent
  - Deep Q-Learning Agents
- Support for human players
- Training and evaluation modes
- GUI-based game play
- Website-based game play

## Prerequisites

- Python 3.6 to Python 3.11
- Virtual environment (recommended)
- Libraries mostly avilable in requirements.txt

## Installation

1. Clone the repository:

`git clone https://github.com/Isaac-Gregory/Game-RL-CSCE-5214.git`
`cd Game-RL-CSCE-5214`

<br /> 

2. Create and activate a virtual environment:

On Windows:

`python -m venv venv`
`venv\Scripts\activate`


On Unix or MacOS:

`python -m venv venv`
`source venv/bin/activate`

<br /> 

3. Install libraries through requriements.txt or like the following:

`pip install numpy gymnasium stable-baselines3 pickle-mixin`


## Usage

The project supports different modes, player configurations, and deployments.

### Playing on the Web

The web deployment is currently hosted at the following link. Choose which opponent to play against, click start game, and select which column you want to start with in order to begin: https://connect4-953633624936.us-central1.run.app/

### Playing on the GUI

To setup to use the GUI:
1. Get the code from this repository onto your local system
2. Download the required libraries (see requirements above)
3. Run `python gui.py` in your command line
4. A menu should pop up. Select whether to be player 1 or 2 as well as what opponent you wish to face
5. Click `Start Game`
6. The board should now have appeared! To play, just select one of the column buttons above the board.
7. Have fun!

### Playing on the Command Line

For playing on the command line, what is mainly needed is to get the code from the repository here and call python on `main.py` with the `--mode` set to play. Please see the command line arguments section below for the game configuration options available.

#### Example of playing a Random Agent
To play against a random agent a user just needs to enter the following command into the command line:

`python main.py --mode play --player1 random --player2 human`

#### Example of playing the DQN Agents
To play against either of the DQN models, the user needs to enter in the following.

Stable Baselines3 Model (run after there is a trained model):

`python main.py --mode play --player1 models/spaced14.zip --player2 human`

**~~GitHub-based Model:~~**

~~`python main.py --mode play --player1 models/p1_dql_100000.weights.h5  --player2 human`~~

Note, the GitHub implementation has been deprecated due to lack of results from the method.

<br /> 

### Training an Agent

To train a Deep Q-Learning agent, the following can be used. Note that the command line arguments' values can be changed as needed.

**Stable Baselines3 (runs model against random agent):**

`python main.py --mode train --player1 dqlsb --player2 random --episodes 1000000 --save_rate 100000 --headless --iterative`

<br /> 

**~~GitHub Implementation (attempts to run model against model):~~**

~~`python main.py --mode train --player1 dql --player2 dql --headless --episodes 1000 --save_rate 100`~~

### Command Line Arguments

- `--mode`: Choose between 'play' or 'train'
- `--player1`: Type of first player ('human', 'random', 'ql', 'dql')
- `--player2`: Type of second player ('human', 'random', 'ql', 'dql')
- `--p1_symbol`: Symbol for player 1 (default: 'o')
- `--p2_symbol`: Symbol for player 2 (default: 'x')
- `--start`: Who starts first ('player1' or 'player2')
- `--headless`: Run without console output (useful for training)
- `--episodes`: Number of games to run during training (For instance, 10,000)
- `--save_rate`: Number representing how often a model will be saved (For instance, 1,000)
- `--iterative`: A flag that indicates for the program to update the opposing model in training to the training model's newest saved version. This occurs after each save.

## Project Structure

- `main.py`: Entry point and argument parsing
- `game.py`: Connect4 game environment and logic
- `agent.py`: Implementation of different AI agents
- `deepq.py`: Deep Q-Learning specific functions for Stable Baselines
- `evaluate.py`: Agent vs. Agent comparisions and statistics tracking in training
- `gui.py`: Local deployment code for running a Tkinter GUI
- `run.py`: Web-based deployment code ran through GCP
- `DQN/ddqn.py`: GitHub implementation of Deep Q-Learning (Now deprecated)

## Training Output

Saving:
- The Stable Baselines3 DQN models are saved as `.zip` files and stored in the `models/` directory
- The GitHub-based models are saved as `.weights.h5` files and stored in the `models/` directory

## Notes

- Training can take a while depending on the number of episodes
- Pre-trained models can be loaded for immediate play
- Link to DQN from GitHub: https://github.com/keon/deep-q-learning/blob/master/ddqn.py 
