from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import predict
from pathlib import Path
import shutil
import os

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
        prediction = predict.predict(filepath)

        # YOLO saves results in a directory like static/predict/result2
        prediction_dir = Path(prediction[0].save_dir) / filename
        if prediction_dir.exists(): 
            prediction_path = prediction_dir.as_posix()  # Convert to forward slashes
            return jsonify({'predicted': prediction_path})
        else:
            return jsonify({'error': 'Prediction image not found'})
        
    return jsonify({'error': 'Allowed image types are - png, jpg, jpeg, gif'})


if __name__ == "__main__":
    clear_folder()
    app.run(host="0.0.0.0", port=8000)


#TODO: Need to add a scheduler to clean /static/predict/ and /static/uploads/ folders every week or so. We can connect these folder data to a database. 