from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

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

    # Request access token
    token_response = requests.post(
        "https://services.leadconnectorhq.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "688133f80c16bf99199cf742-mdgcwy4p",
            "client_secret": "bd3eea63-e017-4138-8046-86248e01e2d4",
            "redirect_uri": "https://blueboost-api.onrender.com/oauth/callback"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    data = token_response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    location_id = data.get("locationId")

    print("✅ Access Token:", access_token)
    print("🔁 Refresh Token:", refresh_token)
    print("📍 Location ID:", location_id)

    # ✅ Store in environment variables
    os.environ["ACCESS_TOKEN"] = access_token or ""
    os.environ["REFRESH_TOKEN"] = refresh_token or ""
    os.environ["LOCATION_ID"] = location_id or ""

    return "Authorization successful!"


# ------------------------------
# Relay to iMessage (Placeholder)
# ------------------------------
def send_to_imessage(data):
    phone = data.get("phone")
    message = data.get("message")

    if not phone or not message:
        print("❌ Missing phone or message in webhook payload")
        return

    payload = {
        "phone": phone,
        "message": message
    }

    # Replace this with your actual Mac's public IP
    mac_ip = "http://YOUR_PUBLIC_MAC_IP:5005/send"

    try:
        response = requests.post(mac_ip, json=payload)
        print(f"📤 Sent to Mac Relay: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"🚨 Error sending to iMessage Relay: {e}")


# ------------------------------
# Push Reply to GHL
# ------------------------------
def send_to_ghl(reply_data):
    print("🔁 [To GHL Conversations]:", reply_data)
    access_token = os.getenv("ACCESS_TOKEN")

    if not access_token:
        print("❌ No access token available")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "contactId": reply_data.get('contact_id'),
        "message": reply_data.get('message')
    }

    response = requests.post(
        "https://services.leadconnectorhq.com/conversations/messages",
        headers=headers,
        json=payload
    )

    print("📨 Response from GHL:", response.status_code, response.text)


# ------------------------------
# Run Flask App
# ------------------------------
if __name__ == '__main__':
    app.run(port=3000)


