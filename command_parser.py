# command_parser.py
import re

class CommandParser:
    def __init__(self):
        self.patterns = [
            # 0. WAKE WORD (New)
            # This is a simple check; a real app needs a dedicated wake word engine
            ("wake_word", re.compile(r"^(hey baby|hey babe|hey senorita)", re.IGNORECASE)),
            
            # 1. PERSONALIZATION
            ("set_name", re.compile(r"\b(?:my name is|i am) (.+)", re.IGNORECASE)),
            ("recall_name", re.compile(r"\bwhat(?:'s| is) my name\b", re.IGNORECASE)),
            
            # 2. TIME & LOCATION
            ("time_in_location", re.compile(r"\bwhat(?:'s| is) the time in (.+)", re.IGNORECASE)),
            ("time", re.compile(r"\bwhat(?:'s| is) the time( now)?\b", re.IGNORECASE)),

            # 3. CONVERSATION
            ("how_are_you", re.compile(r"\b(how are you|how do you do|how's it going)\b", re.IGNORECASE)),
            ("greet", re.compile(r"^(hi|hello|hey|good (morning|afternoon|evening))", re.IGNORECASE)),

            # 4. DIRECT ACTIONS (Apps, Weather, News, Reminders, Maps)
            ("open_app", re.compile(r"\bopen (.+)", re.IGNORECASE)),
            ("get_weather", re.compile(r"\b(?:what's|what is|how is) the weather (?:like )?(?:in |at )?(.+)", re.IGNORECASE)),
            ("get_news", re.compile(r"\b(?:what's|what are|tell me) the news (?:about |on )?(.+)?", re.IGNORECASE)),
            ("get_apod", re.compile(r"\b(?:what's|show me) the nasa picture of the day\b", re.IGNORECASE)),
            ("get_trivia", re.compile(r"\b(?:tell me|give me) a trivia(?: question)?\b", re.IGNORECASE)),
            
            # 5. MOBILE HARDWARE/APP CONTROL (New)
            ("toggle_hardware", re.compile(r"\bturn (on|off) (torch|flashlight|wifi|bluetooth|data)\b", re.IGNORECASE)),
            ("open_mobile_app", re.compile(r"\bopen (camera|settings|gallery|photos|(.+))", re.IGNORECASE)),
            
            # --- REMINDERS & NOTES ---
            # This pattern captures the full reminder query
            ("set_reminder", re.compile(r"\b(?:remember to|take a note|add to my list|note|remind me to)(?: that)? (.+)", re.IGNORECASE)),
            ("recall_notes", re.compile(r"\b(?:what is in my notes|what do i need to remember|show me my reminders|read my list|what's on my list)\b", re.IGNORECASE)),
            
            # --- DIRECTIONS & MAPS ---
            ("get_directions", re.compile(r"\b(?:show me|get|navigate) directions (?:to |for |me to )?(.+)", re.IGNORECASE)),
            
            # 6. MEDIA INTENTS
            ("media_request", re.compile(r"^(?:show|display|get|give|play|search) (?:me |an |a |picture of |image of |video of |clip of |song of |music of )?(.+)", re.IGNORECASE)),
            
            # 7. GENERAL KNOWLEDGE / LLM FALLBACK (Must be last)
            ("search", re.compile(r"^(?:what is|what's|who is|who's|tell me about|how to|where is|when did|why is)?\s*(.+)", re.IGNORECASE))
        ]

    def parse(self, text: str):
        text = text.strip()
        for intent, pattern in self.patterns:
            m = pattern.search(text)
            if m:
                slots = {}
                # Handle special case for wake word, which might precede another command
                if intent == "wake_word":
                    # Remove the wake word from the start of the text and try to parse again
                    remaining_text = text[m.end():].strip()
                    if remaining_text:
                        return self.parse(remaining_text) # Re-parse remaining text
                    
                    # If only the wake word was spoken, treat it as a special intent
                    return "wake_word", {"phrase": m.group(1)}
                
                slots = {}
                for i, g in enumerate(m.groups()):
                    # Set the main query slot for media, directions, reminders, and general search
                    if intent in ["media_request", "search", "set_reminder", "get_directions"]:
                        slots["query"] = g
                    # Map other specific slots
                    elif intent == "set_name":
                        slots["name"] = g
                    elif intent in ["time_in_location", "get_weather"]:
                        slots["location"] = g
                    elif intent == "get_news":
                        slots["topic"] = g
                    elif intent == "toggle_hardware":
                        slots["state"] = m.group(1).lower()
                        slots["device"] = m.group(2).lower()
                    elif intent == "open_mobile_app":
                        slots["app_name"] = m.group(1).lower()
                    else:
                        slots[f"slot{i}"] = g
                return intent, slots
        return "unknown", {}