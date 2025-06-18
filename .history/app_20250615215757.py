from flask import Flask, render_template, request
import joblib
import numpy as np
import mysql.connector

app = Flask(__name__)

# Load the trained model and label encoder
model = joblib.load("crop_recommendation_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush08",  # <-- update this
    database="crop"
)
cursor = db.cursor()

@app.route("/", methods=["GET", "POST"])
def index():
    prediction_text = None
    if request.method == "POST":
        try:
            # Get user inputs
            N = int(request.form["N"])
            P = int(request.form["P"])
            K = int(request.form["K"])
            temp = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            # Make prediction
            features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
            prediction_encoded = model.predict(features)[0]
            prediction = label_encoder.inverse_transform([prediction_encoded])[0]

            # Store in database
            insert = """
                INSERT INTO crop_data (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (N, P, K, temp, humidity, ph, rainfall, prediction)
            cursor.execute(insert, values)
            db.commit()

            prediction_text = f"🌾 Recommended Crop: {prediction.capitalize()}"

        except Exception as e:
            prediction_text = f"Error: {str(e)}"

    return render_template("index.html", prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
