"""
Smart command normalization + free knowledge fallback for Baby/Senorita.

This module does NOT replace the existing command parser.
It normalizes natural variations into the forms the existing parser already
understands, and provides a no-key Wikipedia fallback when Gemini is unavailable.
"""

import re
from urllib.parse import quote
import requests


def normalize_command(text: str) -> str:
    """Normalize common natural-language variations without changing intent."""
    if not text:
        return ""

    q = re.sub(r"\s+", " ", text.strip().lower())
    q = re.sub(r"[?!]+$", "", q).strip()

    # Common conversational wrappers.
    q = re.sub(
        r"^(please\s+|can you\s+|could you\s+|would you\s+|will you\s+)+",
        "",
        q,
    )
    q = re.sub(r"^(tell me|tell me about|give me|show me)\s+",
               lambda m: {
                   "tell me": "",
                   "tell me about": "what is ",
                   "give me": "",
                   "show me": "",
               }[m.group(1)] if m.group(1) in {
                   "tell me", "tell me about", "give me", "show me"
               } else "",
               q)

    q = re.sub(r"\bwhat's\b", "what is", q)
    q = re.sub(r"\bwhats\b", "what is", q)
    q = re.sub(r"\bwhere's\b", "where is", q)
    q = re.sub(r"\bwheres\b", "where is", q)
    q = re.sub(r"\bwho's\b", "who is", q)
    q = re.sub(r"\bwhos\b", "who is", q)

        # "where can I find X" -> "where is X"
    m = re.match(r"^where\s+can\s+i\s+find\s+(?:the\s+)?(.+)$", q)
    if m:
        return f"where is the {m.group(1).strip()}"

    # Very common reversed-question forms:
    # "pyramid where"       -> "where is pyramid"
    # "pyramid where is"    -> "where is pyramid"
    # "pyramid located where" -> "where is pyramid"
    m = re.match(r"^(.+?)\s+where\s+is$", q)
    if m:
        return f"where is {m.group(1).strip()}"

    m = re.match(r"^(.+?)\s+where$", q)
    if m:
        return f"where is {m.group(1).strip()}"

    m = re.match(r"^(.+?)\s+located\s+where$", q)
    if m:
        return f"where is {m.group(1).strip()}"

    m = re.match(r"^where\s+(.+?)\s+located$", q)
    if m:
        return f"where is {m.group(1).strip()}"

    # Hardware control variations
    # Normalize natural language into the exact format
    # understood by command_parser.py.

    # Torch / flashlight
    m = re.match(
        r"^(?:turn|switch)\s+(?:on|off)\s+(?:the\s+)?(torch|flashlight)$",
        q
    )
    if m:
        state = "on" if re.search(r"\b(on)\b", q) else "off"
        return f"turn {state} torch"

    m = re.match(
        r"^(?:turn|switch)\s+(?:the\s+)?(torch|flashlight)\s+(on|off)$",
        q
    )
    if m:
        return f"turn {m.group(2)} torch"

    m = re.match(
        r"^(enable|disable)\s+(?:the\s+)?(torch|flashlight)$",
        q
    )
    if m:
        state = "on" if m.group(1) == "enable" else "off"
        return f"turn {state} torch"

    m = re.match(
        r"^(?:torch|flashlight)\s+(on|off)$",
        q
    )
    if m:
        return f"turn {m.group(1)} torch"


    # Wi-Fi / Bluetooth / data
    for device in ["wifi", "bluetooth", "data"]:
        m = re.match(
            rf"^(?:turn|switch)\s+(?:on|off)\s+(?:the\s+)?{device}$",
            q
        )
        if m:
            state = "on" if re.search(r"\bon\b", q) else "off"
            return f"turn {state} {device}"

        m = re.match(
            rf"^(?:turn|switch)\s+(?:the\s+)?{device}\s+(on|off)$",
            q
        )
        if m:
            return f"turn {m.group(1)} {device}"

        m = re.match(
            rf"^(enable|disable)\s+(?:the\s+)?{device}$",
            q
        )
        if m:
            state = "on" if m.group(1) == "enable" else "off"
            return f"turn {state} {device}"

        m = re.match(
            rf"^{device}\s+(on|off)$",
            q
        )
        if m:
            return f"turn {m.group(1)} {device}"


    # Mobile data variations
    m = re.match(
        r"^(?:turn|switch)\s+(?:on|off)\s+(?:the\s+)?mobile\s+data$",
        q
    )
    if m:
        state = "on" if re.search(r"\bon\b", q) else "off"
        return f"turn {state} data"

    m = re.match(
        r"^(?:turn|switch)\s+(?:the\s+)?mobile\s+data\s+(on|off)$",
        q
    )
    if m:
        return f"turn {m.group(1)} data"

    m = re.match(
        r"^(enable|disable)\s+(?:the\s+)?mobile\s+data$",
        q
    )
    if m:
        state = "on" if m.group(1) == "enable" else "off"
        return f"turn {state} data"

    m = re.match(
        r"^mobile\s+data\s+(on|off)$",
        q
    )
    if m:
        return f"turn {m.group(1)} data"


    # Volume control variations
    # Normalize natural language into the existing:
    # "volume up", "volume down", "volume max", "volume min"

    # Increase volume
    if re.match(
        r"^(?:turn\s+the\s+)?volume\s+(?:up|higher|louder)$",
        q
    ):
        return "volume up"

    if re.match(
        r"^(?:increase|raise)\s+(?:the\s+)?volume$",
        q
    ):
        return "volume up"

    if re.match(
        r"^(?:make\s+(?:it|the\s+volume)\s+louder)$",
        q
    ):
        return "volume up"

    if q == "louder":
        return "volume up"


    # Decrease volume
    if re.match(
        r"^(?:turn\s+the\s+)?volume\s+(?:down|lower|quieter)$",
        q
    ):
        return "volume down"

    if re.match(
        r"^(?:decrease|lower)\s+(?:the\s+)?volume$",
        q
    ):
        return "volume down"

    if re.match(
        r"^(?:make\s+(?:it|the\s+volume)\s+quieter)$",
        q
    ):
        return "volume down"

    if q == "quieter":
        return "volume down"


    # Maximum volume
    if re.match(
        r"^(?:set\s+(?:the\s+)?volume\s+(?:to\s+)?(?:max|maximum))$",
        q
    ):
        return "volume max"

    if q in ["maximum volume", "volume maximum"]:
        return "volume max"


    # Minimum volume
    if re.match(
        r"^(?:set\s+(?:the\s+)?volume\s+(?:to\s+)?(?:min|minimum))$",
        q
    ):
        return "volume min"

    if q in ["minimum volume", "volume minimum"]:
        return "volume min"

    # Weather variations:
    # "bangalore weather" / "weather bangalore" -> "weather in bangalore"
    m = re.match(r"^(.+?)\s+weather$", q)
    if m and not q.startswith("weather "):
        return f"weather in {m.group(1).strip()}"

    m = re.match(r"^weather\s+(.+)$", q)
    if m and not q.startswith("weather in "):
        return f"weather in {m.group(1).strip()}"

    # Time variations:
    # "tokyo time" / "time tokyo" -> "what is the time in tokyo"
    m = re.match(r"^(.+?)\s+time$", q)
    if m and not q.startswith(("what is the time", "time in ")):
        return f"what is the time in {m.group(1).strip()}"

    m = re.match(r"^time\s+(.+)$", q)
    if m and not q.startswith(("time in ", "what is the time")):
        return f"what is the time in {m.group(1).strip()}"

    # Open-app variations
    # Normalize natural ways of asking to launch an app.

    # "open up YouTube" -> "open YouTube"
    m = re.match(r"^open\s+up\s+(.+)$", q)
    if m:
        return f"open {m.group(1).strip()}"

    # "launch YouTube" -> "open YouTube"
    m = re.match(r"^launch\s+(.+)$", q)
    if m:
        return f"open {m.group(1).strip()}"

    # "start YouTube" -> "open YouTube"
    m = re.match(r"^start\s+(.+)$", q)
    if m:
        return f"open {m.group(1).strip()}"

    # "youtube open" -> "open youtube"
    m = re.match(r"^(.+?)\s+open$", q)
    if m:
        return f"open {m.group(1).strip()}"

    # Call variations:
    # "john call" -> "call john"
    m = re.match(r"^(.+?)\s+call$", q)
    if m:
        return f"call {m.group(1).strip()}"

    # Small cleanup.
    q = re.sub(r"\s{2,}", " ", q).strip()
    return q


def _wikipedia_search(query: str):
    """Search Wikipedia and return the best page title, or None."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
        "format": "json",
        "utf8": 1,
    }
    headers = {
        "User-Agent": "BabyAssistant/1.0 (personal assistant)"
    }

    response = requests.get(url, params=params, headers=headers, timeout=8)
    response.raise_for_status()

    results = response.json().get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def _wikipedia_summary(title: str):
    """Fetch a concise Wikipedia summary for a page title."""

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + quote(title.replace(" ", "_"), safe="")
    )

    headers = {
        "User-Agent": "BabyAssistant/1.0 (personal assistant)"
    }

    response = requests.get(url, headers=headers, timeout=8)
    response.raise_for_status()

    data = response.json()
    extract = (data.get("extract") or "").strip()

    if not extract:
        return None

    return {
        "title": data.get("title", title),
        "extract": extract,
        "url": data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page"),
    }


def wikipedia_fallback(query: str):
    """
    Return a factual fallback answer when the LLM is unavailable.

    This is intentionally conservative: it only returns a Wikipedia
    summary rather than pretending that Wikipedia answered every possible
    question.
    """
    try:
        clean = re.sub(
            r"^(where is|where are|what is|what are|who is|who was|tell me about)\s+",
            "",
            query.strip().lower(),
        ).strip()

        if not clean:
            return None

        title = _wikipedia_search(clean)
        if not title:
            return None

        return _wikipedia_summary(title)

    except Exception as exc:
        print(f"Wikipedia fallback error: {exc}")
        return None


def answer_from_free_knowledge(query: str):
    """
    Build a short spoken answer from Wikipedia.
    Returns None if no reliable summary is available.
    """
    if re.match(r"^(where is|where are)\s+", query.strip().lower()):
        search_query = query.strip()
    else:
        search_query = query.strip()

    result = wikipedia_fallback(search_query)
    if not result:
        return None

    extract = result["extract"]

    # Keep voice responses reasonably short.
    sentences = re.split(r"(?<=[.!?])\s+", extract)
    short = " ".join(sentences[:3]).strip()

    answer = f"{result['title']}: {short}"

    if result.get("url"):
        return {
            "text": answer,
            "source": "Wikipedia",
            "url": result["url"],
        }

    return {
        "text": answer,
        "source": "Wikipedia",
    }
