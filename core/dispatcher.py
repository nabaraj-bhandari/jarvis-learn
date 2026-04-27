# core/dispatcher.py

import asyncio
from browser.tabs import list_tabs, switch_to_tab, close_tab


def detect_intent(text: str) -> tuple[str, str]:
    """
    Detect what the user wants from raw text.
    Returns (intent, argument).

    This is keyword matching for now — Ollama replaces this later.
    The interface stays identical. That's the point.
    """
    text_lower = text.lower().strip()

    # Browser intents
    if any(word in text_lower for word in ["list tabs", "show tabs", "open tabs"]):
        return ("browser_list", "")

    if any(word in text_lower for word in ["switch to", "go to", "open tab"]):
        # Extract what comes after the keyword
        for keyword in ["switch to", "go to", "open tab"]:
            if keyword in text_lower:
                arg = text_lower.split(keyword)[-1].strip()
                return ("browser_switch", arg)

    if any(word in text_lower for word in ["close tab", "close"]):
        for keyword in ["close tab", "close"]:
            if keyword in text_lower:
                arg = text_lower.split(keyword)[-1].strip()
                return ("browser_close", arg)

    return ("unknown", text)


async def dispatch(text: str) -> str:
    """
    Takes raw input, detects intent, calls the right function.
    Returns a response string.
    """
    intent, arg = detect_intent(text)

    if intent == "browser_list":
        tabs = await list_tabs()
        if not tabs:
            return "No tabs open."
        lines = [f"[{t['index']}] {t['title']}\n     {t['url']}" for t in tabs]
        return "\n".join(lines)

    elif intent == "browser_switch":
        return await switch_to_tab(arg)

    elif intent == "browser_close":
        return await close_tab(arg)

    else:
        return f"I didn't understand: '{text}'"


def run(text: str):
    """Synchronous wrapper — main.py calls this."""
    return asyncio.run(dispatch(text))
