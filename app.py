from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

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

    # Step 1: Exchange code for tokens
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

    # Step 2: Parse and print
    data = token_response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    location_id = data.get("locationId")

    print("✅ Access Token:", access_token)
    print("🔁 Refresh Token:", refresh_token)
    print("📍 Location ID:", location_id)

    # Step 3: Save to tokens.json
    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "location_id": location_id
    }

    try:
        with open("tokens.json", "w") as f:
            json.dump(token_data, f)
        print("💾 Token saved to tokens.json")
    except Exception as e:
        print("❌ Failed to save token:", e)

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

    mac_ip = "http://8.30.153.4:5005/send"

    try:
        response = requests.post(mac_ip, json=payload)
        print(f"📤 Sent to Mac Relay: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"🚨 Error sending to iMessage Relay: {e}")


# ------------------------------
# Push Reply to GHL
# ------------------------------
def send_to_ghl(reply_data):
    def load_tokens():
        with open("tokens.json", "r") as f:
            return json.load(f)

    def save_tokens(tokens):
        with open("tokens.json", "w") as f:
            json.dump(tokens, f)

    def refresh_token(tokens):
        print("🔁 Refreshing token...")
        refresh_response = requests.post(
            "https://services.leadconnectorhq.com/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
                "client_id": "688133f80c16bf99199cf742-mdgcwy4p",
                "client_secret": "bd3eea63-e017-4138-8046-86248e01e2d4"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        refreshed = refresh_response.json()
        print("✅ Token refreshed:", refreshed)

        tokens["access_token"] = refreshed.get("access_token")
        tokens["refresh_token"] = refreshed.get("refresh_token")
        save_tokens(tokens)
        return tokens

    try:
        tokens = load_tokens()
    except Exception as e:
        print("❌ Could not read token file:", e)
        return

    def send_request(access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }

        payload = {
            "contactId": reply_data.get('contact_id'),
            "message": reply_data.get('message'),
            "type": "SMS"
        }

        return requests.post(
            "https://services.leadconnectorhq.com/conversations/messages",
            headers=headers,
            json=payload
        )

    # Try initial send
    response = send_request(tokens["access_token"])

    if response.status_code == 401:
        print("⚠️ Access token expired. Attempting refresh...")
        try:
            tokens = refresh_token(tokens)
            response = send_request(tokens["access_token"])
        except Exception as e:
            print("❌ Token refresh failed:", e)

    print("📨 GHL Response:", response.status_code, response.text)

# ------------------------------
# Run Flask App
# ------------------------------
if __name__ == '__main__':
    app.run(port=3000)


