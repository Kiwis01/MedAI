from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from api.prediction import pred, draw_box
from api.chat import chat, MedicalExperts
from dotenv import load_dotenv
import cv2

load_dotenv()

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
PREDICTION_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'predictions')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PREDICTION_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PREDICTION_FOLDER'] = PREDICTION_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize medical expert system
medical_expert = MedicalExperts()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file):
    """Helper function to handle file uploads and get predictions"""
    if not file or file.filename == '':
        return None, 'No file selected'
    
    if not allowed_file(file.filename):
        return None, 'Invalid file type'
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    response = pred(filepath)
    print(response.text)
    if isinstance(response, str):
        return None, response

    # Draw bounding box and save as new file
    try:
        image, _ = draw_box(response, filepath)
        bbox_filename = f"bbox_{filename}"
        bbox_filepath = os.path.join(app.config['PREDICTION_FOLDER'], bbox_filename)
        
        # Ensure image is in BGR format for cv2.imwrite
        if len(image.shape) == 3 and image.shape[2] == 3:
            cv2.imwrite(bbox_filepath, image)
        else:
            return None, 'Error processing image: Invalid image format'
        
        # Return both the prediction data and the bbox image path
        return {
            'prediction': response.json(),
            'image_url': f'/static/predictions/{bbox_filename}'
        }, None
        
    except Exception as e:
        return None, f'Error processing image: {str(e)}'

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.dirname(UPLOAD_FOLDER), filename)

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        message = data['message']
        
        # Get prediction from external API if image is present
        prediction = None
        image_url = None
        pred_data = None
        if 'image' in request.files:
            pred_data, error = handle_file_upload(request.files['image'])
            if error:
                return jsonify({'error': error}), 400
            prediction = pred_data['prediction']['predictions'][0]['class']
            image_url = pred_data['image_url']

        # Get the medical specialty
        expert_response = medical_expert.find_expert(message)
        expert_data = expert_response.json()
        study_medicine = expert_data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Get chatbot response with the specialty
        response = chat(message, prediction=prediction, study_medicine=study_medicine)
        response_data = response.json()
        bot_message = response_data["candidates"][0]["content"]["parts"][0]["text"]

        # Return both messages with the predicted image URL for the bot's response
        return jsonify([
            {'content': message, 'is_user': True},
            {
                'content': bot_message, 
                'is_user': False, 
                'image_url': image_url if pred_data else None,
                'analysis': pred_data['prediction'] if pred_data else None
            }
        ])

    except Exception as e:
        print(f"Error in handle_chat: {str(e)}")  
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        pred_data, error = handle_file_upload(request.files['file'])
        if error:
            return jsonify({'error': error}), 400

        return jsonify(pred_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)