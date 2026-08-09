# command_parser.py
import re


class CommandParser:
    def __init__(self):
        self.patterns = [

            # =========================================================
            # 0. WAKE WORD
            # =========================================================
            (
                "wake_word",
                re.compile(
                    r"^(hey baby|hey babe|hey senorita)",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 1. PERSONALIZATION
            # =========================================================
            (
                "set_name",
                re.compile(
                    r"\b(?:my name is|i am) (.+)",
                    re.IGNORECASE
                )
            ),

            (
                "recall_name",
                re.compile(
                    r"\bwhat(?:'s| is) my name\b",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 2. TIME & LOCATION
            # =========================================================
            (
                "time_in_location",
                re.compile(
                    r"^(?:"
                    r"what(?:'s| is) the time in (.+)"
                    r"|what time is it in (.+)"
                    r"|time in (.+)"
                    r")$",
                    re.IGNORECASE
                )
            ),

            (
                "time",
                re.compile(
                    r"^(?:"
                    r"what(?:'s| is) the time(?: now)?"
                    r"|what time is it(?: now)?"
                    r"|tell me the time"
                    r"|current time"
                    r"|time now"
                    r")$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 3. CONVERSATION
            # =========================================================
            (
                "how_are_you",
                re.compile(
                    r"\b(how are you|how do you do|how's it going)\b",
                    re.IGNORECASE
                )
            ),

            (
                "greet",
                re.compile(
                    r"^(hi|hello|hey|good (morning|afternoon|evening))",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 4. DIRECT ACTIONS
            # =========================================================
            (
                "open_app",
                re.compile(
                    r"\bopen (.+)",
                    re.IGNORECASE
                )
            ),

            (
                "get_weather",
                re.compile(
                    r"^(?:"
                    r"(?:what's|what is|how is) the weather "
                    r"(?:like )?(?:in |at )?(.+)"
                    r"|weather (?:in |at )?(.+)"
                    r"|(.+?) weather"
                    r")$",
                    re.IGNORECASE
                )
            ),

            (
                "get_news",
                re.compile(
                    r"\b(?:what's|what are|tell me) the news "
                    r"(?:about |on )?(.+)?",
                    re.IGNORECASE
                )
            ),

            (
                "get_apod",
                re.compile(
                    r"\b(?:what's|show me) the nasa picture of the day\b",
                    re.IGNORECASE
                )
            ),

            (
                "get_trivia",
                re.compile(
                    r"\b(?:tell me|give me) a trivia(?: question)?\b",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 5. CALLING
            # =========================================================
            (
                "make_call",
                re.compile(
                    r"^(?:call|make\s+a?\s*call\s+to\s+)"
                    r"([a-zA-Z0-9\s]+?)$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 6. MESSAGING
            # =========================================================
            (
                "send_message",
                re.compile(
                    r"^(?:(?:send|text|message)"
                    r"(?:\s+(?:a |an |the |me )?)?"
                    r"(.+?)(?:\s+to\s+)"
                    r"([a-zA-Z0-9\s]+?)"
                    r"(?:\s+(?:on |in )?"
                    r"(whatsapp|messenger|telegram|signal))?"
                    r"|(?:send|text|message)\s+"
                    r"([a-zA-Z0-9\s]+?)\s+"
                    r"(.+?)"
                    r"(?:\s+(?:on |in )?"
                    r"(whatsapp|messenger|telegram|signal))?"
                    r")(?:\s+please)?[.?!]?$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 7. MOBILE HARDWARE
            # =========================================================
            (
                "toggle_hardware",
                re.compile(
                    r"^(?:"
                    r"(?:turn|switch|toggle)\s+"
                    r"(on|off)\s+(?:the\s+)?"
                    r"(torch|flashlight|wifi|bluetooth|data)"
                    r"|(?:turn|switch)\s+(?:the\s+)?"
                    r"(torch|flashlight|wifi|bluetooth|data)"
                    r"\s+(on|off)"
                    r"|(?:enable|disable)\s+(?:the\s+)?"
                    r"(torch|flashlight|wifi|bluetooth|data)"
                    r"|(?:torch|flashlight|wifi|bluetooth|data)"
                    r"\s+(on|off)"
                    r")$",
                    re.IGNORECASE
                )
            ),

            (
                "change_volume",
                re.compile(
                    r"\b(?:turn )?volume "
                    r"(up|down|max|min)\b",
                    re.IGNORECASE
                )
            ),

            (
                "open_mobile_app",
                re.compile(
                    r"\bopen\s+(.+)",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 8. CALENDAR
            # =========================================================
            (
                "set_calendar_event",
                re.compile(
                    r"^(?:"
                    r"(?:please\s+)?schedule\s+(?:a\s+|an\s+)?(.+)"
                    r"|(?:please\s+)?create\s+(?:a\s+|an\s+)?(.+)"
                    r"|(?:please\s+)?set\s+up\s+(?:a\s+|an\s+)?(.+)"
                    r")$",
                    re.IGNORECASE
                )
            ),

            (
                "get_calendar_events",
                re.compile(
                    r"^(?:"
                    r"show\s+(?:me\s+)?my\s+calendar"
                    r"|what\s+(?:is|are)\s+on\s+my\s+calendar"
                    r"|what\s+events?\s+do\s+i\s+have"
                    r"(?:\s+(today|tomorrow))?"
                    r"|what\s+is\s+my\s+schedule"
                    r"(?:\s+(today|tomorrow))?"
                    r"|show\s+my\s+(?:schedule|events?)"
                    r"(?:\s+(today|tomorrow))?"
                    r"|what(?:'s|\s+is)\s+my\s+"
                    r"(?:schedule|calendar)"
                    r"(?:\s+(today|tomorrow))?"
                    r")$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 9. REMINDERS
            # =========================================================
            (
                "set_reminder",
                re.compile(
                    r"\b(?:remember to|take a note(?: to)?|"
                    r"add to my list|note|remind me to)"
                    r"(?: that)? (.+)",
                    re.IGNORECASE
                )
            ),

            (
                "recall_notes",
                re.compile(
                    r"^(?:"
                    r"my reminders"
                    r"|show me my reminders"
                    r"|what is in my notes"
                    r"|what do i need to remember"
                    r"|read my list"
                    r"|what is on my list"
                    r"|what's on my list"
                    r")$",
                    re.IGNORECASE
                )
            ),

            (
                "clear_notes",
                re.compile(
                    r"\b(?:clear|delete|remove) my "
                    r"(?:notes|reminders|list)\b",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 10. DIRECTIONS
            # =========================================================
            (
                "get_directions",
                re.compile(
                    r"^(?:"
                    r"directions?\s+(?:to|for)\s+(.+)"
                    r"|get\s+directions?\s+(?:to|for)\s+(.+)"
                    r"|show\s+(?:me\s+)?directions?\s+(?:to|for)\s+(.+)"
                    r"|navigate\s+(?:to\s+)?(.+)"
                    r"|take\s+me\s+(?:to|towards)\s+(.+)"
                    r"|how\s+do\s+i\s+get\s+to\s+(.+)"
                    r")$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 11. MEDIA
            # =========================================================

            # ---------------------------------------------------------
            # VIDEO
            #
            # Supported:
            # watch nature video
            # watch Avengers trailer
            # play nature video
            # play video of nature
            # play Avengers trailer
            # play Python tutorial on YouTube
            # ---------------------------------------------------------
            (
                "play_video",
                re.compile(
                    r"^(?:"
                    r"watch\s+(.+?)"
                    r"(?:\s+(?:video|videos|trailer|movie|film|clip|episode))?"
                    r"|play\s+(?:a\s+|the\s+)?"
                    r"(?:video|videos|trailer|movie|film|clip|episode)"
                    r"(?:\s+(?:of|about))?\s+(.+?)"
                    r"|play\s+(.+?)\s+"
                    r"(?:video|videos|trailer|movie|film|clip|episode)"
                    r")"
                    r"(?:\s+(?:on|in|using)\s+(youtube|yt))?$",
                    re.IGNORECASE
                )
            ),

            # ---------------------------------------------------------
            # MUSIC
            #
            # Supported:
            # play Shape of You
            # play Shape of You song
            # play Ed Sheeran Shape of You
            # listen to Shape of You
            # play Shape of You on Spotify
            # ---------------------------------------------------------
            (
                "play_music",
                re.compile(
                    r"^(?:"
                    r"play\s+"
                    r"|listen\s+to\s+"
                    r"|listen\s+"
                    r"|start\s+"
                    r")"
                    r"(?:the\s+|a\s+|some\s+)?"
                    r"(?:song\s+|music\s+|track\s+)?"
                    r"(.+?)"
                    r"(?:\s+(?:on|in|using)\s+"
                    r"(spotify|jiosaavn|saavn))?$",
                    re.IGNORECASE
                )
            ),

            # =========================================================
            # 12. GENERAL SEARCH
            # =========================================================
            (
                "search",
                re.compile(
                    r"^(?:what is|what's|who is|who's|"
                    r"tell me about|how to|where is|when did|"
                    r"why is)?\s*(.+)",
                    re.IGNORECASE
                )
            )
        ]

    def parse(self, text: str):
        text = (text or "").strip()

        if not text:
            return "unknown", {"query": ""}

        for intent, pattern in self.patterns:

            m = pattern.search(text)

            if not m:
                continue

            slots = {}

            # =====================================================
            # WAKE WORD
            # =====================================================
            if intent == "wake_word":

                remaining_text = text[m.end():].strip()

                if remaining_text:
                    return self.parse(remaining_text)

                return "wake_word", {
                    "phrase": m.group(1)
                }

            # =====================================================
            # MEDIA
            # =====================================================
            elif intent in ["play_music", "play_video"]:

                query = ""
                platform = None

                # -------------------------
                # MUSIC
                # -------------------------
                if intent == "play_music":

                    query = m.group(1) or ""

                    if m.lastindex and m.lastindex >= 2:
                        platform_value = m.group(2)

                        if platform_value:
                            platform = platform_value.lower().strip()

                # -------------------------
                # VIDEO
                # -------------------------
                else:

                    # The video regex has several possible query groups.
                    # Find the first non-platform capture.
                    for index, group in enumerate(m.groups(), start=1):

                        if not group:
                            continue

                        value = group.strip()

                        if value.lower() in [
                            "youtube",
                            "yt"
                        ]:
                            platform = value.lower()
                            continue

                        if not query:
                            query = value

                query = query.strip()

                # Remove media words accidentally included in query.
                query = re.sub(
                    r"\s+(?:song|music|track|video|videos|"
                    r"trailer|movie|film|clip|episode)$",
                    "",
                    query,
                    flags=re.IGNORECASE
                ).strip()

                # Normalize platform names.
                if platform == "yt":
                    platform = "youtube"

                elif platform == "saavn":
                    platform = "jiosaavn"

                slots["slot0"] = query
                slots["platform"] = platform

                print(
                    f"🎵/🎬 MEDIA PARSER: "
                    f"{intent} | query={query} | platform={platform}"
                )

            # =====================================================
            # MEDIA REQUEST
            # =====================================================
            elif intent == "media_request":

                query = m.group(1)

                if query:
                    slots["query"] = query.strip()
                else:
                    slots["query"] = ""

            # =====================================================
            # SEARCH
            # =====================================================
            elif intent == "search":

                query = m.group(1)

                if query:
                    slots["query"] = query.strip()
                else:
                    slots["query"] = ""

            # =====================================================
            # REMINDER
            # =====================================================
            elif intent == "set_reminder":

                query = m.group(1)

                if query:
                    slots["query"] = query.strip()

            # =====================================================
            # CALENDAR EVENT
            # =====================================================
            elif intent == "set_calendar_event":

                query = next(
                    (
                        group
                        for group in m.groups()
                        if group
                    ),
                    None
                )

                if query:
                    slots["query"] = query.strip()

            # =====================================================
            # CALENDAR LOOKUP
            # =====================================================
            elif intent == "get_calendar_events":

                period = next(
                    (
                        group
                        for group in m.groups()
                        if group
                    ),
                    None
                )

                slots["period"] = (
                    period.lower()
                    if period
                    else "today"
                )

            # =====================================================
            # DIRECTIONS
            # =====================================================
            elif intent == "get_directions":

                query = next(
                    (
                        group
                        for group in m.groups()
                        if group
                    ),
                    None
                )

                if query:
                    slots["query"] = query.strip()

            # =====================================================
            # NAME
            # =====================================================
            elif intent == "set_name":

                if m.group(1):
                    slots["name"] = m.group(1).strip()

            # =====================================================
            # TIME IN LOCATION
            # =====================================================
            elif intent == "time_in_location":

                location = (
                    m.group(1)
                    or m.group(2)
                    or m.group(3)
                )

                if location:
                    slots["location"] = location.strip()

            # =====================================================
            # WEATHER
            # =====================================================
            elif intent == "get_weather":

                location = (
                    m.group(1)
                    or m.group(2)
                    or m.group(3)
                )

                if location:
                    slots["location"] = location.strip()

            # =====================================================
            # NEWS
            # =====================================================
            elif intent == "get_news":

                topic = m.group(1)

                slots["topic"] = (
                    topic.strip()
                    if topic
                    else ""
                )

            # =====================================================
            # HARDWARE
            # =====================================================
            elif intent == "toggle_hardware":

                groups = [
                    group.lower()
                    if isinstance(group, str)
                    else None
                    for group in m.groups()
                ]

                # turn on wifi
                if groups[0] in ["on", "off"]:

                    slots["state"] = groups[0]
                    slots["device"] = groups[1]

                # turn wifi on
                elif (
                    len(groups) >= 3
                    and groups[1] in [
                        "torch",
                        "flashlight",
                        "wifi",
                        "bluetooth",
                        "data"
                    ]
                ):

                    slots["device"] = groups[1]
                    slots["state"] = groups[2]

                # enable wifi / disable wifi
                elif groups[1] in [
                    "torch",
                    "flashlight",
                    "wifi",
                    "bluetooth",
                    "data"
                ]:

                    slots["device"] = groups[1]

                    if groups[0] == "enable":
                        slots["state"] = "on"

                    elif groups[0] == "disable":
                        slots["state"] = "off"

                # wifi on
                elif groups[0] in [
                    "torch",
                    "flashlight",
                    "wifi",
                    "bluetooth",
                    "data"
                ]:

                    slots["device"] = groups[0]
                    slots["state"] = groups[1]

            # =====================================================
            # VOLUME
            # =====================================================
            elif intent == "change_volume":

                slots["state"] = m.group(1).lower()

            # =====================================================
            # MOBILE APP
            # =====================================================
            elif intent == "open_mobile_app":

                if m.group(1):
                    slots["app_name"] = m.group(1).strip().lower()

            # =====================================================
            # DESKTOP APP
            # =====================================================
            elif intent == "open_app":

                if m.group(1):
                    slots["slot0"] = m.group(1).strip()

            # =====================================================
            # CALL
            # =====================================================
            elif intent == "make_call":

                if m.group(1):

                    contact = m.group(1).strip()

                    print(
                        f"Calling contact: {contact}"
                    )

                    slots["contact"] = contact
                    slots["name"] = contact

            # =====================================================
            # MESSAGING
            # =====================================================
            elif intent == "send_message":

                # send hello to John on WhatsApp
                if m.group(1) and m.group(2):

                    slots["message"] = m.group(1).strip()
                    slots["contact"] = m.group(2).strip()

                    slots["platform"] = (
                        m.group(3).lower()
                        if m.group(3)
                        else "sms"
                    )

                # text John hello on WhatsApp
                elif m.group(4) and m.group(5):

                    slots["contact"] = m.group(4).strip()
                    slots["message"] = m.group(5).strip()

                    slots["platform"] = (
                        m.group(6).lower()
                        if m.group(6)
                        else "sms"
                    )

            return intent, slots

        return "unknown", {
            "query": text
        }