from flask import Blueprint, render_template, request
import joblib
import numpy as np
import mysql.connector

main = Blueprint('main', __name__)

# Load trained model
model = joblib.load("crop_recommendation_model.pkl") 

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush08@",
    database="crop"
)
cursor = db.cursor()

@main.route('/')
def home():
    return render_template('index.html', show_prediction = False)

@main.route("/predict", methods=["POST"])
def predict_crop():
    if request.method == "POST":
            N = int(request.form["N"])
            P = int(request.form["P"])
            K = int(request.form["K"])
            temp = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            features = np.array([N, P, K, temp, humidity, ph, rainfall]).reshape(1, -1)
            prediction = model.predict(features)[0]
            

            crop_label_mapping = {
    0: 'apple',
    1: 'banana',
    2: 'blackgram',
    3: 'chickpea',
    4: 'coconut',
    5: 'coffee',
    6: 'cotton',
    7: 'grapes',
    8: 'jute',
    9: 'kidneybeans',
    10: 'lentil',
    11: 'maize',
    12: 'mango',
    13: 'mothbeans',
    14: 'mungbean',
    15: 'muskmelon',
    16: 'orange',
    17: 'papaya',
    18: 'pigeonpeas',
    19: 'pomegranate',
    20: 'rice',
    21: 'watermelon'
}

            

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
            )

            cursor.execute(insert, values)
            db.commit()

            prediction_text = f"🌾 Recommended Crop: {prediction.capitalize()}"

        except Exception as e:
            prediction_text = f"Error: {str(e)}"

    return render_template("index.html", prediction_text=prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
