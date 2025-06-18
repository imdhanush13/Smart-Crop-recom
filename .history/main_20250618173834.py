from flask import Blueprint, render_template, request
import joblib
import numpy as np
import pandas as pd
import mysql.connector
from datetime import datetime

main = Blueprint('main', __name__)

# Load model and scaler
model = joblib.load("crop_recommendation_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load weather and rainfall data
weather_df = pd.read_csv("weather-1.csv")
rainfall_df = pd.read_csv("Monthly District Avg RainFall 1901 - 2017.csv")

# Database connection
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
        # Get form values
        N = int(request.form["N"])
        P = int(request.form["P"])
        K = int(request.form["K"])
        ph = float(request.form["ph"])
        state = request.form["state"]
        district = request.form["district"]
        duration = int(request.form["duration"])

        # Get weather values
        weather = weather_df[
            (weather_df["State/UT"].str.lower() == state.lower()) &
            (weather_df["District"].str.lower() == district.lower())
        ]

        if weather.empty:
            return render_template('index.html', prediction_text="❌ Weather data not found for selected district!", show_prediction=True)

        temp = float(weather["Temperature (°C)"].mean())
        humidity = float(weather["Humidity (%)"].mean())

        # Get month range
        current_month = datetime.now().month
        months = [(current_month + i - 1) % 12 + 1 for i in range(duration)]
        month_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        selected_months = [month_cols[m-1] for m in months]

        # Get rainfall values
        rain = rainfall_df[
            (rainfall_df["State"].str.lower() == state.lower()) &
            (rainfall_df["District"].str.lower() == district.lower())
        ]

        if rain.empty:
            return render_template('index.html', prediction_text="❌ Rainfall data not found for selected district!", show_prediction=True)

        rainfall = float(rain[selected_months].mean(axis=1).values[0])

        # Final input
        features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        scaled_features = scaler.transform(features)

        prediction = model.predict(scaled_features)[0]
        predicted_crop = crop_label_mapping[prediction]

        # Store in DB
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
        return render_template('index.html', prediction_text=f'Error: {str(e)}', show_prediction=True)
