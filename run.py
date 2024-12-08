from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from game import Connect4
from agent import RandomAgent
import eventlet
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

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
    # On initial connect, create a default game
    game = Connect4(mode='play', player1='human', player2='random', headless=True)
    games[request.sid] = game
    # Emit a neutral state
    emit('game_state', {
        'board': game.get_state().tolist(),
        'current_player': None,
        'game_over': game.game_over,
        'winner': game.winner,
        'human_color': None
    })

@socketio.on('make_move')
def handle_move(data):
    player_option = data.get('player_option', '1')
    game = games.get(request.sid)
    if not game:
        emit('error', {'message': 'No game found for this session'})
        return

    # Human move comes from client directly
    state, reward, done, _, info = game.step(data['column'])
    response = {
        'board': state.tolist(),
        'current_player': info['current_player'] if not done else None,
        'game_over': done,
        'winner': game.winner,
        'human_color': getattr(game, 'human_color', None)
    }
    emit('game_state', response)

    print("Finish player move")


    if player_option == '1':
        print("Normal call")
        # If next up is AI and the game isn't over
        if not done and game.current_player == game.player2_symbol and game.player2 is not None:
            print("Human player 1, inside if")
            ai_move = game.player2.next_move(game.get_valid_actions(), game.get_state(game.player2_symbol))
            ai_state, ai_reward, ai_done, _, ai_info = game.step(ai_move)
            ai_response = {
                'board': ai_state.tolist(),
                'current_player': ai_info['current_player'] if not ai_done else None,
                'game_over': ai_done,
                'winner': game.winner,
                'human_color': getattr(game, 'human_color', None)
            }
            emit('game_state', ai_response)
    elif player_option == '2':
        print("Human is player 2")
       # If next up is AI and the game isn't over
        if not done and game.current_player == game.player1_symbol and game.player1 is not None:
            print("Human player 2, inside if")
            ai_move = game.player1.next_move(game.get_valid_actions(), game.get_state(game.player1_symbol))
            ai_state, ai_reward, ai_done, _, ai_info = game.step(ai_move)
            ai_response = {
                'board': ai_state.tolist(),
                'current_player': ai_info['current_player'] if not ai_done else None,
                'game_over': ai_done,
                'winner': game.winner,
                'human_color': getattr(game, 'human_color', None)
            }
            emit('game_state', ai_response)


@socketio.on('new_game')
def handle_new_game(data):
    player_option = data.get('player_option', '1')
    opponent = data.get('opponent', 'human')

    # Determine players based on player_option
    # If player_option == '1', human is player1
    # If player_option == '2', human is player2
    player1 = 'human' if player_option == '1' else opponent
    player2 = opponent if player_option == '1' else 'human'

    game = Connect4(mode='play', 
                    player1=player1, 
                    player2=player2, 
                    player1_symbol='o', 
                    player2_symbol='x', 
                    headless=True)

    # Set human_color only if human vs AI
    if opponent != 'human':
        # Human vs AI scenario
        if player_option == '1':
            game.human_color = 'Red'
        else:
            # player_option == '2'
            game.human_color = 'Yellow'
    else:
        # human vs human scenario
        game.human_color = None

    games[request.sid] = game

    initial_response = {
        'board': game.get_state().tolist(),
        'current_player': 'o' if not game.game_over else None,
        'game_over': game.game_over,
        'winner': game.winner,
        'human_color': game.human_color
    }
    emit('game_state', initial_response)

    # If human is player 2 and opponent is AI, AI should move first
    if player_option == '2' and opponent != 'human':
        # Now player1 is AI
        if hasattr(game.player1, 'next_move'):
            ai_move = game.player1.next_move(game.get_valid_actions(), game.get_state())
            ai_state, ai_reward, ai_done, _, ai_info = game.step(ai_move)
            ai_response = {
                'board': ai_state.tolist(),
                'current_player': ai_info['current_player'] if not ai_done else None,
                'game_over': ai_done,
                'winner': game.winner,
                'human_color': game.human_color
            }
            emit('game_state', ai_response)


if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")
        socketio.run(app, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
