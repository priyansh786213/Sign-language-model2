import os
import logging
import cv2
import numpy as np
import base64
from flask import Flask, render_template, Response, request, jsonify
from sign_language_model import SignLanguageModel

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(_name_)

# Initialize Flask app
app = Flask(_name_)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the sign language model
sign_model = SignLanguageModel()

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    Process the image frame sent from the client.
    Identify the sign language gesture and return the text.
    """
    try:
        # Get the image data from the request
        image_data = request.json.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image data received'}), 400
        
        # Remove the data URL prefix
        image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Process the frame with the sign language model
        result, confidence, processed_image_base64 = sign_model.process_frame(frame)
        
        return jsonify({
            'text': result,
            'confidence': confidence,
            'processed_image': processed_image_base64
        })
        
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Internal server error"), 500
