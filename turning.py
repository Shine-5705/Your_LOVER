import os
import requests
import questionary
import os
import requests
import questionary
from deep_translator import GoogleTranslator
from langdetect import detect
from dotenv import load_dotenv

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

def translate_text(text, target_lang='en'):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        return text  # fallback

def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return 'en'

def get_personality():
    return questionary.select(
        "Who do you want to talk to?",
        choices=PERSONALITIES
    ).ask()

def get_characteristics():
    return questionary.checkbox(
        "Select characteristics (use spacebar to select, enter to confirm):",
        choices=CHARACTERISTICS
    ).ask()

def get_custom_characteristics():
    return questionary.text("Describe any other characteristics or details (leave blank if none):").ask()

def get_details():
    nationality = questionary.text("Specify the nationality (or leave blank):").ask()
    language = questionary.text("Specify preferred language (English, Hindi, etc.):").ask()
    tone = questionary.text("Specify preferred tone (e.g., warm, formal, playful):").ask()
    more = questionary.text("Add any additional details about this person (job, habits, etc.):").ask()
    return nationality, language, tone, more

def build_persona_description(personality, characteristics, custom, nationality, language, tone, more):
    desc = f"Act as the user's {personality.lower()}.\n"
    desc += f"Characteristics: {', '.join(characteristics)}"
    if custom:
        desc += f", {custom}"
    if nationality:
        desc += f"\nNationality: {nationality}"
    if language:
        desc += f"\nLanguage: {language}"
    if tone:
        desc += f"\nTone: {tone}"
    if more:
        desc += f"\nExtra details: {more}"
    desc += "\n\nNow start a natural, human-like conversation as this personality, in the correct language and tone."
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

def setup_persona():
    personality = get_personality()
    characteristics = get_characteristics()
    custom = ""
    if "Other" in characteristics:
        custom = get_custom_characteristics()
    nationality, language, tone, more = get_details()
    persona_desc = build_persona_description(
        personality, [c for c in characteristics if c != "Other"], custom, nationality, language, tone, more
    )
    return personality, persona_desc, language.strip() if language else None

def main():
    print("\n--- AI Personality Chat ---\n")
    print("Type 'exit', 'quit', or 'q' at any time to leave the chat.")
    print("Type 'setting' at any time to modify the personality and its specifications.\n")

    personality, persona_desc, persona_language = setup_persona()
    print("\nSetting up your conversation partner...\n")

    messages = [
        {"role": "system", "content": persona_desc},
    ]
    first_prompt = f"Begin as the user's {personality.lower()} and say hello in a way that matches all these traits."
    messages.append({"role": "user", "content": first_prompt})

    try:
        ai_message = groq_chat(messages)
        # If language specified, translate AI response
        reply_lang = persona_language or detect_language(ai_message)
        if detect_language(ai_message) != reply_lang:
            ai_message = translate_text(ai_message, reply_lang)
        print(f"\n{personality}: {ai_message}\n")
        messages.append({"role": "assistant", "content": ai_message})
    except Exception as e:
        print(f"Error communicating with API: {e}")
        return

    while True:
        user_msg = questionary.text("You: ").ask()
        user_msg_lower = user_msg.strip().lower()
        if user_msg_lower in ['exit', 'quit', 'q']:
            print("Ending conversation. Goodbye!")
            break
        if user_msg_lower == 'setting':
            print("\n--- Modify Personality & Specifications ---\n")
            personality, persona_desc, persona_language = setup_persona()
            messages = [{"role": "system", "content": persona_desc}]
            first_prompt = f"Begin as the user's {personality.lower()} and say hello in a way that matches all these traits."
            messages.append({"role": "user", "content": first_prompt})
            try:
                ai_message = groq_chat(messages)
                reply_lang = persona_language or detect_language(ai_message)
                if detect_language(ai_message) != reply_lang:
                    ai_message = translate_text(ai_message, reply_lang)
                print(f"\n{personality}: {ai_message}\n")
                messages.append({"role": "assistant", "content": ai_message})
            except Exception as e:
                print(f"Error communicating with API: {e}")
                break
            continue

        # Detect and translate user input to English for LLM
        user_lang = detect_language(user_msg)
        user_msg_en = translate_text(user_msg, 'en') if user_lang != 'en' else user_msg
        messages.append({"role": "user", "content": user_msg_en})
        try:
            ai_message = groq_chat(messages)
            # Translate AI reply back to persona language or user's language
            reply_lang = persona_language if persona_language else user_lang
            if detect_language(ai_message) != reply_lang:
                ai_message = translate_text(ai_message, reply_lang)
            print(f"\n{personality}: {ai_message}\n")
            messages.append({"role": "assistant", "content": ai_message})
        except Exception as e:
            print(f"Error communicating with API: {e}")
            break

if __name__ == "__main__":
    main()
