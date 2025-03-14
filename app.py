from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import shutil
from api import pred, draw_box
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
PREDICTIONS_FOLDER = 'static/predict/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PREDICTION_FOLDER'] = PREDICTIONS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_folder():
    upload_path = "./static/uploads"
    predict_path = "./static/predict"
    if os.path.exists(upload_path):
        shutil.rmtree(upload_path)
    os.makedirs(upload_path)

    if os.path.exists(predict_path):
        shutil.rmtree(predict_path)
    os.makedirs(predict_path)


@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run prediction
        prediction = pred(filepath)        
        image, f_name = draw_box(prediction, filepath)
        pred_filepath = os.path.join(app.config['PREDICTION_FOLDER'], f_name)

        # Save or display the image
        cv2.imwrite(pred_filepath, image)  # Saves the image
        return jsonify({'predicted': pred_filepath})
        
    return jsonify({'error': 'Please try again, Allowed image types are - png and jpg'})


if __name__ == "__main__":
    clear_folder()
    app.run(host="0.0.0.0", port=8011)


#TODO: Need to add a scheduler to clean /static/predict/ and /static/uploads/ folders every week or so. We can connect these folder data to a database. 