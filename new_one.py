import asyncio
import os
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime
from dotenv import load_dotenv

from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import INVALID_PARAMS

from pydantic import BaseModel
import requests
from deep_translator import GoogleTranslator
from langdetect import detect

# --- Load environment variables ---
load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

assert AUTH_TOKEN, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# --- Logging Setup ---
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Tool Metadata Model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="mcp-puchai-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# --- FastMCP Setup ---
mcp = FastMCP(
    "Personality Chat MCP 🚀",
    auth=SimpleBearerAuthProvider(AUTH_TOKEN),
)

# --- Personality/Traits Config ---
PERSONALITIES = [
    "Brother", "Sister", "Lover", "Mother", "Father", "Girlfriend", "Boyfriend",
    "Friend", "Grandmother", "Grandfather"
]
CHARACTERISTICS = [
    "Caring", "Loving", "Funny", "Supportive", "Honest", "Adventurous",
    "Patient", "Understanding", "Well-mannered", "Confident", "Hardworking", "Talkative", "Quiet", "Other"
]
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
    return LANG_MAP.get(l, l[:2])

def translate_text(text: str, target_lang: str | None = 'en') -> str:
    if not text or not target_lang:
        return text
    try:
        tgt = normalize_language(target_lang)
        if not tgt or tgt == 'en':
            return text
        logger.debug(f"Translating to {tgt}...")
        return GoogleTranslator(source='auto', target=tgt).translate(text)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
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
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set")
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
    try:
        logger.debug("Sending request to Groq API...")
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: Could not reach Groq API")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in groq_chat: {e}")
        raise

# --- Tool Descriptions ---
PERSONA_DESCRIPTION = RichToolDescription(
    description="Chat as a custom persona (e.g., Brother, Friend, Girlfriend) with traits, language, and tone. Ideal for emotionally intelligent, role-playing, or multilingual responses.",
    use_when="Use for conversations where the bot should answer in a specific character or tone, or when emotional intelligence or multilingual support is needed.",
    side_effects=None,
)
VALIDATE_DESCRIPTION = RichToolDescription(
    description="Quickly check if the Personality Chat MCP server is healthy and configured.",
    use_when="Use to test server connection, status, or environment variable configuration.",
    side_effects=None,
)

# --- Validation Tool ---
@mcp.tool(description=VALIDATE_DESCRIPTION.model_dump_json())
def validate() -> str:
    """
    Simple validation to check if the MCP server is configured correctly.
    Returns MY_NUMBER if set, otherwise 'puchai:ok'.
    """
    return MY_NUMBER or "puchai:ok"

# --- Persona Chat Tool ---
@mcp.tool(description=PERSONA_DESCRIPTION.model_dump_json())
def turing2_persona_chat(
    personality: str,
    user_message: str,
    characteristics: List[str] | None = None,
    custom_characteristics: str = "",
    nationality: str = "",
    language: str = "",
    tone: str = "",
    more_details: str = "",
    chat_history: List[Dict[str, str]] | None = None,
    enforce_language: bool = True,
    temperature: float = 0.8,
    max_tokens: int = 512
) -> dict[str, Any]:
    """
    Engage in a persona-driven chat, replying in the desired personality and language.
    """
    logger.debug(f"Received turing2_persona_chat request: personality={personality}, user_message={user_message}")
    if not personality:
        logger.error("Personality is required")
        return {"error": "personality required", "reply": "", "chat_history": chat_history or []}
    if characteristics is None:
        characteristics = []
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

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for m in chat_history:
            if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                messages.append({"role": m["role"], "content": m["content"]})

    detected_user_lang = detect_language(user_message) if user_message else 'en'
    user_msg_en = translate_text(user_message, 'en') if detected_user_lang != 'en' else user_message
    messages.append({"role": "user", "content": user_msg_en})

    try:
        ai_raw = groq_chat(messages, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        logger.error(f"Model call failed: {e}")
        return {
            "error": f"Model call failed: {e}",
            "reply": "",
            "chat_history": chat_history or [],
            "persona_language": norm_language_code,
            "detected_user_language": detected_user_lang,
            "system_persona": system_prompt,
        }

    ai_reply = translate_text(ai_raw, norm_language_code) if norm_language_code else translate_text(ai_raw, detected_user_lang)

    updated_history = (chat_history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_reply}
    ]

    logger.debug(f"Returning reply: {ai_reply}")
    return {
        "reply": ai_reply,
        "chat_history": updated_history,
        "persona_language": norm_language_code,
        "detected_user_language": detected_user_lang,
        "system_persona": system_prompt,
    }

# --- Quick Persona Prompt Tool ---
@mcp.prompt
def quick_persona_exchange(
    personality: str,
    message: str,
    language: str = "English",
    traits: List[str] | None = None,
) -> str:
    """
    Quickly get a persona-driven reply for a given message and personality.
    """
    logger.debug(f"Quick persona exchange: personality={personality}, message={message}")
    traits = traits or ["Caring"]
    try:
        result = turing2_persona_chat(
            personality=personality,
            user_message=message,
            characteristics=traits,
            language=language,
            chat_history=[],
        )
        if "error" in result and result["error"]:
            logger.error(f"Error in turing2_persona_chat: {result['error']}")
            return f"Error: {result['error']}"
        return f"{personality} ({language}): {result['reply']}"
    except Exception as e:
        logger.error(f"Error in quick_persona_exchange: {e}")
        return f"Error in quick_persona_exchange: {e}"

# --- Main Entrypoint ---
async def main():
    logger.info("🚦 Starting Personality Chat MCP server on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())
