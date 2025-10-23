from flask import Flask, render_template, request, jsonify
from command_parser import CommandParser
from action_handler import ActionHandler
from flask_cors import CORS
import sys
from gtts import gTTS
from io import BytesIO
import base64
import os  # <-- needed for environment variables

# --- Initialization ---
app = Flask(__name__)
CORS(app)  # <-- enables CORS for all routes and origins
parser = CommandParser()
actions = ActionHandler()

# --- Utility Function ---
def app_speak_wrapper(content):
    """Logs the response text and speech content to the server console."""
    if isinstance(content, dict):
        print(f"ASSISTANT SPEAKS (STRUCTURED): {content.get('text_response', content.get('content'))}", file=sys.stderr)
    else:
        print(f"ASSISTANT SPEAKS (TEXT): {content}", file=sys.stderr)

# --- Routes ---
@app.route("/")
def home():
    """Renders the main HTML template."""
    return render_template("index.html")

@app.route("/send_command", methods=["POST"])
def send_command():
    """Receives text command from the client, processes it, and returns the structured response including female TTS audio as base64."""
    try:
        data = request.json
        user_text = data.get("text", "")

        if not user_text:
            return jsonify({"response": {"type": "text", "content": "Please provide a command.", "audio": ""}})

        # 1. Parse Command
        t = user_text.lower().strip()
        intent, slots = parser.parse(t)

        # 2. Handle Action
        response_text = actions.handle(intent, slots, app_speak_wrapper)
        if isinstance(response_text, dict):
            response_text = response_text.get("content", str(response_text))
        if not isinstance(response_text, str):
            response_text = str(response_text)

        # 3. Generate female TTS audio
        tts = gTTS(text=response_text, lang="en", tld="com")
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_base64 = base64.b64encode(audio_fp.read()).decode("utf-8")

        # 4. Return JSON with text + audio
        return jsonify({
            "response": {
                "type": "text",
                "content": response_text,
                "audio": audio_base64
            }
        })

    except Exception as e:
        error_message = f"Internal Server Error during command processing. Details: {e}"
        print(f"CRITICAL FLASK ERROR: {error_message}", file=sys.stderr)

        return jsonify({
            "response": {
                "type": "text",
                "content": "Oops! I ran into an internal error while processing your request. Please try again.",
                "audio": ""
            }
        }), 500

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
