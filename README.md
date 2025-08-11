# Personality Chat MCP Server 🚀

A powerful [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that enables AI assistants like Puch AI to engage in persona-driven conversations with multilingual support and emotional intelligence.

## Features

- 🎭 **10+ Personality Types**: Brother, Sister, Lover, Mother, Father, Girlfriend, Boyfriend, Friend, Grandmother, Grandfather
- 🌍 **Multilingual Support**: 20+ languages including Hindi, Spanish, French, German, Japanese, Korean, Chinese, Arabic, and more
- 🧠 **AI-Powered Responses**: Powered by Groq's Llama 3.3 70B model for natural conversations
- 🔒 **Bearer Token Authentication**: Secure authentication system compatible with Puch AI
- 🎨 **Customizable Traits**: Configure personality characteristics like Caring, Loving, Funny, Supportive, etc.
- 📝 **Chat History**: Maintains conversation context for coherent interactions
- 🔄 **Auto Translation**: Automatically detects and translates between languages

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Environment variables configured
- GROQ API key

### Installation

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd Your_LOVER
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   AUTH_TOKEN=your_secret_token_here
   MY_NUMBER=919876543210
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the server:**
   ```bash
   python new_one.py
   ```

   You'll see: `🚦 Starting Personality Chat MCP server on http://0.0.0.0:8086`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTH_TOKEN` | Secret token for authentication | `yourlover575` |
| `MY_NUMBER` | Your phone number (country_code + number) | `919876543210` |
| `GROQ_API_KEY` | Your Groq API key for AI responses | `gsk_...` |

## Connecting with Puch AI

### Step 1: Deploy Your Server

Deploy to a public HTTPS endpoint using:
- **Render** (recommended): Use the included [`render.yaml`](render.yaml)
- **Railway**, **Heroku**, or **DigitalOcean**
- **ngrok** for local testing

### Step 2: Connect in Puch AI

1. Open [Puch AI](https://wa.me/+919998881729) in WhatsApp
2. Start a conversation
3. Use the connect command:
   ```
   /mcp connect https://your-deployed-server-url yourlover575
   ```

### Step 3: Start Chatting!

Once connected, you can use the personality chat tool for engaging conversations!

## Available Tools

### 1. `turing2_persona_chat`

The main personality chat tool with extensive customization options.

**Parameters:**
- `personality` (required): Choose from Brother, Sister, Lover, Mother, Father, etc.
- `user_message` (required): Your message to the AI persona
- `characteristics`: List of traits (Caring, Loving, Funny, Supportive, etc.)
- `custom_characteristics`: Additional custom traits
- `nationality`: Set the persona's nationality
- `language`: Response language (English, Hindi, Spanish, etc.)
- `tone`: Communication tone
- `more_details`: Additional personality details
- `chat_history`: Previous conversation context
- `enforce_language`: Force responses in specified language only
- `temperature`: AI creativity level (0.0-1.0)
- `max_tokens`: Maximum response length

**Example Usage:**
```json
{
  "personality": "Girlfriend",
  "user_message": "How was your day?",
  "characteristics": ["Caring", "Loving", "Supportive"],
  "language": "Hindi",
  "tone": "Romantic",
  "enforce_language": true
}
```

### 2. `validate`

Simple validation tool that returns your configured phone number when provided with the correct bearer token.

### 3. `quick_persona_exchange` (Prompt)

Quick way to get a persona-driven reply without full customization.

## Supported Languages

The server supports 20+ languages with automatic translation:

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | `en` | Hindi | `hi` |
| Spanish | `es` | French | `fr` |
| German | `de` | Italian | `it` |
| Portuguese | `pt` | Russian | `ru` |
| Japanese | `ja` | Korean | `ko` |
| Chinese | `zh` | Arabic | `ar` |
| Bengali | `bn` | Marathi | `mr` |
| Tamil | `ta` | Telugu | `te` |
| Gujarati | `gu` | Punjabi | `pa` |
| Urdu | `ur` | | |

## Personality Types

Choose from these built-in personalities:
- **Family**: Brother, Sister, Mother, Father, Grandmother, Grandfather
- **Romantic**: Lover, Girlfriend, Boyfriend
- **Social**: Friend

## Characteristics

Customize your persona with these traits:
- **Emotional**: Caring, Loving, Supportive, Understanding, Patient
- **Social**: Funny, Talkative, Quiet, Well-mannered, Confident
- **Lifestyle**: Honest, Adventurous, Hardworking
- **Custom**: Add your own with `custom_characteristics`

## API Integration

### Groq Integration

The server uses Groq's powerful Llama 3.3 70B model for generating responses:
- **Model**: `llama3-70b-8192`
- **Max Tokens**: 512 (configurable)
- **Temperature**: 0.8 (configurable)
- **Timeout**: 60 seconds

### Translation Integration

Automatic language detection and translation using:
- **Language Detection**: `langdetect` library
- **Translation**: `deep-translator` with Google Translate
- **Supported**: 20+ languages with automatic fallback

## Deployment

### Using Render (Recommended)

The included [`render.yaml`](render.yaml) makes deployment simple:

1. Push your code to GitHub
2. Connect your GitHub repo to Render
3. Environment variables will be automatically configured
4. Your server will be available at `https://your-app.onrender.com`

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8086
CMD ["python", "new_one.py"]
```

## Development

### Project Structure

```
Your_LOVER/
├── new_one.py              # Main MCP server
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── .env.example           # Environment template
├── .env                   # Your environment (create this)
└── mcp-starter/           # Example MCP implementations
    ├── mcp-bearer-token/  # Bearer auth examples
    ├── mcp-google-oauth/  # Google OAuth example
    └── mcp-oauth-github/  # GitHub OAuth example
```

### Key Dependencies

- **FastMCP**: MCP server framework
- **deep-translator**: Language translation
- **langdetect**: Language detection
- **requests**: HTTP client for Groq API
- **python-dotenv**: Environment variable management

## Security

- ✅ Bearer token authentication
- ✅ Environment variable security
- ✅ Input validation
- ✅ Error handling
- ✅ Rate limiting via Groq API
- ✅ HTTPS requirement for production

## Troubleshooting

### Common Issues

1. **"GROQ_API_KEY is not set"**
   - Ensure your `.env` file contains a valid Groq API key

2. **"Please set AUTH_TOKEN in your .env file"**
   - Add your authentication token to the `.env` file

3. **Connection timeout**
   - Check your internet connection and Groq API status

4. **Translation errors**
   - Falls back to original text if translation fails

### Debug Mode

Enable detailed logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Puch AI Discord**: https://discord.gg/VMCnMvYx
- **MCP Documentation**: https://puch.ai/mcp
- **Groq API Docs**: https://console.groq.com/docs

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Groq](https://groq.com/) Llama 3.3 70B
- Translation by [deep-translator](https://github.com/nidhaloff/deep-translator)
- MCP examples inspired by [mcp-starter](mcp-starter/)

---

**Happy chatting! 💬🚀**

Use the hashtag `#PersonalityChatMCP` when sharing your experiences!