import requests
import cv2
import os
from dotenv import load_dotenv
load_dotenv()

def pred(filepath):
    url = "https://medai-api-f34085d124bb.herokuapp.com/uploadfile/"
    file_path = filepath

    with open(file_path, "rb") as file:
        files = {"file": file} 
        response = requests.post(url, files=files)
        if response.ok:
            return response
    return "There was an error, try uploading again or a different file" 

def draw_box(response, filepath):
    # Parse JSON response
    response_data = response.json()

    # Extract data
    file_name = response_data['filename']
    predictions = response_data['prediction']['predictions']
    prediction_dim = predictions[0]

    # load image
    image = cv2.imread(filepath)
    x, y, w, h = int(prediction_dim['x']),int(prediction_dim['y']),int(prediction_dim['width']),int(prediction_dim['height'])     
    
    # Convert center (x, y) to top-left (x1, y1)
    x1 = int(x - w / 2)
    y1 = int(y - h / 2)
    x2 = int(x + w / 2)
    y2 = int(y + h / 2)

    # Draw rectangle
    color = (0, 255, 0)  # Green color, this can be changed
    thickness = 2
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
 
    # Add label with class name and confidence
    label = f"{prediction_dim['class']} ({prediction_dim['confidence']:.2f})"
    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return image, file_name
