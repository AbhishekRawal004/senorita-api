from flask import Flask, render_template, request, jsonify
from command_parser import CommandParser
from action_handler import ActionHandler
from flask_cors import CORS
import sys
import os

# --- Initialization ---
app = Flask(__name__)
CORS(app)
parser = CommandParser()
actions = ActionHandler()

# --- Utility Function ---
def app_speak_wrapper(content):
    """Logs the response text and speech content to the server console."""
    if isinstance(content, dict):
        # Handle both old and new structured response formats
        text_content = content.get('text_response', content.get('content', str(content)))
        print(f"ASSISTANT SPEAKS (STRUCTURED): {text_content}", file=sys.stderr)
    else:
        print(f"ASSISTANT SPEAKS (TEXT): {content}", file=sys.stderr)

# --- Routes ---
@app.route("/")
def home():
    """Renders the main HTML template."""
    return render_template("index.html")

@app.route("/send_command", methods=["POST"])
def send_command():
    """Receives text command from the client, processes it, and returns the response as text and structured data."""
    try:
        data = request.json
        user_text = data.get("text", "")

        if not user_text:
            return jsonify({"response": {"type": "text", "content": "Please provide a command.", "structured_data": None}})

        # 1. Parse Command
        t = user_text.lower().strip()
        intent, slots = parser.parse(t)

        # 2. Handle Action
        response = actions.handle(intent, slots, app_speak_wrapper)
        
        # 3. Format Response
        # List all structured command types that require mobile-side execution
        mobile_command_types = ["hardware_toggle", "open_mobile_app", "maps_search", "media_deep_link", "add_calendar_event"]
        
        if isinstance(response, dict) and response.get("type") in mobile_command_types:
            # Structured command response
            response_text = response.get("text_response", response.get("content", "Command processed."))
            return jsonify({
                "response": {
                    "type": response["type"],
                    "content": response_text,
                    "structured_data": response
                }
            })
        else:
            # Text-only or image_list response
            response_text = response.get("content", str(response)) if isinstance(response, dict) else str(response)
            
            # For image_list, send the list structure in the structured_data field too
            structured_data = response if isinstance(response, dict) and response.get("type") == "image_list" else None

            return jsonify({
                "response": {
                    "type": response.get("type", "text") if isinstance(response, dict) else "text",
                    "content": response_text,
                    "structured_data": structured_data
                }
            })

    except Exception as e:
        error_message = f"Internal Server Error during command processing. Details: {e}"
        print(f"CRITICAL FLASK ERROR: {error_message}", file=sys.stderr)

        return jsonify({
            "response": {
                "type": "text",
                "content": "Oops! I ran into an internal error while processing your request. Please try again.",
                "structured_data": None
            }
        }), 500

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)