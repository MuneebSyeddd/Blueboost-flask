from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ------------------------------
# Route: Incoming Message from GHL
# ------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📨 Incoming from GHL:", data)

    # Send to iMessage relay (you'll define this)
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
# Placeholder: Relay to iMessage
# ------------------------------
def send_to_imessage(data):
    # Implement your logic here:
    # Could be an HTTP POST to Mac relay running on your Mac mini (port 5005?)
    print("📤 [To iMessage]:", data['message'])

    # Example: HTTP POST to your Mac relay
    # import requests
    # requests.post("http://<mac-relay-ip>:5005/send", json=data)


# ------------------------------
# Placeholder: Push Reply to GHL
# ------------------------------
def send_to_ghl(reply_data):
    print("🔁 [To GHL Conversations]:", reply_data)

    # Example (you’ll need to authenticate with GHL OAuth access token):
    # import requests
    # headers = {
    #     "Authorization": f"Bearer {access_token}",
    #     "Content-Type": "application/json"
    # }
    # payload = {
    #     "contactId": reply_data['contact_id'],
    #     "message": reply_data['message']
    # }
    # requests.post("https://rest.gohighlevel.com/v1/conversations/messages", headers=headers, json=payload)


# ------------------------------
# Run the Flask app
# ------------------------------
if __name__ == '__main__':
    app.run(port=3000)

