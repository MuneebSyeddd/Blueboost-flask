from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # Needed for OAuth flow

app = Flask(__name__)
CORS(app)

# ------------------------------
# Route: Incoming Message from GHL
# ------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📨 Incoming from GHL:", data)

    # Send to iMessage relay
    send_to_imessage(data)

    return jsonify({'status': 'sent to iMessage'}), 200


# ------------------------------
# Route: Incoming Reply from iMessage
# ------------------------------
@app.route('/reply', methods=['POST'])
def reply():
    data = request.get_json()
    print("📥 Reply from iMessage:", data)

    # Send reply to GoHighLevel Conversations API
    send_to_ghl(data)

    return jsonify({'status': 'synced to GHL'}), 200


# ------------------------------
# Route: OAuth Callback from GHL
# ------------------------------
@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    token_response = requests.post("https://services.leadconnectorhq.com/oauth/token", json={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": "688133f80c16bf99199cf742-mdgcwy4p",
        "client_secret": "bd3eea63-e017-4138-8046-86248e01e2d4",
        "redirect_uri": "https://blueboost-api.onrender.com/oauth/callback"
    })

    # NEW: Log full response
    print("🔍 Raw response:", token_response.status_code, token_response.text)

    data = token_response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    location_id = data.get("locationId")

    print("✅ Access Token:", access_token)
    print("🔁 Refresh Token:", refresh_token)
    print("📍 Location ID:", location_id)

    return "Authorization successful!"



# ------------------------------
# Placeholder: Relay to iMessage
# ------------------------------
def send_to_imessage(data):
    print("📤 [To iMessage]:", data['message'])
    # Example: POST to Mac mini
    # requests.post("http://<mac-ip>:5005/send", json=data)


# ------------------------------
# Placeholder: Push Reply to GHL
# ------------------------------
def send_to_ghl(reply_data):
    print("🔁 [To GHL Conversations]:", reply_data)
    # headers = {
    #     "Authorization": f"Bearer {access_token}",
    #     "Content-Type": "application/json"
    # }
    # requests.post("https://rest.gohighlevel.com/v1/conversations/messages", headers=headers, json=payload)


# ------------------------------
# Run the Flask app
# ------------------------------
if __name__ == '__main__':
    app.run(port=3000)

