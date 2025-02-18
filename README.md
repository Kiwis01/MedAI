# Tumor Detector with Bounding Boxes

Run the following command to start the app:
```python app.py```


This will redirect you to `http://127.0.0.1:5000` in the browser to visualize the app.

## Setup

Install the required dependencies:
```pip install -r requirements.txt```


## Useful Information

- `"training/"` is not needed in the app; it's just for experimentation and trying different datasets, etc.
- `"static/script.js"` handles the files (input image and output predictions).
- `"static/predict"` and `"static/uploads"` handle predicted images and uploaded images, respectively.
- `"predict.py"` can run independently. Some code is commented out if you want to try local predictions (without running Flask).

## Todo

- Connect to database.
- Add sign-in metrics (ideally connected to the database so users can save previous predictions).
- Once deployed, add a refresher to delete unwanted predictions saved on the server.
- Improve the GUI.
- Add confidence threshold.
