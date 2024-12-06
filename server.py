from flask import Flask, jsonify
import os
from game import Connect4
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def home():
    return jsonify({"status": "Connect4 Game Server Running"}), 200

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {error}")
    return jsonify({"error": str(error)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")