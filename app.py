from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "DizBot API is Running"})


@app.route("/status")
def bot_status():
    return jsonify({"status": "DizBot is online!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)


