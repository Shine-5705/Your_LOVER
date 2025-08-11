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

# --- In-memory user session (replace with Redis/DB for production) ---
USER_STATE: dict[str, dict] = {}

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

def build_persona_description(
    personality: str,
    characteristics: list[str],
    custom: str,
    nationality: str,
    language: str,
    tone: str,
    more: str,
    enforce_language: bool
) -> str:
    desc = f"Act as the user's {personality.lower()}."
    if characteristics:
        desc += f"\nTraits: {', '.join(characteristics)}"
    if custom:
        desc += f", {custom}" if characteristics else f"\nExtra traits: {custom}"
    if nationality:
        desc += f"\nNationality: {nationality}"
    if language:
        desc += f"\nLanguage: {language}"
        if enforce_language:
            desc += (f"\nIMPORTANT: Reply ONLY in {language}. "
                     f"Don't use English or translations. Be as natural as a real {personality.lower()}.")
    if tone:
        desc += f"\nTone: {tone}"
    if more:
        desc += f"\nMore: {more}"
    desc += (
        "\n\nSpeak casually, human-like, never as a bot. All replies should be short and natural (1-3 sentences max)."
        " Never explain or break character."
    )
    return desc

def groq_chat(messages: list[dict[str, str]], api_key: str = GROQ_API_KEY, temperature: float = 0.7,
              max_tokens: int = 256) -> str:
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
    except Exception as e:
        logger.error(f"Groq chat failed: {e}")
        return "Sorry, I couldn't get a reply right now."

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

# --- Persona Chat Tool (waits for user state to be ready for chat) ---
@mcp.tool(description=PERSONA_DESCRIPTION.model_dump_json())
def turing2_persona_chat(
    user_id: str,
    user_message: str,
    chat_history: List[Dict[str, str]] | None = None,
    enforce_language: bool = True,
    temperature: float = 0.7,
    max_tokens: int = 256
) -> dict[str, Any]:
    """
    Main chat entry: replies in persona once persona setup is done.
    """
    session = USER_STATE.setdefault(user_id, {})
    step = session.get("step", "start")

    # 1. Persona selection step
    if step == "start":
        session["step"] = "persona"
        return {
            "reply": "Who do you want to talk to?\n" + "\n".join([f"- {p}" for p in PERSONALITIES]),
            "poll_type": "list",
            "options": PERSONALITIES,
            "step": "persona"
        }

    # 2. Trait selection step
    if step == "persona":
        personality = user_message.strip().capitalize()
        if personality not in PERSONALITIES:
            return {
                "reply": f"Please choose one from the list:\n" + "\n".join([f"- {p}" for p in PERSONALITIES]),
                "poll_type": "list",
                "options": PERSONALITIES,
                "step": "persona"
            }
        session["personality"] = personality
        session["step"] = "traits"
        return {
            "reply": "Select up to 3 traits for this persona (comma-separated or choose):\n" +
                     "\n".join([f"{i+1}. {t}" for i, t in enumerate(CHARACTERISTICS)]),
            "poll_type": "multi",
            "options": CHARACTERISTICS,
            "step": "traits"
        }

    # 3. Custom traits step
    if step == "traits":
        # Accept comma or number-based selection
        traits = []
        for part in user_message.replace(',', ' ').split():
            try:
                idx = int(part) - 1
                if 0 <= idx < len(CHARACTERISTICS):
                    traits.append(CHARACTERISTICS[idx])
                elif part.capitalize() in CHARACTERISTICS:
                    traits.append(part.capitalize())
            except:
                if part.capitalize() in CHARACTERISTICS:
                    traits.append(part.capitalize())
        traits = list({t for t in traits if t in CHARACTERISTICS})
        if not traits:
            return {
                "reply": "Please pick at least one trait. Example: 1,3,5 or Caring, Funny",
                "poll_type": "multi",
                "options": CHARACTERISTICS,
                "step": "traits"
            }
        session["characteristics"] = traits
        session["step"] = "custom"
        return {
            "reply": "Any extra details? (Type or say 'none' if not needed)",
            "poll_type": "text",
            "step": "custom"
        }

    # 4. Details step
    if step == "custom":
        custom = user_message.strip()
        session["custom_characteristics"] = "" if custom.lower() == "none" else custom
        session["step"] = "ready"
        return {
            "reply": "Great! Any specific language or tone you'd like? (e.g., Hindi, playful)\nOr type 'skip' to use default.",
            "poll_type": "text",
            "step": "ready"
        }

    # 5. Final chat prep
    if step == "ready":
        lang = ""
        tone = ""
        parts = user_message.split(',')
        for p in parts:
            if "hindi" in p.lower() or "english" in p.lower():
                lang = p.strip()
            elif "playful" in p.lower() or "formal" in p.lower() or "warm" in p.lower():
                tone = p.strip()
        session["language"] = lang
        session["tone"] = tone
        session["step"] = "chat"
        session["chat_history"] = []
        # Greet as persona:
        greeting = f"Say hi as {session['personality'].lower()} with traits: {', '.join(session['characteristics'])}."
        system_prompt = build_persona_description(
            session["personality"],
            session["characteristics"],
            session.get("custom_characteristics", ""),
            "",
            session.get("language", ""),
            session.get("tone", ""),
            "",
            enforce_language=True,
        )
        session["system_prompt"] = system_prompt
        session["chat_history"] = [{"role": "system", "content": system_prompt}]
        session["chat_history"].append({"role": "user", "content": greeting})

        ai_raw = groq_chat(session["chat_history"])
        session["chat_history"].append({"role": "assistant", "content": ai_raw})

        return {
            "reply": ai_raw,
            "step": "chat",
            "persona": session["personality"]
        }

    # 6. Main chat
    if step == "chat":
        system_prompt = session["system_prompt"]
        chat_history = session.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_message})

        ai_raw = groq_chat(chat_history)
        ai_reply = ai_raw.strip().split('\n')[0]  # Short, 1-2 lines only
        chat_history.append({"role": "assistant", "content": ai_reply})
        session["chat_history"] = chat_history
        return {
            "reply": ai_reply,
            "step": "chat",
            "persona": session["personality"]
        }

    # Fallback
    return {"reply": "Let's start! Who do you want to talk to?", "step": "persona", "options": PERSONALITIES}

# --- Quick Persona Prompt Tool ---
@mcp.prompt
def quick_persona_exchange(
    user_id: str,
    message: str,
) -> str:
    """
    Quickly get a persona-driven reply for a given message and personality (assumes user already set up).
    """
    session = USER_STATE.get(user_id)
    if not session or session.get("step") != "chat":
        return "Please set up your persona first!"
    result = turing2_persona_chat(user_id, message)
    return f"{session['personality']}: {result['reply']}"

# --- Main Entrypoint ---
async def main():
    logger.info("🚦 Starting Personality Chat MCP server on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())
