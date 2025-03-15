# Tumor Detector with Bounding Boxes

https://medai-509c7d6aeb86.herokuapp.com

Run the following command to start the app:
```python app.py```
This will redirect you to `http://127.0.0.1:8000` in the browser to visualize the app.

## Setup

Install the required dependencies:
```pip install -r requirements.txt```


## Useful Information
- `"static/script.js"` handles the files (input image and output predictions).
- `"static/predict"` and `"static/uploads"` handle predicted images and uploaded images, respectively.

## Todo

- Connect to database.
- Add sign-in metrics (ideally connected to the database so users can save previous predictions).
- Once deployed, add a refresher to delete unwanted predictions saved on the server.
- Improve the GUI.
- Add confidence threshold.
