from flask import Flask, render_template, request
import joblib
import numpy as np
import mysql.connector

app = Flask(__name__)

# Load trained model
model = joblib.load("crop_recommendation_model.pkl")  # update path as needed

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush08@",
    database="crop"
)
cursor = db.cursor()

@app.route("/", methods=["GET", "POST"])
def predict_crop():
    prediction_text = None

    if request.method == "POST":
        try:
            # Get form values
            N = int(request.form["N"])
            P = int(request.form["P"])
            K = int(request.form["K"])
            temp = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
            prediction = model.predict(features)[0]

            # Save to DB
            insert = """
                INSERT INTO crop_predictions (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (N, P, K, temp, humidity, ph, rainfall, prediction)
            values = (
            int(N), int(P), int(K),
            float(temp), float(humidity),
            float(ph), float(rainfall),
            str(prediction)
            

            cursor.execute(insert, values)
            db.commit()

            prediction_text = f"🌾 Recommended Crop: {prediction.capitalize()}"

        except Exception as e:
            prediction_text = f"Error: {str(e)}"

    return render_template("index.html", prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
