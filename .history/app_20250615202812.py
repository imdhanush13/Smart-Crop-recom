from flask import Flask, render_template, request
import joblib
import numpy as np
import mysql.connector
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load the trained model and LabelEncoder
model = joblib.load("crop_recommendation_model.pkl")       # Your trained model
label_encoder = joblib.load("label_encoder.pkl")           # Corresponding LabelEncoder

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush08@",   # ✅ Change if needed
    database="crop"
)
cursor = db.cursor()

@app.route("/", methods=["GET", "POST"])
def predict_crop():
    prediction_text = None

    if request.method == "POST":
        try:
            # Get input values from form
            N = int(request.form["N"])
            P = int(request.form["P"])
            K = int(request.form["K"])
            temp = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            # Make prediction
            features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
            prediction = model.predict(features)[0]

            # Decode predicted label
            crop_name = label_encoder.inverse_transform([prediction])[0]

            # Store input + prediction in DB
            insert_query = """
                INSERT INTO crop_data (N, P, K, temperature, humidity, ph, rainfall, predicted_crop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (N, P, K, temp, humidity, ph, rainfall, crop_name)
            cursor.execute(insert_query, values)
            db.commit()

            prediction_text = f"🌾 Recommended Crop: {crop_name.capitalize()}"

        except Exception as e:
            prediction_text = f"❌ Error: {str(e)}"

    return render_template("index.html", prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
