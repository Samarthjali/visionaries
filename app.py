from flask import Flask, request, jsonify
from ai_model import AIPredictor
from blockchain import store_prediction

app = Flask(__name__)
ai = AIPredictor()

# Hardcode for demo (later replace with your generated account)
PRIVATE_KEY = "your-private-key"
ADDRESS = "your-wallet-address"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    amount = data.get("amount", 0)

    result = ai.predict(amount)
    label = "Risky" if result == 1 else "Safe"

    # Store in blockchain
    txid = store_prediction(PRIVATE_KEY, ADDRESS, label)

    return jsonify({"amount": amount, "prediction": label, "txid": txid})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
