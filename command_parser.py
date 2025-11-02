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
            ("how_are_you", re.compile(r"\b(how are you|how do you do|how's it going)\\b", re.IGNORECASE)),
            ("greet", re.compile(r"^(hi|hello|hey|good (morning|afternoon|evening))", re.IGNORECASE)),

            # 4. DIRECT ACTIONS (Apps, Weather, News, Reminders, Maps)
            ("open_app", re.compile(r"\bopen (.+)", re.IGNORECASE)),
            ("get_weather", re.compile(r"\b(?:what's|what is|how is) the weather (?:like )?(?:in |at )?(.+)", re.IGNORECASE)),
            ("get_news", re.compile(r"\b(?:what's|what are|tell me) the news (?:about |on )?(.+)?", re.IGNORECASE)),
            ("get_apod", re.compile(r"\b(?:what's|show me) the nasa picture of the day\b", re.IGNORECASE)),
            ("get_trivia", re.compile(r"\b(?:tell me|give me) a trivia(?: question)?\b", re.IGNORECASE)),
            
            # 5. MESSAGING - Made more specific and moved before search
            ("send_message", re.compile(r"^(?:(?:send|text|message)(?:\s+(?:a |an |the |me )?)?(.+?)(?:\s+to\s+)([a-zA-Z0-9\s]+?)(?:\s+(?:on |in )?(whatsapp|messenger|telegram|signal))?|(?:send|text|message)\s+([a-zA-Z0-9\s]+?)\s+(.+?)(?:\s+(?:on |in )?(whatsapp|messenger|telegram|signal))?)(?:\s+please)?[.?!]?$", re.IGNORECASE)),
            
            # 6. MOBILE HARDWARE/APP CONTROL (Updated)
            ("toggle_hardware", re.compile(r"\bturn (on|off) (torch|flashlight|wifi|bluetooth|data)\b", re.IGNORECASE)),
            ("change_volume", re.compile(r"\b(?:turn )?volume (up|down|max|min)\b", re.IGNORECASE)),
            ("open_mobile_app", re.compile(r"\bopen\s+(.+)", re.IGNORECASE)), 
            
            # --- REMINDERS, CALENDAR & NOTES (Updated) ---
            ("set_calendar_event", re.compile(r"\b(?:schedule|set up|create) a (?:meeting|event|reminder for my calendar) (.+)", re.IGNORECASE)),
            ("set_reminder", re.compile(r"\b(?:remember to|take a note|add to my list|note|remind me to)(?: that)? (.+)", re.IGNORECASE)),
            ("recall_notes", re.compile(r"\b(?:what is in my notes|what do i need to remember|show me my reminders|read my list|what's on my list)\b", re.IGNORECASE)),
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
                if intent == "wake_word":
                    remaining_text = text[m.end():].strip()
                    if remaining_text:
                        return self.parse(remaining_text)
                    
                    return "wake_word", {"phrase": m.group(1)}
                
                slots = {}
                if intent in ["media_request", "search", "set_reminder", "set_calendar_event", "get_directions"]:
                    slots["query"] = m.group(1) 
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
                    slots["app_name"] = m.group(1).lower() 
                elif intent == "open_app":
                    slots["slot0"] = m.group(1)
                elif intent == "send_message":
                    # Handle both formats:
                    # 1. "send [message] to [contact] [on platform]" (groups 1, 2, 3)
                    # 2. "send [contact] [message] [on platform]" (groups 4, 5, 6)
                    if m.group(1) and m.group(2):
                        slots["message"] = m.group(1).strip()
                        slots["contact"] = m.group(2).strip()
                        slots["platform"] = m.group(3).lower() if m.group(3) else None
                    elif m.group(4) and m.group(5):
                        slots["contact"] = m.group(4).strip()
                        slots["message"] = m.group(5).strip()
                        slots["platform"] = m.group(6).lower() if m.group(6) else None
                    
                return intent, slots
        return "unknown", {"query": text}