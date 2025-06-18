from flask import Flask
from main import main  # Import your blueprint

app = Flask(__name__)
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
