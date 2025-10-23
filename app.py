from flask import Flask, render_template, request, jsonify
from command_parser import CommandParser
from action_handler import ActionHandler
from flask_cors import CORS
import sys

# --- Initialization ---
app = Flask(__name__)
CORS(app)  # <-- enables CORS for all routes and origins
parser = CommandParser()
actions = ActionHandler()

# --- Utility Function ---
# This wrapper is passed to ActionHandler.handle to handle the 'speak' side effect (TTS).
# It simply logs the content to the server console for debugging, 
# as the JavaScript client handles the actual TTS based on the returned JSON.
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
    # Assuming 'index.html' exists in the 'templates' folder
    return render_template("index.html")

@app.route("/send_command", methods=["POST"])
def send_command():
    """
    Receives text command from the client, processes it, and returns the structured response.
    """
    try:
        data = request.json
        user_text = data.get("text", "")

        if not user_text:
            response_data = {"type": "text", "content": "Please provide a command."}
            return jsonify({"response": response_data})

        # 1. Parse Command
        t = user_text.lower().strip()
        intent, slots = parser.parse(t)
        
        # 2. Handle Action - The ActionHandler RETURNS the final structured dictionary.
        # It passes the wrapper for the side effect (speech/console log).
        response_data = actions.handle(intent, slots, app_speak_wrapper)
        
        # 3. Finalize Response
        # Ensure the final response is the expected dictionary format.
        if isinstance(response_data, str):
             response_data = {"type": "text", "content": response_data}
        
        # 4. Return JSON to Client
        return jsonify({"response": response_data})
    
    except Exception as e:
        error_message = f"Internal Server Error during command processing. Details: {e}"
        print(f"CRITICAL FLASK ERROR: {error_message}", file=sys.stderr)
        
        error_response = {"type": "text", "content": "Oops! I ran into an internal error while processing your request. Please try again."}
        return jsonify({"response": error_response}), 500

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)