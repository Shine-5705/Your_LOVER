from mcp.server.fastmcp import FastMCP
import os
import requests
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

# Create an MCP server
mcp = FastMCP("AI Personality Chat MCP Tool")

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

def translate_text(text, target_lang='en'):
    try:
        # Convert language names to language codes
        lang_map = {
            'hindi': 'hi', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja',
            'korean': 'ko', 'chinese': 'zh', 'arabic': 'ar'
        }
        
        target_code = lang_map.get(target_lang.lower(), target_lang.lower()[:2])
        if target_code == 'en' or not target_code:
            return text
            
        translator = GoogleTranslator(source='auto', target=target_code)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # fallback

def detect_language(text):
    try:
        translator = GoogleTranslator(source='auto', target='en')
        # This is a simple detection - we'll assume based on content
        return 'en'  # Default fallback
    except Exception:
        return 'en'

def build_persona_description(personality, characteristics, custom, nationality, language, tone, more):
    desc = f"Act as the user's {personality.lower()}.\n"
    desc += f"Characteristics: {', '.join(characteristics)}"
    if custom:
        desc += f", {custom}"
    if nationality:
        desc += f"\nNationality: {nationality}"
    if language:
        desc += f"\nLanguage: {language}"
        desc += (
            f"\nIMPORTANT: All of your responses MUST be in {language} only. "
            f"Do NOT add any English translation, transliteration, or bilingual content. "
            f"Respond like a real human, using only {language}."
        )
    if tone:
        desc += f"\nTone: {tone}"
    if more:
        desc += f"\nExtra details: {more}"
    desc += "\n\nNow start a natural, human-like conversation as this personality, using the correct language and tone."
    return desc

def groq_chat(messages, api_key=GROQ_API_KEY):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 1024,
        "stop": None
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

@mcp.tool()
def ai_personality_chat(
    personality: str,
    characteristics: list,
    custom_characteristics: str = "",
    nationality: str = "",
    language: str = "",
    tone: str = "",
    more_details: str = "",
    user_message: str = "",
    chat_history: list = None
) -> str:
    """
    Chat with an AI personality. Give persona details and a user message, and get a reply in the specified language.
    Parameters:
      - personality: one of Brother, Sister, Lover, etc.
      - characteristics: list of traits (Caring, Loving, etc.)
      - custom_characteristics: (optional) more details
      - nationality: (optional)
      - language: (optional) e.g. "Hindi"
      - tone: (optional)
      - more_details: (optional)
      - user_message: message from user
      - chat_history: (optional) previous chat history [{"role": "user"/"assistant", "content": ...}]
    Returns:
      - reply from the AI, ONLY in the requested language
    """
    # Detect persona language code (like 'hi' for Hindi)
    persona_language_code = None
    if language:
        # Map common language names to codes
        lang_map = {
            'hindi': 'hi', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja',
            'korean': 'ko', 'chinese': 'zh', 'arabic': 'ar'
        }
        persona_language_code = lang_map.get(language.lower(), language.lower()[:2])

    # Build system prompt/persona
    persona_desc = build_persona_description(
        personality, [c for c in characteristics if c != "Other"], custom_characteristics, nationality, language, tone, more_details
    )

    # Prepare chat history for LLM
    messages = [{"role": "system", "content": persona_desc}]
    if chat_history:
        messages.extend(chat_history)
    # Add the latest user message (translated to English for LLM if needed)
    user_lang = detect_language(user_message)
    user_msg_en = translate_text(user_message, 'en') if user_lang != 'en' else user_message
    messages.append({"role": "user", "content": user_msg_en})

    # Get AI reply from Groq
    ai_message = groq_chat(messages)

    # Translate AI reply to the persona language
    if persona_language_code:
        ai_message = translate_text(ai_message, persona_language_code)
    else:
        # fallback: reply in user's detected language
        ai_message = translate_text(ai_message, user_lang)
    return ai_message

# === Example usage as a prompt tool ===
@mcp.prompt()
def chat_as_personality(
    name: str, 
    personality: str, 
    message: str, 
    traits: list = None, 
    language: str = "Hindi"
) -> str:
    """
    Quick prompt to chat with a personality.
    """
    traits = traits or ["Caring"]
    ai_reply = ai_personality_chat(
        personality=personality,
        characteristics=traits,
        language=language,
        user_message=message
    )
    return f"{personality} ({language}): {ai_reply}"

# You can now run this server using FastMCP, and call the tool in your agent, workflow, or prompt!

if __name__ == "__main__":
    # Run FastMCP server using its built-in method
    mcp.run()
