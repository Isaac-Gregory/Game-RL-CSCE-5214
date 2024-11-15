# Connect4 Reinforcement Learning

This project implements a Connect4 game environment and trains various agents (including Deep Q-Learning) to play the game optimally.

## Project Overview

The project includes:
- A Connect4 game environment compatible with OpenAI Gymnasium
- Multiple AI agents:
  - Random Agent
  - Deep Q-Learning Agents
- Support for human players
- Training and evaluation modes

## Prerequisites

- Python 3.6 to Python 3.11
- Virtual environment (recommended)

## Installation

1. Clone the repository:

`git clone https://github.com/Isaac-Gregory/Game-RL-CSCE-5214.git`
`cd Game-RL-CSCE-5214`


2. Create and activate a virtual environment:

On Windows:

`python -m venv venv`
`venv\Scripts\activate`


On Unix or MacOS:

`python -m venv venv`
`source venv/bin/activate`


`pip install numpy gymnasium stable-baselines3 pickle-mixin`


## Usage

The project supports different modes and player configurations.

### Playing the Game

#### Random Agent
To play against a random agent a user just needs to enter the following command into the command line:

`python main.py --mode play --player1 random --player2 human`

#### DQN Agents
To play against either of the DQN models, the user needs to enter in either of the following.


Stable Baselines3 Model (run after there is a trained model):

`python main.py --mode play --player1 dqlsb --player2 human`


GitHub-based Model (where `models/p1_dql_100000.weights.h5` is the name of one of the trained models' files):

`python main.py --mode play --player1 models/p1_dql_100000.weights.h5  --player2 human`

### Training an Agent

To train a Deep Q-Learning agent, either of the following can be used.

#### Stable Baselines3 (runs model against random agent):

`python main.py --mode train --player1 dqlsb --player2 random --headless`

#### GitHub Implementation (attempts to run model against model):

`python main.py --mode train --player1 dql --player2 dql --headless --episodes 1000 --save_rate 100`

### Command Line Arguments

- `--mode`: Choose between 'play' or 'train'
- `--player1`: Type of first player ('human', 'random', 'ql', 'dql')
- `--player2`: Type of second player ('human', 'random', 'ql', 'dql')
- `--p1_symbol`: Symbol for player 1 (default: 'o')
- `--p2_symbol`: Symbol for player 2 (default: 'x')
- `--start`: Who starts first ('player1' or 'player2')
- `--headless`: Run without console output (useful for training)

Currently only for the GitHub Implementation:
- `--episodes`: Number of games to run during training (For instance, 10,000)
- `--save_rate`: Number representing how often a model will be saved (For instance, 1,000)

## Project Structure

- `main.py`: Entry point and argument parsing
- `game.py`: Connect4 game environment and logic
- `agent.py`: Implementation of different AI agents
- `deepq.py`: Deep Q-Learning specific functions
- `ddqn.py`: GitHub implementation of Deep Q-Learning

## Training Output

Saving:
- The Stable Baselines3 DQN models are saved as `.zip` files in the main directory
- The GitHub-based models are saved as `.weights.h5` files and stored in the `models/` directory

## Notes

- Training can take a while depending on the number of episodes
- Pre-trained models can be loaded for immediate play
- Link to DQN from GitHub: https://github.com/keon/deep-q-learning/blob/master/ddqn.py 
