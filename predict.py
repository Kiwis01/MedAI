from ultralytics import YOLO 

def predict(filepath):
    model = YOLO("./model/best.pt")  
    results =  model.predict(source=filepath, save=True, project="./static/predict", name="result", conf=0.5)
    tumor_label = label(results)
    return results, tumor_label


def label(prediction):
    if prediction and prediction[0].boxes is not None:
        boxes = prediction[0].boxes  
        class_id = int(boxes.cls[0])
        predicted_label = prediction[0].names[class_id]  
        print(f"predicted tumor is {predicted_label}")
        return predicted_label



# if __name__ == '__main__':
#     predict("./static/uploads/tr-pi_1393.jpg")
     