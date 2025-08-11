from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
from deep_translator import GoogleTranslator
from langdetect import detect
from dotenv import load_dotenv
load_dotenv()

# FastAPI app
app = FastAPI(title="AI Personality Chat", description="Chat with AI personalities in different languages")

# Configuration
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

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    personality: str
    characteristics: List[str]
    custom_characteristics: Optional[str] = ""
    nationality: Optional[str] = ""
    language: Optional[str] = ""
    tone: Optional[str] = ""
    more_details: Optional[str] = ""
    user_message: str
    chat_history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    reply: str
    personality: str
    language: str

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
        return detect(text)
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

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Personality Chat</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .response { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
            .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
            .checkbox-item { display: flex; align-items: center; margin-right: 15px; }
            .checkbox-item input { width: auto; margin-right: 5px; }
        </style>
    </head>
    <body>
        <h1>AI Personality Chat</h1>
        <form id="chatForm">
            <div class="form-group">
                <label for="personality">Personality:</label>
                <select id="personality" required>
                    <option value="">Select a personality</option>
                    <option value="Brother">Brother</option>
                    <option value="Sister">Sister</option>
                    <option value="Lover">Lover</option>
                    <option value="Mother">Mother</option>
                    <option value="Father">Father</option>
                    <option value="Girlfriend">Girlfriend</option>
                    <option value="Boyfriend">Boyfriend</option>
                    <option value="Friend">Friend</option>
                    <option value="Grandmother">Grandmother</option>
                    <option value="Grandfather">Grandfather</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Characteristics:</label>
                <div class="checkbox-group">
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Caring"> Caring</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Loving"> Loving</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Funny"> Funny</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Supportive"> Supportive</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Honest"> Honest</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Adventurous"> Adventurous</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Patient"> Patient</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Understanding"> Understanding</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Well-mannered"> Well-mannered</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Confident"> Confident</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Hardworking"> Hardworking</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Talkative"> Talkative</div>
                    <div class="checkbox-item"><input type="checkbox" name="characteristics" value="Quiet"> Quiet</div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="nationality">Nationality (optional):</label>
                <input type="text" id="nationality" placeholder="e.g., Indian, American, British">
            </div>
            
            <div class="form-group">
                <label for="language">Language (optional):</label>
                <input type="text" id="language" placeholder="e.g., Hindi, Spanish, French">
            </div>
            
            <div class="form-group">
                <label for="tone">Tone (optional):</label>
                <input type="text" id="tone" placeholder="e.g., warm, formal, playful">
            </div>
            
            <div class="form-group">
                <label for="user_message">Your Message:</label>
                <textarea id="user_message" rows="3" required placeholder="Type your message here..."></textarea>
            </div>
            
            <button type="submit">Send Message</button>
        </form>
        
        <div id="response" class="response" style="display: none;">
            <h3>Response:</h3>
            <div id="responseContent"></div>
        </div>
        
        <script>
            document.getElementById('chatForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const characteristics = Array.from(document.querySelectorAll('input[name="characteristics"]:checked')).map(cb => cb.value);
                
                const data = {
                    personality: document.getElementById('personality').value,
                    characteristics: characteristics,
                    nationality: document.getElementById('nationality').value,
                    language: document.getElementById('language').value,
                    tone: document.getElementById('tone').value,
                    user_message: document.getElementById('user_message').value
                };
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('responseContent').innerHTML = 
                            `<strong>${result.personality}:</strong> ${result.reply}`;
                        document.getElementById('response').style.display = 'block';
                    } else {
                        alert('Error: ' + result.detail);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat_with_personality(request: ChatRequest):
    try:
        # Detect persona language code (like 'hi' for Hindi)
        persona_language_code = None
        if request.language:
            # Map common language names to codes
            lang_map = {
                'hindi': 'hi', 'spanish': 'es', 'french': 'fr', 'german': 'de',
                'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja',
                'korean': 'ko', 'chinese': 'zh', 'arabic': 'ar'
            }
            persona_language_code = lang_map.get(request.language.lower(), request.language.lower()[:2])

        # Build system prompt/persona
        persona_desc = build_persona_description(
            request.personality, 
            [c for c in request.characteristics if c != "Other"], 
            request.custom_characteristics, 
            request.nationality, 
            request.language, 
            request.tone, 
            request.more_details
        )

        # Prepare chat history for LLM
        messages = [{"role": "system", "content": persona_desc}]
        if request.chat_history:
            messages.extend([{"role": msg.role, "content": msg.content} for msg in request.chat_history])
        
        # Add the latest user message (translated to English for LLM if needed)
        user_lang = detect_language(request.user_message)
        user_msg_en = translate_text(request.user_message, 'en') if user_lang != 'en' else request.user_message
        messages.append({"role": "user", "content": user_msg_en})

        # Get AI reply from Groq
        ai_message = groq_chat(messages)

        # Translate AI reply to the persona language
        if persona_language_code:
            ai_message = translate_text(ai_message, persona_language_code)
        else:
            # fallback: reply in user's detected language
            ai_message = translate_text(ai_message, user_lang)
        
        return ChatResponse(
            reply=ai_message,
            personality=request.personality,
            language=request.language or user_lang
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personalities")
async def get_personalities():
    return {"personalities": PERSONALITIES}

@app.get("/characteristics")
async def get_characteristics():
    return {"characteristics": CHARACTERISTICS}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("personality_web:app", host="127.0.0.1", port=8000, reload=True)
