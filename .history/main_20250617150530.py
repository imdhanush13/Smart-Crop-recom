from flask import Blueprint, render_template, request
import joblib
import numpy as np
import mysql.connector

main = Blueprint('main', __name__)

# Load trained model, label encoder, and scaler
model = joblib.load("crop_recommendation_model.pkl")
scaler = joblib.load("scaler.pkl")

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush08@",
    database="crop"
)
cursor = db.cursor()


# Crop label mapping
crop_label_mapping = {
    0: 'apple', 1: 'banana', 2: 'blackgram', 3: 'chickpea',
    4: 'coconut', 5: 'coffee', 6: 'cotton', 7: 'grapes',
    8: 'jute', 9: 'kidneybeans', 10: 'lentil', 11: 'maize',
    12: 'mango', 13: 'mothbeans', 14: 'mungbean', 15: 'muskmelon',
    16: 'orange', 17: 'papaya', 18: 'pigeonpeas', 19: 'pomegranate',
    20: 'rice', 21: 'watermelon'
}

@main.route('/')
def home():
    return render_template('index.html', show_prediction=False)

@main.route("/predict", methods=["POST"])
def predict_crop():
    try:
        N = int(request.form["N"])
        P = int(request.form["P"])
        K = int(request.form["K"])
        temp = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])

        features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        scaled_features = scaler.transform(features)

        prediction = model.predict(scaled_features)[0]
        predicted_crop = crop_label_mapping[prediction]

        insert = """
            INSERT INTO crop_data (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (N, P, K, temp, humidity, ph, rainfall, predicted_crop)
        cursor.execute(insert, values)
        db.commit()

        return render_template(
            'index.html',
            prediction_text=f'🌾 Predicted Crop: {predicted_crop.capitalize()}',
            show_prediction=True
        )

    except Exception as e:
        return render_template(
            'index.html',
            prediction_text=f'Error: {str(e)}',
            show_prediction=True
        )
