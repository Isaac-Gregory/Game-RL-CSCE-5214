# Connect4 Reinforcement Learning

This project implements a Connect4 game environment and trains various AI agents (including Deep Q-Learning) to play the game optimally.

## Project Overview

The project includes:
- A Connect4 game environment compatible with OpenAI Gymnasium
- Multiple AI agents:
  - Random Agent
  - Q-Learning Agent
  - Deep Q-Learning Agent
- Support for human players
- Training and evaluation modes

## Prerequisites

- Python 3.6 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:

git clone https://github.com/Isaac-Gregory/Game-RL-CSCE-5214.git
cd Game-RL-CSCE-5214


2. Create and activate a virtual environment:

On Windows:

python -m venv venv
venv\Scripts\activate


On Unix or MacOS:

python -m venv venv
source venv/bin/activate


pip install numpy gymnasium stable-baselines3 pickle-mixin


## Usage

The project supports different modes and player configurations.

### Playing the Game

To play against a random agent:

python main.py --mode play --player1 human --player2 random


To play against a trained DQL agent:

(Ran after you train the model)

python main.py --mode play --player1 human --player2 dql


### Training an Agent

To train a Deep Q-Learning agent:

python main.py --mode train --player1 dql --player2 random --headless


### Command Line Arguments

- `--mode`: Choose between 'play' or 'train'
- `--player1`: Type of first player ('human', 'random', 'ql', 'dql')
- `--player2`: Type of second player ('human', 'random', 'ql', 'dql')
- `--p1_symbol`: Symbol for player 1 (default: 'o')
- `--p2_symbol`: Symbol for player 2 (default: 'x')
- `--start`: Who starts first ('player1' or 'player2')
- `--headless`: Run without console output (useful for training)

## Project Structure

- `main.py`: Entry point and argument parsing
- `game.py`: Connect4 game environment and logic
- `agent.py`: Implementation of different AI agents
- `deepq.py`: Deep Q-Learning specific functions

## Training Output

Saving:
- Q-tables are saved as pickle files in the `models/` directory
- DQL models are saved as `.zip` files

## Notes

- The Deep Q-Learning agent uses the Stable-Baselines3 implementation
- Training can take a while depending on the number of episodes
- Pre-trained models can be loaded for immediate play