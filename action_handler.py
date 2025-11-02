import datetime
import os
import sys
import json
import requests
import time
import pytz
import random 
import re 
from datetime import datetime, timedelta

import os

# --- BASE CONSTANTS (HARDCODED FOR LOCAL TESTING) ---
# WARNING: DELETE THESE KEYS BEFORE DEPLOYMENT.
API_KEY = "AIzaSyBLKlvvfpGFt-7VE9KGEawvowVLg8lQ_oM".strip() 
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
USER_DATA_FILE = "user_data.json"

# --- EXTERNAL API KEYS AND URLs (HARDCODED FOR LOCAL TESTING) ---
WEATHER_API_KEY = "a51eb3849c1ee6390888af3c304f602f".strip()
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
NEWS_API_KEY = "217f554ac72748d9a52a35fee2d07856".strip()
NEWS_API_URL = "https://newsapi.org/v2/top-headlines" 
NASA_API_KEY = "G4woneZEsTf4qaAjmF4bIY6AALRwx7Vl42LNt7dC".strip()
NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1"

# --- IMAGE SEARCH CONSTANTS (HARDCODED FOR LOCAL TESTING) ---
GOOGLE_API_KEY = "AIzaSyCoziUxrf0YSMpX1IDlltXziH8NKELmLkQ".strip() 
GOOGLE_CUSTOM_SEARCH_CX = "1702b3481ec8b4dce".strip()
# ===================================================

class ActionHandler:
    """
    Handles the execution of specific intents, including state management for user data
    and contextual conversation history.
    """
    def __init__(self):
        self.user_data = self._load_data()
        self.conversation_history = [] 
        self.last_image_query = None
        self.last_image_start_index = 1
        self.user_data["waiting_for_platform"] = None 

        self.conversation_context = {
            "current_topic": None,
            "user_mood": "neutral",
            "last_action": None,
            "preferences": {}
        } 
        
    def _get_default_data(self):
        """Returns the default structure for user data, now expanded."""
        return {
            "name": None,
            "favorite_things": {}, 
            "interests": [],
            "waiting_for_platform": None,
            "reminders": []
        }

    def _load_data(self):
        """Loads user data (like name, favorites, interests) from the persistent JSON file.)"""
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, 'r') as f:
                    print(f"Loading user data from {USER_DATA_FILE}")
                    loaded_data = json.load(f)
                    default_data = self._get_default_data()
                    return {**default_data, **loaded_data, "waiting_for_platform": None, "reminders": loaded_data.get("reminders", [])}
            except Exception as e:
                print(f"Error loading user data from {USER_DATA_FILE}: {e}. Using default data.")
                return self._get_default_data()
        else:
            print(f"User data file {USER_DATA_FILE} not found. Using default data.")
            return self._get_default_data()

    def _save_data(self):
        """Saves the current *persistent* user data to the JSON file."""
        try:
            data_to_save = {
                "name": self.user_data.get("name"),
                "favorite_things": self.user_data.get("favorite_things", {}),
                "interests": self.user_data.get("interests", []),
                "reminders": self.user_data.get("reminders", []), 
            }
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"User data saved to {USER_DATA_FILE}")
        except Exception as e:
            print(f"Error saving user data to {USER_DATA_FILE}: {e}")
            
    # --- EXTERNAL API HANDLERS ---

    def _get_weather(self, city: str, speak) -> bool:
        """Fetches and speaks the current weather for a specified city."""
        global WEATHER_API_KEY, WEATHER_API_URL
        
        if "YOUR_OPENWEATHERMAP_KEY_HERE" in WEATHER_API_KEY:
            speak("Weather API Key is placeholder. Please update it in action_handler.py.")
            print("ERROR: WEATHER_API_KEY is empty!", file=sys.stderr)
            return False

        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        try:
            response = requests.get(WEATHER_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("cod") == 200:
                main_data = data["main"]
                weather_desc = data["weather"][0]["description"]
                temp = int(main_data["temp"])
                speak(f"The weather in {city.title()} is currently {weather_desc}, with a temperature of {temp} degrees Celsius.")
                return True
            else:
                error_msg = data.get("message", "unknown error")
                speak(f"Sorry, I couldn't find the weather for {city.title()}. The service reported: {error_msg}.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Weather API Error: {e}", file=sys.stderr)
            speak("I'm having trouble connecting to the weather service right now. Check the API key and connection.")
            return False

    def _get_news(self, topic: str, speak) -> bool:
        """Fetches and speaks the top news headlines for a specified topic."""
        
        if "YOUR_NEWSAPI_KEY_HERE" in NEWS_API_KEY:
            speak("News API Key is placeholder. Please update it in action_handler.py.")
            return False
            
        params = {"q": topic if topic else "technology", "apiKey": NEWS_API_KEY, "language": "en", "pageSize": 3 }
        try:
            response = requests.get(NEWS_API_URL, params=params, timeout=7)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                headlines = [a["title"] for a in articles]
                speak(f"Here are the top headlines for '{topic if topic else 'technology'}': 1. {headlines[0]}. 2. {headlines[1]}. 3. {headlines[2]}.")
                return True
            else:
                speak(f"I couldn't find any news articles for '{topic}'.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"News API Error: {e}", file=sys.stderr)
            speak("I'm having trouble connecting to the news service right now.")
            return False

    def _get_nasa_apod(self, speak) -> bool:
        """Fetches and speaks the title and explanation of NASA's Astronomy Picture of the Day (APOD)."""
        
        if "YOUR_NASA_KEY_HERE" in NASA_API_KEY:
            speak("NASA API Key is placeholder. Please update it in action_handler.py.")
            print("ERROR: NASA_API_KEY is empty!", file=sys.stderr)
            return False

        params = {"api_key": NASA_API_KEY}
        try:
            response = requests.get(NASA_APOD_URL, params=params, timeout=7)
            response.raise_for_status()
            data = response.json()
            title = data.get("title", "the Astronomy Picture of the Day")
            speak(f"Today's NASA picture is titled '{title}'. You can search for it online to see the image.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"NASA API Error: {e}", file=sys.stderr)
            speak("I'm sorry, I failed to retrieve the NASA picture of the day.")
            return False

    def _get_trivia(self, speak) -> bool:
        """Fetches and speaks a random trivia question."""
        try:
            response = requests.get(TRIVIA_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if results:
                question = results[0].get("question", "What is the meaning of life?")
                speak(f"Here is a trivia question: {question}")
                return True
            else:
                speak("I couldn't find a fun fact right now.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Trivia API Error: {e}", file=sys.stderr)
            speak("I'm unable to connect to the trivia database right now.")
            return False
    
    def search_for_image(self, query, start_index=1, num_results=10):
        """Uses the Google Custom Search API to find multiple image URLs."""
        if "AIzaSyCoziUxrf0YSMpX1IDlltXziH8NKELmLkQ" not in GOOGLE_API_KEY or "1702b3481ec8b4dce" not in GOOGLE_CUSTOM_SEARCH_CX:
            error_msg = "Google Image API Key or CX ID is missing. Image search disabled."
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return None

        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'cx': GOOGLE_CUSTOM_SEARCH_CX,
            'key': GOOGLE_API_KEY,
            'searchType': 'image', 
            'num': min(num_results, 10),
            'start': start_index
        }

        try:
            response = requests.get(search_url, params=params, timeout=7)
            response.raise_for_status()
            data = response.json()

            if 'items' in data and data['items']:
                images = []
                for item in data['items']:
                    images.append({
                        'url': item['link'],
                        'title': item.get('title', ''),
                        'thumbnail': item.get('image', {}).get('thumbnailLink', item['link'])
                    })
                return images
            
        except requests.exceptions.RequestException as e:
            print(f"Image Search API Error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred during image search: {e}", file=sys.stderr)

        return None
    
    def _update_conversation_context(self, user_input, response_type, response_content):
        """Update conversation context based on user input and response."""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['image', 'picture', 'photo', 'show me']):
            self.conversation_context["current_topic"] = "image search"
        elif any(word in user_input_lower for word in ['video', 'play', 'watch', 'youtube', 'spotify', 'song', 'music']):
            self.conversation_context["current_topic"] = "media content"
        elif any(word in user_input_lower for word in ['weather', 'temperature']):
            self.conversation_context["current_topic"] = "weather"
        else:
            self.conversation_context["current_topic"] = "general conversation"
        
        self.conversation_context["last_action"] = response_type
        
        if any(word in user_input_lower for word in ['thanks', 'thank you', 'great', 'awesome', 'love']):
            self.conversation_context["user_mood"] = "positive"
        elif any(word in user_input_lower for word in ['help', 'problem', 'issue', 'error']):
            self.conversation_context["user_mood"] = "needs_help"
        elif any(word in user_input_lower for word in ['urgent', 'quickly', 'asap']):
            self.conversation_context["user_mood"] = "urgent"
        else:
            self.conversation_context["user_mood"] = "neutral"

    def handle_image_request(self, user_input, speak):
        """Handles commands like 'show me' or 'display' an image, supporting 'more'."""
        user_input_lower = user_input.lower()
        
        is_follow_up = "more" in user_input_lower and len(user_input_lower.split()) <= 3
        query = user_input_lower

        if is_follow_up:
            print(f"DEBUG: Follow-up request detected. Last query: {self.last_image_query}, Start index: {self.last_image_start_index}", file=sys.stderr)
            if self.last_image_query:
                query = self.last_image_query
                images = self.search_for_image(query, start_index=self.last_image_start_index + 10, num_results=10)
                if images:
                    text_response = f"Here are more pictures of **{query.title()}**!"
                    response_data = {
                        "type": "image_list",
                        "content": images,
                        "text_response": text_response,
                        "query": query,
                        "start_index": self.last_image_start_index + 10
                    }
                    self.last_image_start_index += 10
                    speak(response_data)
                    return response_data
                else:
                    text_response = f"No more images found for **{query.title()}**. Try a different search!"
                    speak(text_response)
                    return {"type": "text", "content": text_response}
            else:
                text_response = "I'm not sure what you mean by 'more'. What image were you looking for?"
                speak(text_response)
                return {"type": "text", "content": text_response}
        else:
            search_query = query 

        if not search_query:
            text_response = "I need a subject to search for. Try 'show me a dog'."
            speak(text_response)
            return {"type": "text", "content": text_response}

        images = self.search_for_image(search_query, start_index=1, num_results=10)

        if images:
            print(f"DEBUG: Found {len(images)} images for query: {query}", file=sys.stderr)
            text_response = f"Found {len(images)} pictures of **{query.title()}** for you. Click 'Load More' for additional images!"
            
            self.last_image_query = query 
            self.last_image_start_index = 1
            
            response_data = {
                "type": "image_list",
                "content": images,
                "text_response": text_response,
                "query": query,
                "start_index": 1
            }
            speak(response_data)
            return response_data
        else:
            self.last_image_query = None 
            text_response = f"Sorry, I couldn't find any relevant images for '{query}'. Check your API keys if this persists."
            speak(text_response)
            return {"type": "text", "content": text_response}

    def _extract_and_save_personal_info(self, query: str, speak):
        """Uses Gemini to extract and save personal information from a query."""
        extraction_prompt = f"""Analyze the user's sentence: '{query}'. 
        If the sentence is setting a personal preference (e.g., 'My favorite color is blue' or 'I like watching sci-fi movies'), extract the key and the value.
        Key examples: 'favorite color', 'favorite food', 'interest', 'hobby'.
        Value examples: 'blue', 'pizza', 'sci-fi movies'.
        
        Respond ONLY in a JSON format like this:
        {{ "type": "favorite", "key": "favorite food", "value": "pizza" }}
        OR
        {{ "type": "interest", "value": "sci-fi movies" }}
        OR if no personal info is found:
        {{ "type": "none" }}
        DO NOT include any explanation or additional text outside the JSON block."""

        raw_response = self._call_gemini_api(extraction_prompt, history=None)

        try:
            start = raw_response.find('{')
            end = raw_response.rfind('}') + 1
            json_str = raw_response[start:end]
            
            data = json.loads(json_str)
            
            info_type = data.get("type")
            
            if info_type == "favorite":
                key = data.get("key").lower().strip()
                value = data.get("value").strip()
                if key and value:
                    self.user_data["favorite_things"][key] = value
                    self._save_data()
                    speak(f"Got it! I'll remember that your {key} is **{value}**.")
                    return True
            
            elif info_type == "interest":
                value = data.get("value").strip()
                if value and value not in self.user_data["interests"]:
                    self.user_data["interests"].append(value)
                    self._save_data()
                    speak(f"Cool! I've noted that you are interested in **{value}**.")
                    return True

        except Exception as e:
            print(f"Error parsing Gemini response for personal info: {e}. Raw: {raw_response}", file=sys.stderr)
            pass
        
        return False
        
    def _map_location_to_timezone(self, location: str) -> str:
        """Maps a common location name to a IANA timezone string."""
        location = location.lower().strip()
        
        if "thailand" in location: return "Asia/Bangkok"
        if "london" in location or "uk" in location: return "Europe/London"
        if "tokyo" in location or "japan" in location: return "Asia/Tokyo"
        if "new york" in location or "nyc" in location: return "America/New_York"
        if "dubai" in location or "uae" in location: return "Asia/Dubai"
        if "paris" in location or "france" in location: return "Europe/Paris"
        if "india" in location or "mumbai" in location or "delhi" in location: return "Asia/Kolkata"

        try:
            matches = [tz for tz in pytz.all_timezones if location in tz.lower()]
            if matches: return matches[0]
        except Exception:
            pass
        return None

    def _call_gemini_api(self, user_query: str, history: list = None):
        """Calls the Gemini API with conversation history and system instruction."""
        global API_KEY, GEMINI_API_URL
        
        if "AIzaSyBLKlvvfpGFt-7VE9KGEawvowVLg8lQ_oM" not in API_KEY:
            return "My connection to the knowledge base is blocked because the Gemini API key is missing or invalid. Please check the .env file."
        
        system_prompt = """You are Senorita, a helpful, friendly, and intelligent personal assistant. You are designed to sound human and conversational, not like an AI or language model.

Key traits:
- Be warm, friendly, friendly, and engaging
- Remember context from previous messages in the conversation
- Ask follow-up questions when appropriate
- Show genuine interest in helping the user
- Use natural, conversational language
- Be concise but not robotic
- Remember the user's name and preferences when mentioned
- Adapt your tone to match the user's mood and needs

Current context:
- User name: {user_name}
- Current topic: {current_topic}
- Last action: {last_action}
- User mood: {user_mood}

Answer the user's query clearly and helpfully, maintaining context and building on previous conversation.""".format(
            user_name=self.user_data.get('name', 'friend'),
            current_topic=self.conversation_context.get('current_topic', 'general conversation'),
            last_action=self.conversation_context.get('last_action', 'none'),
            user_mood=self.conversation_context.get('user_mood', 'neutral')
        )
        
        contents = []
        if history: contents.extend(history)
        
        contents.append({ "role": "user", "parts": [{ "text": user_query }] })

        payload = {
            "contents": contents,
            "tools": [{ "google_search": {} }],
            "systemInstruction": {
                "parts": [{ "text": system_prompt }]
            },
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", 
                                         headers={'Content-Type': 'application/json'}, 
                                         data=json.dumps(payload),
                                         timeout=15)
                
                response.raise_for_status()
                result = response.json()
                candidate = result.get("candidates", [])[0]
                text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "Sorry, I couldn't find an answer.")
                
                return text.replace('**', '').replace('***', '').strip() 

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    if 'response' in locals() and response.status_code != 200:
                         return f"I received an error code {response.status_code} from the search service."
                    else:
                         print(f"CRITICAL API ERROR: {e}", file=sys.stderr)
                         return "I'm sorry, I'm having trouble connecting to my knowledge base right now."

            except Exception as e:
                return "I received a response, but couldn't understand it."
        return "I experienced too many errors trying to get an answer."

    def _check_for_immediate_platform_and_launch(self, query: str, speak):
        """
        Checks if the query contains an explicit platform mention (YouTube, Spotify, JioSaavn).
        If found, prepares the structured response and returns the structured response.
        Returns False otherwise.
        """
        query_lower = query.lower()
        platform_name = None
        media_query = query_lower 

        if "youtube" in query_lower or "yt" in query_lower:
            platform_name = "youtube"
        elif "spotify" in query_lower:
            platform_name = "spotify"
        elif "jiosaavn" in query_lower or "saavn" in query_lower:
            platform_name = "jiosaavn"
        
        if platform_name:
            platform_terms = [f" in {platform_name}", f" on {platform_name}", platform_name]
            
            for term in platform_terms:
                if term in query_lower:
                    media_query = query_lower.split(term)[0].strip()
                    break

            if not media_query or media_query in ["play", "search", "watch", "listen"]:
                 clean_query_match = re.search(r'(play|listen to|watch|search for)\s+(.*?)', query_lower)
                 if clean_query_match:
                     media_query = clean_query_match.group(2).strip()
                 else:
                     media_query = query_lower

            return self._open_search_link(platform_name, media_query, speak)
            
        return False

    def _open_search_link(self, platform_name: str, query: str, speak):
        """Generates structured response for opening search results via deep links."""
        query_encoded = requests.utils.quote(query)
        url = None
        platform_display = platform_name.title()

        if platform_name == "youtube" or platform_name == "yt":
            url = f"vnd.youtube://www.youtube.com/results?search_query={query_encoded}"
            platform_display = "YouTube"
        elif platform_name == "spotify":
            url = f"spotify:search:{query_encoded}"
            platform_display = "Spotify"
        elif platform_name == "jiosaavn":
            url = f"jiosaavn://search/{query_encoded}"
            platform_display = "JioSaavn"
        else:
            url = f"https://www.google.com/search?q={query_encoded}+{platform_name}+music+video"
            platform_display = f"Google for {platform_name}"

        response_text = f"Searching for '{query.title()}' and opening the results on **{platform_display}** now. Enjoy!"
        speak(response_text)
        
        return {
            "type": "media_deep_link", 
            "url": url,
            "text_response": response_text
        }

    def open_app(self, app_name: str, speak):
        """Generates structured response for opening a generic application."""
        app_name_clean = app_name.strip().title()
        response_text = f"Requesting the mobile app to open **{app_name_clean}**."
        speak(response_text)
        
        return {
            "type": "open_mobile_app",
            "app_name": app_name_clean,
            "text_response": response_text
        }
        
    def _extract_time_and_task(self, query: str):
        """Uses Gemini to extract structured time and task data from the reminder query."""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        extraction_prompt = f"""
        Analyze the following reminder request. 
        Current time is: {current_time} (in the format YYYY-MM-DD HH:MM:SS).

        Rules:
        1. Extract the primary 'task' or 'note' to be remembered.
        2. Extract the 'reminder_time' as a clear, absolute date and time string (e.g., "Tuesday at 3 PM" or "2025-10-22 10:00 AM"). If no time is found, set it to NULL.
        3. Extract the 'task_only' without the time phrases, for cleaner storage.
        4. If the query is just a generic note without any time/date mentioned (e.g., "buy milk"), set reminder_time to NULL.

        Query: "{query}"

        Respond ONLY in a JSON format like this:
        {{ "task": "call mom", "task_only": "call mom", "reminder_time": "2025-10-22 10:00 AM" }}
        OR (if no time is detected):
        {{ "task": "buy milk", "task_only": "buy milk", "reminder_time": null }}
        DO NOT include any explanation or additional text outside the JSON block."""
        
        response = self._call_gemini_api(extraction_prompt, history=[])
        
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            
            if data.get("task_only") and data.get("task_only").strip():
                return data
            
        except Exception as e:
            print(f"Error parsing Gemini response for reminder extraction: {e}", file=sys.stderr)
        
        return {"task": query, "task_only": query.strip(), "reminder_time": None}

    def _extract_calendar_event(self, query: str):
        """NEW: Uses Gemini to extract structured calendar event data."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        extraction_prompt = f"""
        Analyze the following event request. 
        Current time is: {current_time} (in the format YYYY-MM-DD HH:MM:SS).

        Rules:
        1. Extract the 'title' of the event/meeting.
        2. Extract the 'start_time' as a string in ISO 8601 format (YYYY-MM-DD HH:MM:SS). Resolve relative times (e.g., 'tomorrow 3pm').
        3. Extract the 'end_time' in the same ISO 8601 format. If duration is not specified, set end_time 1 hour after start_time. If no time/date is found, use null for both.
        4. Set 'all_day' to true if the event is clearly an all-day event (e.g., "birthday on Monday") or false otherwise.
        5. Extract a brief 'description' for the event, or use the query itself.

        Query: "{query}"

        Respond ONLY in a JSON format like this:
        {{ "title": "Team Meeting", "description": "Discuss project launch.", "start_time": "2025-11-20 15:00:00", "end_time": "2025-11-20 16:00:00", "all_day": false }}
        OR (if no time is detected):
        {{ "title": null, "description": null, "start_time": null, "end_time": null, "all_day": false }}
        DO NOT include any explanation or additional text outside the JSON block."""
        
        response = self._call_gemini_api(extraction_prompt, history=[])
        
        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            return data
            
        except Exception as e:
            print(f"Error parsing Gemini response for calendar extraction: {e}", file=sys.stderr)
        
        return {"title": None, "description": None, "start_time": None, "end_time": None, "all_day": False}


    def handle_set_reminder(self, query: str, speak):
        """Adds a new reminder to the user's persistent data (Feature A)."""
        if not query:
            answer = "I need something to remember! What should I add to your list?"
        else:
            extracted_data = self._extract_time_and_task(query)
            
            task_only = extracted_data["task_only"]
            reminder_time_raw = extracted_data["reminder_time"]
            
            task_to_store = task_only.strip() 

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            reminder_entry = {
                "note": task_to_store, 
                "timestamp": timestamp,
                "remind_at": reminder_time_raw
            }
            
            self.user_data["reminders"].append(reminder_entry)
            self._save_data()
            
            if reminder_time_raw and reminder_time_raw.lower() != 'null':
                answer = f"Okay, I've noted: **{task_to_store}**. I will remind you about that on **{reminder_time_raw}**."
            else:
                answer = f"Okay, I've noted: **{task_to_store}**."


        speak(answer)
        return {"type": "text", "content": answer}

    def handle_recall_notes(self, speak):
        """Retrieves and speaks the list of reminders (Feature A)."""
        reminders = self.user_data.get("reminders", [])
        
        if not reminders:
            answer = "You have no notes or reminders currently stored. Want to add one?"
        else:
            reminder_text_display = []
            reminder_text_speak = []

            for i, r in enumerate(reminders):
                note = r.get('note', 'Untitled Note')
                added_date = r.get('timestamp', 'Unknown Date').split()[0]
                remind_at = r.get('remind_at')
                
                time_suffix = f" (Remind: **{remind_at}**)" if remind_at and remind_at.lower() != 'null' else ""
                
                reminder_text_display.append(f"- **{i+1}.** {note}{time_suffix} (Added: {added_date})")
                
                speak_time = f"for {remind_at.replace('AM', ' A. M.').replace('PM', ' P. M.')}" if remind_at and remind_at.lower() != 'null' else ""
                reminder_text_speak.append(f"Number {i+1}, {note} {speak_time}")

            
            reminder_text_display = "\n".join(reminder_text_display)
            reminder_text_speak = ", ".join(reminder_text_speak)

            speak(f"You currently have {len(reminders)} items on your list. They are: {reminder_text_speak}.")
            
            answer = f"You currently have {len(reminders)} items on your list:\n{reminder_text_display}\n\n*(You can say 'Clear my list' to delete them all.)*"

        return {"type": "text", "content": answer}
        
    def handle_clear_notes(self, speak):
        """NEW: Clears all reminders/notes."""
        self.user_data["reminders"] = []
        self._save_data()
        
        answer = "I have completely cleared your notes and reminders list."
        speak(answer)
        return {"type": "text", "content": answer}
        
    def handle_set_calendar_event(self, query: str, speak):
        """NEW: Adds an event to the mobile calendar via a structured command."""
        extracted_data = self._extract_calendar_event(query)

        title = extracted_data["title"]
        start_time = extracted_data["start_time"]
        end_time = extracted_data["end_time"]
        all_day = extracted_data["all_day"]
        description = extracted_data["description"] or "Set by Senorita Assistant."

        if not title or not start_time or not end_time:
            answer = "I'm sorry, I couldn't figure out the title and timing for that event. Could you be more specific?"
            speak(answer)
            return {"type": "text", "content": answer}
        
        answer = f"I've prepared a calendar event titled **{title}** starting at **{start_time}**. The mobile app will now ask you to confirm and add it."
        speak(answer)
        
        return {
            "type": "add_calendar_event",
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "all_day": all_day,
            "text_response": answer
        }


    def handle_mobile_control(self, intent: str, slots: dict, speak):
        """
        Generates structured JSON for mobile actions (toggle_hardware, open_mobile_app, change_volume).
        """
        if intent == "toggle_hardware":
            device = slots["device"]
            state = slots["state"]
            
            response_text = f"Requesting the app to turn **{state}** the **{device}**."
            speak(response_text)
            
            return {
                "type": "hardware_toggle", 
                "device": device, 
                "state": state,
                "text_response": response_text
            }
        
        elif intent == "change_volume":
            state = slots["state"]
            
            if state in ["up", "down", "max", "min"]:
                response_text = f"Requesting the app to adjust the volume to **{state}**."
            else:
                response_text = "I'm not sure how to adjust the volume that way."
                speak(response_text)
                return {"type": "text", "content": response_text}
                
            speak(response_text)
            
            return {
                "type": "hardware_toggle", 
                "device": "volume", 
                "state": state,
                "text_response": response_text
            }
            
        elif intent == "open_mobile_app":
            app_name = slots["app_name"]
            
            response_text = f"Requesting the app to open **{app_name.title()}**."
            speak(response_text)
            
            return {
                "type": "open_mobile_app",
                "app_name": app_name.title(),
                "text_response": response_text
            }
        
        return {"type": "text", "content": "Mobile control command recognized but not processed."}

    def handle_get_directions(self, query: str, speak):
        """Generates structured response for opening Google Maps for a search query."""
        if not query:
            answer = "Where would you like to go? Tell me a destination or a place, like 'nearest coffee shop'."
            speak(answer)
            return {"type": "text", "content": answer}

        query_encoded = query.strip()
        
        answer = f"Opening Google Maps now to search for **{query_encoded.title()}**."
        speak(answer)
        
        return {
            "type": "maps_search",
            "query": query_encoded,
            "text_response": answer
        }
        
    def get_user_name(self):
        return self.user_data.get('name', 'friend')


    def handle_send_message(self, message: str, contact_name: str, speak, platform=None):
        """Handles sending a message to a contact through different platforms.
        
        Args:
            message (str): The message content to send
            contact_name (str): Name of the contact
            speak (function): Callback function for speech output
            platform (str, optional): The messaging platform to use (whatsapp, messenger, etc.)
            
        Returns:
            dict: A structured response with message details
            message: The message content to send
            contact_name: Name of the contact
            speak: Callback function for speech output
            platform: Optional platform (whatsapp, messenger, etc.)
        """
        try:
            # Clean up the message (remove any trailing punctuation)
            message = message.rstrip(' .,!?;:')
            
            # If platform is None, default to SMS
            platform = platform.lower() if platform else 'sms'
            
            response = {
                "type": "send_message",
                "contact_name": contact_name,
                "message": message,
                "platform": platform,
                "text_response": f"Sending message to {contact_name} on {platform}."
            }
            return response
        except Exception as e:
            error_msg = f"Error preparing to send message: {e}"
            print(error_msg, file=sys.stderr)
            return {
                "type": "text",
                "content": "I couldn't prepare the message to send."
            }

    def handle(self, intent: str, slots: dict, speak):
        
        current_query = None 
        answer = None
        local_intent = intent 

        if local_intent in ["open_app", "time", "time_in_location", "set_name", "recall_name", "greet", "set_reminder", "recall_notes", "get_directions", "toggle_hardware", "open_mobile_app", "change_volume", "set_calendar_event", "clear_notes"]:
            self.conversation_history = [] 
        
        if local_intent == "wake_word":
            user_name = self.user_data.get("name", "there")
            answer = f"Yes, {user_name}? How can I help you?"
            speak(answer)
            return {"type": "text", "content": answer}
        
        if self.user_data["waiting_for_platform"] and "query" in slots:
            user_input = slots["query"].lower().strip()
            platform_name = user_input.split()[0]
            if "youtube" in user_input or "yt" in user_input:
                platform_name = "youtube"
            elif "spotify" in user_input:
                platform_name = "spotify"
            elif "jiosaavn" in user_input or "saavn" in user_input:
                platform_name = "jiosaavn"
            
            media_query = self.user_data["waiting_for_platform"]
            self.user_data["waiting_for_platform"] = None 

            return self._open_search_link(platform_name, media_query, speak)
        
        if local_intent == "media_request":
            query = slots.get("query", "")
            result = self._check_for_immediate_platform_and_launch(query, speak)
            if result:
                return result 
            
            if any(term in query.lower() for term in ["image", "picture", "photo", "show me"]):
                return self.handle_image_request(query, speak)

            return self.handle("play_music", {"slot0": query}, speak)


        try:
            if local_intent in ["toggle_hardware", "open_mobile_app", "change_volume"]:
                return self.handle_mobile_control(local_intent, slots, speak)
            
            elif local_intent in ["can_play_music", "can_play_video", "play_music", "play_video"]:
                query = slots.get("slot0")
                media_type = "music or a song" if local_intent in ["can_play_music", "play_music"] else "video or a clip"
                
                if query:
                    result = self._check_for_immediate_platform_and_launch(query, speak)
                    if result:
                        return result

                    self.user_data["waiting_for_platform"] = query
                    answer = f"I can play **{query}**! On which platform would you like me to search? For example, tell me 'YouTube' or 'Spotify'."
                else:
                    self.user_data["waiting_for_platform"] = "generic media"
                    answer = f"I can definitely play {media_type}! What would you like to hear/watch, and on which platform (like YouTube or Spotify)?"
                    
                speak(answer)
                return {"type": "text", "content": answer}

            elif local_intent == "set_reminder":
                query = slots.get("query")
                return self.handle_set_reminder(query, speak)
            
            elif local_intent == "set_calendar_event":
                query = slots.get("query")
                return self.handle_set_calendar_event(query, speak)
            
            elif local_intent == "recall_notes":
                return self.handle_recall_notes(speak)
            
            elif local_intent == "clear_notes": 
                return self.handle_clear_notes(speak)
            
            elif local_intent == "get_directions":
                query = slots.get("query")
                return self.handle_get_directions(query, speak) 
            
            elif local_intent == "set_name":
                name = slots.get("name").strip()
                if name:
                    clean_name = name.replace('*', '') 
                    self.user_data["name"] = clean_name
                    self._save_data()
                    answer = f"Got it! I will remember you as {clean_name}."
                else:
                    answer = "I didn't quite catch your name."
                speak(answer)
                return {"type": "text", "content": answer}
            
            elif local_intent == "get_weather":
                city = slots.get("location")
                if city:
                    self._get_weather(city, speak)
                    answer = f"Fetching weather for {city}... (Check speaker output for details)"
                else:
                    answer = "Which city would you like the weather for?"
                    speak(answer)
                return {"type": "text", "content": answer}
                
            elif local_intent == "get_news":
                topic = slots.get("topic")
                self._get_news(topic, speak)
                answer = f"Fetching news for {topic}... (Check speaker output for details)"
                return {"type": "text", "content": answer}
            
            elif local_intent == "get_apod":
                self._get_nasa_apod(speak)
                answer = "Fetching NASA Picture of the Day... (Check speaker output for details)"
                return {"type": "text", "content": answer}
            
            elif local_intent == "get_trivia":
                self._get_trivia(speak)
                answer = "Fetching trivia question... (Check speaker output for details)"
                return {"type": "text", "content": answer}

            elif local_intent == "time_in_location":
                location_raw = slots.get("location")
                tz_name = self._map_location_to_timezone(location_raw)

                if tz_name:
                    tz = pytz.timezone(tz_name)
                    location_time = datetime.now(tz).strftime("%I:%M %p")
                    answer = f"The time in {location_raw.title()} is {location_time}"
                    speak(answer)
                else:
                    speak(f"I don't recognize the location '{location_raw}'. I can search for it instead.")
                    current_query = f"what is the current time in {location_raw}"
                    answer = self._call_gemini_api(current_query, self.conversation_history)
                
                return {"type": "text", "content": answer}

            elif local_intent == "recall_name":
                user_name = self.user_data.get("name")
                if user_name:
                    answer = f"Your name is {user_name.replace('*', '')}."
                else:
                    answer = "I don't currently have your name stored. You can tell me by saying, 'My name is [your name]'."
                speak(answer)
                return {"type": "text", "content": answer}
            
            elif local_intent == "time":
                # FIX: Set timezone to Asia/Kolkata (IST)
                kolkata_tz = pytz.timezone('Asia/Kolkata')
                now_ist = datetime.now(kolkata_tz).strftime("%I:%M %p %Z")
                answer = f"The current time in India is {now_ist}"
                speak(answer)
                return {"type": "text", "content": answer}

            elif local_intent == "send_message":
                # Extract slots from the parsed command
                message = slots.get("message")
                contact = slots.get("contact")
                platform = slots.get("platform")
                
                if not message or not contact:
                    answer = "Please specify both a message and a contact name."
                    speak(answer)
                    return {
                        "type": "text",
                        "content": answer
                    }
                
                # Clear conversation history to prevent Gemini from overriding our response
                self.conversation_history = []
                return self.handle_send_message(message, contact, speak, platform=platform)              

            elif local_intent == "open_app":
                app = slots.get("slot0", "").strip()
                return self.open_app(app, speak)
            
            elif local_intent == "how_are_you":
                current_query = "The user just said they are doing good/fine/well. Respond with a short, human-like acknowledgment (e.g., 'That's great!') and then ask how their day is going or what they are up to. Do not mention being an AI or a model."
                answer = self._call_gemini_api(current_query, self.conversation_history)
            
            elif local_intent == "greet":
                user_name = self.user_data.get("name", "there")
                greetings = [
                    f"Hey {user_name}! What's up? I'm here to help.",
                    f"Hello {user_name}! How can I assist you today?",
                    f"Hi {user_name}. Good to hear from you!",
                    f"What's on your mind today, {user_name}?"
                ]
                answer = random.choice(greetings)
            
            elif local_intent == "search":
                query = slots.get("query")
                if query:
                    current_query = query
                    
                    if self._extract_and_save_personal_info(query, speak):
                        self.conversation_history = []
                        answer = "Personal info saved."
                    else:
                        speak("Let me quickly look that up for you...")
                        answer = self._call_gemini_api(query, self.conversation_history)
                else:
                    answer = "I need a query to search for."

            else:
                fallback_query = slots.get("query", "")
                
                if fallback_query:
                    current_query = fallback_query
                    
                    if self._extract_and_save_personal_info(fallback_query, speak):
                        self.conversation_history = []
                        answer = "Personal info saved."
                    else:
                        speak("Hmm, I'm not sure what you mean, but let me try searching for it anyway.")
                        answer = self._call_gemini_api(fallback_query, self.conversation_history)
                else:
                    answer = "Sorry, I didn't recognize that command. Try 'open chrome' or 'what's the time'."
                    
            if answer:
                if local_intent in ["how_are_you", "greet", "search"] or answer in ["Personal info saved.", "I need a query to search for."]:
                    speak(answer)
                
                if current_query:
                    self.conversation_history.append({"role": "user", "parts": [{"text": current_query}]})
                    self.conversation_history.append({"role": "model", "parts": [{"text": answer}]})
                    
                    MAX_HISTORY_LENGTH = 10 
                    if len(self.conversation_history) > MAX_HISTORY_LENGTH:
                        self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH:]
                
                self._update_conversation_context(current_query or "", "text", answer)
            
            return {"type": "text", "content": answer} if answer else {"type": "text", "content": "Command processed."}

        except Exception as e:
            error_msg = f"An unexpected error occurred while executing the '{local_intent}' command. Check server logs."
            print(f"Action Execution Error for '{local_intent}': {e}", file=sys.stderr)
            speak(error_msg)
            return {"type": "text", "content": error_msg}