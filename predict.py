from ultralytics import YOLO 

def predict(filepath):
    model = YOLO("./model/best.pt")  
    results =  model.predict(source=filepath, save=True, project="./static/predict", name="result", conf=0.5)
    return results

# if __name__ == '__main__':
#     predict("./static/uploads/tr-pi_1393.jpg")
    