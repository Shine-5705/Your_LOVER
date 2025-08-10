from __future__ import annotations
import os
import requests
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP
from deep_translator import GoogleTranslator
from langdetect import detect

# === MCP Server Instance ===
mcp = FastMCP("Turing2 Personality Chat MCP")
load_dotenv()

# --- Settings ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

PERSONALITIES = [
    "Brother", "Sister", "Lover", "Mother", "Father", "Girlfriend", "Boyfriend",
    "Friend", "Grandmother", "Grandfather"
]
CHARACTERISTICS = [
    "Caring", "Loving", "Funny", "Supportive", "Honest", "Adventurous",
    "Patient", "Understanding", "Well-mannered", "Confident", "Hardworking", "Talkative", "Quiet", "Other"
]

# Common language name to code map (extend as needed)
LANG_MAP = {
    'english': 'en', 'en': 'en',
    'hindi': 'hi', 'spanish': 'es', 'french': 'fr', 'german': 'de', 'italian': 'it',
    'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja', 'korean': 'ko',
    'chinese': 'zh', 'arabic': 'ar', 'bengali': 'bn', 'marathi': 'mr', 'tamil': 'ta',
    'telugu': 'te', 'gujarati': 'gu', 'punjabi': 'pa', 'urdu': 'ur'
}

def normalize_language(lang: str | None) -> str | None:
    if not lang:
        return None
    l = lang.strip().lower()
    if not l:
        return None
    return LANG_MAP.get(l, l[:2])

def translate_text(text: str, target_lang: str | None = 'en') -> str:
    if not text or not target_lang:
        return text
    try:
        tgt = normalize_language(target_lang)
        if not tgt or tgt == 'en':
            # If translation target is English or unknown, keep original
            return text
        return GoogleTranslator(source='auto', target=tgt).translate(text)
    except Exception:
        return text  # fallback on any failure

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return 'en'

def build_persona_description(personality: str, characteristics: list[str], custom: str, nationality: str,
                              language: str, tone: str, more: str, enforce_language: bool) -> str:
    desc = f"Act as the user's {personality.lower()}."
    if characteristics:
        desc += f"\nCharacteristics: {', '.join(characteristics)}"
    if custom:
        desc += f", {custom}" if characteristics else f"\nExtra characteristics: {custom}"
    if nationality:
        desc += f"\nNationality: {nationality}"
    if language:
        desc += f"\nLanguage: {language}"
        if enforce_language:
            desc += (f"\nIMPORTANT: All of your responses MUST be in {language} only. "
                      f"Do NOT add any English translation, transliteration, or bilingual content. "
                      f"Respond naturally and colloquially, like a real human using only {language}.")
    if tone:
        desc += f"\nTone: {tone}"
    if more:
        desc += f"\nExtra details: {more}"
    desc += ("\n\nYou are having an ongoing conversation. Keep replies concise (1-5 sentences), "
             "context-aware, emotionally consistent, and never break character.")
    return desc

def groq_chat(messages: list[dict[str, str]], api_key: str = GROQ_API_KEY, temperature: float = 0.8,
              max_tokens: int = 512) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop": None
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content']

@mcp.tool()
def turing2_persona_chat(
    personality: str,
    user_message: str,
    characteristics: list[str] | None = None,
    custom_characteristics: str = "",
    nationality: str = "",
    language: str = "",
    tone: str = "",
    more_details: str = "",
    chat_history: list[dict[str, str]] | None = None,
    enforce_language: bool = True,
    temperature: float = 0.8,
    max_tokens: int = 512
) -> dict[str, Any]:
    """Send one chat turn to the Turing2 personality engine and receive a reply.

    Parameters:
      personality: Persona relationship label (Brother, Sister, etc.)
      user_message: The latest user message (any language)
      characteristics: List of selected traits (without 'Other')
      custom_characteristics: Free-form traits/details if 'Other'
      nationality: Optional nationality descriptor
      language: Desired output language name (e.g. Hindi, English, Spanish) – can be blank
      tone: Desired tone (warm, playful, formal, etc.)
      more_details: Additional context (job, habits, backstory)
      chat_history: Previous messages (exclude system) [{"role": "user"|"assistant", "content": str}]
      enforce_language: If True, system prompt forces strict single-language replies
      temperature: Sampling temperature for model
      max_tokens: Max tokens for model reply

    Returns dict with keys:
      reply: Assistant reply (already translated if needed)
      chat_history: Updated history including this user + assistant turn
      persona_language: Normalized language code (if provided)
      detected_user_language: Detected language of user_message
      system_persona: The system prompt used this turn
    """
    if not personality:
        raise ValueError("personality required")
    if characteristics is None:
        characteristics = []
    # Filter out 'Other'
    characteristics = [c for c in characteristics if c and c.lower() != 'other']

    norm_language_code = normalize_language(language) if language else None

    system_prompt = build_persona_description(
        personality=personality,
        characteristics=characteristics,
        custom=custom_characteristics,
        nationality=nationality,
        language=language,
        tone=tone,
        more=more_details,
        enforce_language=enforce_language,
    )

    # Build messages list
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        # Only allow valid roles
        for m in chat_history:
            if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                messages.append({"role": m["role"], "content": m["content"]})

    # Detect & translate user input to English for LLM
    detected_user_lang = detect_language(user_message) if user_message else 'en'
    user_msg_en = translate_text(user_message, 'en') if detected_user_lang != 'en' else user_message
    messages.append({"role": "user", "content": user_msg_en})

    # Call model
    try:
        ai_raw = groq_chat(messages, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return {
            "error": f"Model call failed: {e}",
            "reply": "",
            "chat_history": chat_history or [],
            "persona_language": norm_language_code,
            "detected_user_language": detected_user_lang,
            "system_persona": system_prompt,
        }

    # Translate reply if needed
    if norm_language_code:
        ai_reply = translate_text(ai_raw, norm_language_code)
    else:
        # fallback: respond in user's detected language
        ai_reply = translate_text(ai_raw, detected_user_lang)

    updated_history = (chat_history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_reply}
    ]

    return {
        "reply": ai_reply,
        "chat_history": updated_history,
        "persona_language": norm_language_code,
        "detected_user_language": detected_user_lang,
        "system_persona": system_prompt,
    }

@mcp.prompt()
def quick_persona_exchange(
    personality: str,
    message: str,
    language: str = "English",
    traits: list[str] | None = None,
) -> str:
    """Lightweight prompt wrapper for a single-turn exchange.

    Example: quick_persona_exchange(personality="Brother", message="How are you?", language="Hindi")
    """
    traits = traits or ["Caring"]
    result = turing2_persona_chat(
        personality=personality,
        user_message=message,
        characteristics=traits,
        language=language,
        chat_history=[],
    )
    if "error" in result and result["error"]:
        return f"Error: {result['error']}"
    return f"{personality} ({language}): {result['reply']}"

if __name__ == "__main__":
    mcp.run()
