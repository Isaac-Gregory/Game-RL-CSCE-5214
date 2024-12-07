from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from game import Connect4
from agent import RandomAgent
import eventlet
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

# Store game instances
games = {}

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {error}")
    return jsonify({"error": str(error)}), 500

@app.route('/')
def index():
    return render_template('game.html')

@socketio.on('connect')
def handle_connect():
    game = Connect4(mode='play', player1='human', player2='random', headless=True)
    games[request.sid] = game
    emit('game_state', {'board': game.get_state().tolist()})

@socketio.on('make_move')
def handle_move(data):
    game = games[request.sid]
    state, reward, done, _, info = game.step(data['column'])
    response = {
        'board': state.tolist(),
        'current_player': info['current_player'],
        'game_over': done,
        'winner': game.winner,
        'human_color': getattr(game, 'human_color', None)
    }
    emit('game_state', response)

    # If AI needs to move immediately
    if not done and hasattr(game.player2, 'next_move'):
        ai_move = game.player2.next_move(game.get_valid_actions(), game.get_state())
        ai_state, ai_reward, ai_done, _, ai_info = game.step(ai_move)
        ai_response = {
            'board': ai_state.tolist(),
            'current_player': ai_info['current_player'],
            'game_over': ai_done,
            'winner': game.winner,
            'human_color': getattr(game, 'human_color', None)
        }
        emit('game_state', ai_response)

@socketio.on('new_game')
def handle_new_game(data):
    player_option = data.get('player_option', '1')
    opponent = data.get('opponent', 'random')

    # Determine players
    player1 = 'human' if player_option == '1' else opponent
    player2 = opponent if player_option == '1' else 'human'
    
    # Create a new game instance
    game = Connect4(mode='play', 
                    player1=player1, 
                    player2=player2, 
                    player1_symbol='o', 
                    player2_symbol='x', 
                    headless=True)
    
    # Store the human color in the game object for easy retrieval
    game.human_color = 'Red' if player_option == '1' else 'Yellow'
    games[request.sid] = game

    # Emit initial empty board state
    initial_response = {
        'board': game.get_state().tolist(),
        'current_player': 'o',   # Red starts
        'game_over': game.game_over,
        'winner': game.winner,
        'human_color': game.human_color
    }
    emit('game_state', initial_response)

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")
        socketio.run(app, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")