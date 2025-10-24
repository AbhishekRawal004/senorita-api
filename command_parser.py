# command_parser.py
import re

class CommandParser:
    def __init__(self):
        self.patterns = [
            # 0. WAKE WORD (New)
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
            
            # 5. MOBILE HARDWARE/APP CONTROL (Updated)
            # Toggles like Wi-Fi, Torch
            ("toggle_hardware", re.compile(r"\bturn (on|off) (torch|flashlight|wifi|bluetooth|data)\b", re.IGNORECASE)),
            # NEW: Volume control
            ("change_volume", re.compile(r"\b(?:turn )?volume (up|down|max|min)\b", re.IGNORECASE)),
            ("open_mobile_app", re.compile(r"\bopen (camera|settings|gallery|photos|(.+))", re.IGNORECASE)),
            
            # --- REMINDERS, CALENDAR & NOTES (Updated) ---
            # NEW: Calendar event
            ("set_calendar_event", re.compile(r"\b(?:schedule|set up|create) a (?:meeting|event|reminder for my calendar) (.+)", re.IGNORECASE)),
            # Simple list reminder
            ("set_reminder", re.compile(r"\b(?:remember to|take a note|add to my list|note|remind me to)(?: that)? (.+)", re.IGNORECASE)),
            ("recall_notes", re.compile(r"\b(?:what is in my notes|what do i need to remember|show me my reminders|read my list|what's on my list)\b", re.IGNORECASE)),
            # NEW: Clear notes command
            ("clear_notes", re.compile(r"\b(?:clear|delete|remove) my (?:notes|reminders|list)\b", re.IGNORECASE)),
            
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
                    remaining_text = text[m.end():].strip()
                    if remaining_text:
                        return self.parse(remaining_text)
                    
                    return "wake_word", {"phrase": m.group(1)}
                
                slots = {}
                # Get the first captured group as the main slot/query
                g = m.group(1) if m.groups() and m.group(1) is not None else (m.group(2) if m.groups() and len(m.groups()) > 1 and m.group(2) is not None else None)

                # Set the main query slot for media, directions, reminders, and general search
                if intent in ["media_request", "search", "set_reminder", "set_calendar_event", "get_directions"]:
                    slots["query"] = m.group(m.lastindex) if m.lastindex else g
                # Map other specific slots
                elif intent == "set_name":
                    slots["name"] = m.group(1)
                elif intent in ["time_in_location", "get_weather"]:
                    slots["location"] = m.group(1)
                elif intent == "get_news":
                    slots["topic"] = m.group(1)
                elif intent == "toggle_hardware":
                    slots["state"] = m.group(1).lower()
                    slots["device"] = m.group(2).lower()
                elif intent == "change_volume":
                    slots["state"] = m.group(1).lower()
                elif intent == "open_mobile_app":
                    # Logic to capture the app name, even if it matches the general (.+) group
                    app_match = re.search(r"\bopen (camera|settings|gallery|photos|(.+))", text, re.IGNORECASE)
                    if app_match:
                         # Prioritize the named group (1) or the catch-all group (2)
                         app_name = next(g for g in reversed(app_match.groups()) if g is not None)
                         slots["app_name"] = app_name
                    
                return intent, slots
        return "unknown", {"query": text}