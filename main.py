from flask import Blueprint, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

main = Blueprint('main', __name__)

# Load model and scaler
model = joblib.load("crop_recommendation_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load data
weather_df = pd.read_csv("weather-1.csv")
rainfall_df = pd.read_csv("Monthly District Avg RainFall 1901 - 2017.csv")



crop_label_mapping = {
    0: 'apple', 1: 'banana', 2: 'blackgram', 3: 'chickpea', 4: 'coconut',
    5: 'coffee', 6: 'cotton', 7: 'grapes', 8: 'jute', 9: 'kidneybeans',
    10: 'lentil', 11: 'maize', 12: 'mango', 13: 'mothbeans', 14: 'mungbean',
    15: 'muskmelon', 16: 'orange', 17: 'papaya', 18: 'pigeonpeas',
    19: 'pomegranate', 20: 'rice', 21: 'watermelon'
}

@main.route('/')
def home():
    return render_template('index.html', show_prediction=False)

@main.route("/fetch-weather")
def fetch_weather():
    state = request.args.get("state")
    district = request.args.get("district")
    duration = int(request.args.get("duration", 3))

    weather = weather_df[
        (weather_df["State/UT"].str.lower() == state.lower()) &
        (weather_df["District"].str.lower() == district.lower())
    ]
    rain = rainfall_df[
        (rainfall_df["State"].str.lower() == state.lower()) &
        (rainfall_df["District"].str.lower() == district.lower())
    ]

    if weather.empty or rain.empty:
        return jsonify({"error": "Data not found"}), 404

    temp = float(weather["Temperature (°C)"].mean())
    humidity = float(weather["Humidity (%)"].mean())

    current_month = datetime.now().month
    months = [(current_month + i - 1) % 12 + 1 for i in range(duration)]
    month_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                  'Sep', 'Oct', 'Nov', 'Dec']
    selected_months = [month_cols[m - 1] for m in months]
    rainfall = float(rain[selected_months].mean(axis=1).values[0])

    return jsonify({
        "temperature": round(temp, 2),
        "humidity": round(humidity, 2),
        "rainfall": round(rainfall, 2)
    })

@main.route("/predict", methods=["POST"])
def predict_crop():
    try:
        N = int(request.form["N"])
        P = int(request.form["P"])
        K = int(request.form["K"])
        ph = float(request.form["ph"])
        temp = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        rainfall = float(request.form["rainfall"])

        features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        scaled = scaler.transform(features)
        pred = model.predict(scaled)[0]
        crop = crop_label_mapping[pred]


        return render_template("index.html", prediction_text=f"🌾 Predicted Crop: {crop.capitalize()}", show_prediction=True)
    except Exception as e:
        return render_template("index.html", prediction_text=f"❌ Error: {e}", show_prediction=True)
