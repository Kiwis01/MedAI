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

def chat(text, prediction=None):
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "generationConfig": {
            "stopSequences": [
                "Title"
            ],
            "temperature": 1.0,
            "maxOutputTokens":200,
            "topP": 0.8,
            "topK": 10
        },
        "system_instruction": {
        "parts": [
        { "text": "You are collaborating with medical professionals to assist users in understanding their symptoms. Your primary goal is to provide honest, accurate, and reliable information based on the listed symptoms. Ensure that your responses are clear, medically sound, and aligned with best practices in healthcare. Make educated diagnoses or medical claims; but also encourage users to consult a qualified healthcare provider for professional evaluation and treatment when necessary."},
        { "text": "Keep in mind that the output should not exceed 200 tokens. Ensure that responses are concise, relevant, and well-structured while maintaining clarity and accuracy."},
        { "text": f"Consider that the tumor prediction from the image is {prediction}. Make sure that you are also considering confidence scores since low confidence scores should make the tumor even less likely to be present, however do not skip on informing the user if there is a posibility of a tumor being present. The prediction has 5 possible values: Pituitary, Glioma, Meningioma, No Tumor, and None (default). If the prediction is none it means that the user has not utilized the classification model yet, if that is the case and the symptoms listed by the user seem to be correlated to a brain tumor, suggest the user to upload a medical image so the web application can perform a classification task and possibly predict a tumor."},
        # { "text": "Make sure to not mention exact results coming from the prediction value, use high, low, medium to represent the confidence score"}
            ]
        },

        "contents": {
        "parts": {
            "text": text}
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return(response)

#TODO: We need at least 3 studies by medical professionals regarding information of each of the three tumors, pituitary, meningioma, glioma.
    # chatbot
        # Add chatbot into html design
        # Implement conversation awareness
    
    # Vector Embedding 
        # embed pdf medical files

    # Add more instructions
        # Instructions to evaluate medical files stored in vector embeddings

    # Add login auth

    # Add database
        # store medical responses on database 


if __name__ == "__main__":
    response = chat("I am sick, Im having strong headaches, I had seizure in the last two weeks, and I have been nauseous all day. What could be the issue? ", prediction="None")
    response_data = response.json()
    response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
    usage_metadata = response_data["usageMetadata"]

    print("Response Text:")
    print(response_text)

    print("\nUsage Metadata:")
    print(usage_metadata)
