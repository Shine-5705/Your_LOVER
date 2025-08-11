"""MCP server exposing simplified tools for the turing2 persona chat logic.

Run (stdio):
  uv run server turing2_simple_mcp stdio
Or (python):
  python turing2_simple_mcp.py
"""
from __future__ import annotations
import os
import requests
from typing import Any, List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from deep_translator import GoogleTranslator
from langdetect import detect
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Turing2 Simple MCP")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

PERSONALITIES = [
    "Brother", "Sister", "Lover", "Mother", "Father", "Girlfriend", "Boyfriend",
    "Friend", "Grandmother", "Grandfather"
]

LANG_MAP = {
    'english': 'en', 'en': 'en', 'hindi': 'hi', 'spanish': 'es', 'french': 'fr', 'german': 'de',
    'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja', 'korean': 'ko',
    'chinese': 'zh', 'arabic': 'ar', 'bengali': 'bn', 'marathi': 'mr', 'tamil': 'ta',
    'telugu': 'te', 'gujarati': 'gu', 'punjabi': 'pa', 'urdu': 'ur'
}

def _norm_lang(lang: str | None) -> str | None:
    if not lang:
        return None
    l = lang.strip().lower()
    if not l:
        return None
    return LANG_MAP.get(l, l[:2])

def translate_text(text: str, target_lang: str | None) -> str:
    if not text or not target_lang:
        return text
    try:
        tgt = _norm_lang(target_lang)
        if not tgt or tgt == 'en':
            return text
        return GoogleTranslator(source='auto', target=tgt).translate(text)
    except Exception:
        return text

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return 'en'

def build_persona_description(personality: str, traits: List[str], custom: str, nationality: str,
                              language: str, tone: str, more: str, enforce_language: bool) -> str:
    desc = f"Act as the user's {personality.lower()}."
    if traits:
        desc += f"\nCharacteristics: {', '.join(traits)}"
    if custom:
        desc += f"\nAdditional traits: {custom}"
    if nationality:
        desc += f"\nNationality: {nationality}"
    if language:
        desc += f"\nLanguage: {language}"
        if enforce_language:
            desc += (f"\nIMPORTANT: Respond ONLY in {language}. No translations, no bilingual output. "
                     f"Natural, human tone.")
    if tone:
        desc += f"\nTone: {tone}"
    if more:
        desc += f"\nExtra details: {more}"
    desc += ("\n\nMaintain emotional consistency, never break character, keep replies concise (1-5 sentences).")
    return desc

def groq_chat(messages: List[Dict[str, str]], api_key: str = GROQ_API_KEY, temperature: float = 0.8, max_tokens: int = 512) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop": None
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

@mcp.tool()
def init_persona(
    personality: str,
    traits: List[str] | None = None,
    custom_traits: str = "",
    nationality: str = "",
    language: str = "",
    tone: str = "",
    more_details: str = "",
    enforce_language: bool = True,
) -> Dict[str, Any]:
    """Initialize a persona. Returns system prompt and normalized language code.
    Use the returned system_prompt and persona_language_code in subsequent chat_turn calls.
    """
    if personality not in PERSONALITIES:
        raise ValueError(f"personality must be one of {PERSONALITIES}")
    traits = traits or []
    traits = [t for t in traits if t.lower() != 'other']
    persona_lang_code = _norm_lang(language) if language else None
    system_prompt = build_persona_description(
        personality, traits, custom_traits, nationality, language, tone, more_details, enforce_language
    )
    return {
        "system_prompt": system_prompt,
        "persona_language_code": persona_lang_code,
    }

@mcp.tool()
def chat_turn(
    system_prompt: str,
    user_message: str,
    chat_history: List[Dict[str, str]] | None = None,
    persona_language_code: str | None = None,
    temperature: float = 0.8,
    max_tokens: int = 512,
) -> Dict[str, Any]:
    """Send one chat turn. Provide system_prompt (from init_persona) and prior chat_history.
    chat_history is a list of {role: 'user'|'assistant', content: str} excluding system.
    Returns reply and updated chat_history.
    """
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for m in chat_history:
            if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                messages.append({"role": m["role"], "content": m["content"]})
    detected_user_lang = detect_language(user_message) if user_message else 'en'
    user_msg_en = translate_text(user_message, 'en') if detected_user_lang != 'en' else user_message
    messages.append({"role": "user", "content": user_msg_en})
    try:
        raw = groq_chat(messages, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        return {"error": f"model_error: {e}", "reply": "", "chat_history": chat_history or []}
    if persona_language_code:
        reply = translate_text(raw, persona_language_code)
    else:
        reply = translate_text(raw, detected_user_lang)
    updated = (chat_history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply}
    ]
    return {
        "reply": reply,
        "chat_history": updated,
        "detected_user_language": detected_user_lang,
    }

@mcp.prompt()
def quick_reply(personality: str, message: str, language: str = "English") -> str:
    """Convenience single-turn prompt: builds a simple caring persona and returns formatted reply."""
    init = init_persona(personality=personality, traits=["Caring"], language=language)
    turn = chat_turn(system_prompt=init["system_prompt"], user_message=message, persona_language_code=init["persona_language_code"])
    if turn.get("error"):
        return f"Error: {turn['error']}"
    return f"{personality} ({language}): {turn['reply']}"

@mcp.resource("persona://{personality}")
def persona_resource(personality: str) -> str:
    """Simple resource returning a default caring persona system prompt."""
    init = init_persona(personality=personality, traits=["Caring"], language="English")
    return init["system_prompt"]

if __name__ == "__main__":
    import sys
    print("[turing2_simple_mcp] Starting FastMCP server on stdio...", file=sys.stderr)
    mcp.run()
