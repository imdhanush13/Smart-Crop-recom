from flask import jsonify, request

@main.route("/fetch-weather")
def fetch_weather():
    state = request.args.get("state", "").lower()
    district = request.args.get("district", "").lower()
    duration = int(request.args.get("duration", "1"))

    try:
        weather = weather_df[
            (weather_df["State/UT"].str.lower() == state) &
            (weather_df["District"].str.lower() == district)
        ]
        if weather.empty:
            return jsonify({"error": "No weather data found"}), 404

        temp = float(weather["Temperature (°C)"].mean())
        humidity = float(weather["Humidity (%)"].mean())

        current_month = datetime.now().month
        months = [(current_month + i - 1) % 12 + 1 for i in range(duration)]
        month_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        selected_months = [month_cols[m-1] for m in months]

        rain = rainfall_df[
            (rainfall_df["State"].str.lower() == state) &
            (rainfall_df["District"].str.lower() == district)
        ]
        if rain.empty:
            return jsonify({"error": "No rainfall data found"}), 404

        rainfall = float(rain[selected_months].mean(axis=1).values[0])

        return jsonify({
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "rainfall": round(rainfall, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
