from __future__ import annotations
import os
import requests
from typing import Optional, Any, Dict
from fastmcp import FastMCP, Context
from deep_translator import GoogleTranslator
from langdetect import detect
import logging
from dotenv import load_dotenv


load_dotenv()
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Custom FastMCP class to handle method listing
class CustomFastMCP(FastMCP):
    async def handle_jsonrpc(self, request: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
        method = request.get("method")
        if method == "list_methods":
            # Return list of available methods
            available_methods = ["tools/call", "tools/list", "prompts/get", "prompts/list"]
            return {
                "jsonrpc": "2.0",
                "result": {"methods": available_methods},
                "id": request.get("id", "server-generated-id")
            }
        return await super().handle_jsonrpc(request, ctx)

# Initialize FastMCP in stateless mode
mcp = CustomFastMCP("Personality Chat MCP 🚀")

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

@mcp.tool
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

@mcp.prompt
def quick_persona_exchange(
    personality: str,
    message: str,
    language: str = "English",
    traits: list[str] | None = None,
) -> str:
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

if __name__ == "__main__":
    try:
        import requests
        from deep_translator import GoogleTranslator
        from langdetect import detect
        logger.info("All dependencies imported successfully")
    except ImportError as e:
        logger.error(f"Dependency error: {e}")
        logger.error("Please install required packages: uv pip install requests deep-translator langdetect fastmcp")
        exit(1)

    if not GROQ_API_KEY:
        logger.error("Error: GROQ_API_KEY environment variable is not set")
        logger.error("Set it using: export GROQ_API_KEY='your-api-key'")
        exit(1)

    logger.info("Starting FastMCP server in stateless mode")
    PORT = int(os.environ.get("PORT", 9000))

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=PORT,
        log_level="DEBUG",
        stateless_http=True
    )

