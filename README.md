# WhatsApp Personality MCP Server

A Model Context Protocol (MCP) server that provides personality-based AI companions for WhatsApp interactions. This server allows users to create and interact with different relationship personalities such as family members, romantic partners, and friends, each with customizable characteristics.

## Features

### Personality Types
- **Family Members**: Brother, Sister, Mother, Father, Grandmother, Grandfather
- **Romantic Partners**: Girlfriend, Boyfriend, Lover
- **Social**: Friend

### Customizable Characteristics
- **Basic Info**: Nationality, Language, Age
- **Personality Traits**: Caring, Well-mannered, Understanding, Supportive, Protective, Wise, Playful, Romantic
- **Communication Style**: Tone, Formal/Casual preferences
- **Lifestyle**: Working status, Interests and hobbies
- **Behavior**: Willingness to share problems, communication preferences
- **Custom Traits**: Additional personality descriptions

### Available Tools

1. **create_personality** - Create a new personality companion with specific characteristics
2. **chat_with_companion** - Send messages and receive human-like responses
3. **get_conversation_info** - Get details about active conversations
4. **list_active_conversations** - View all active conversations
5. **end_conversation** - End an active conversation

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build the project:
   ```bash
   npm run build
   ```

## Usage

### Building and Running
```bash
# Build the project
npm run build

# Start the server
npm start

# Development mode (build + run)
npm run dev
```

### Example Usage

1. **Create a Personality Companion**:
   ```json
   {
     "tool": "create_personality",
     "arguments": {
       "conversationId": "conv_001",
       "personalityType": "girlfriend",
       "companionName": "Sarah",
       "characteristics": {
         "nationality": "American",
         "language": "English",
         "tone": "caring and sweet",
         "caring": true,
         "wellMannered": true,
         "understanding": true,
         "working": true,
         "shareProblems": true,
         "age": 25,
         "interests": ["cooking", "reading", "movies"],
         "communicationStyle": "warm and supportive",
         "romantic": true,
         "supportive": true
       }
     }
   }
   ```

2. **Chat with Your Companion**:
   ```json
   {
     "tool": "chat_with_companion",
     "arguments": {
       "conversationId": "conv_001",
       "message": "Hi Sarah, I had a rough day at work today"
     }
   }
   ```

3. **List Active Conversations**:
   ```json
   {
     "tool": "list_active_conversations",
     "arguments": {}
   }
   ```

## Configuration

The server can be configured with VS Code by creating an `mcp.json` file in the `.vscode` folder:

```json
{
  "servers": {
    "whatsapp-personality-server": {
      "type": "stdio",
      "command": "node",
      "args": ["build/index.js"]
    }
  }
}
```

## Personality Examples

### Caring Girlfriend
```json
{
  "personalityType": "girlfriend",
  "companionName": "Emma",
  "characteristics": {
    "nationality": "British",
    "language": "English",
    "tone": "warm and caring",
    "caring": true,
    "wellMannered": true,
    "understanding": true,
    "working": true,
    "shareProblems": true,
    "age": 24,
    "interests": ["art", "travel", "yoga"],
    "romantic": true,
    "supportive": true
  }
}
```

### Wise Grandfather
```json
{
  "personalityType": "grandfather",
  "companionName": "George",
  "characteristics": {
    "nationality": "Italian",
    "language": "English with Italian expressions",
    "tone": "wise and gentle",
    "caring": true,
    "understanding": true,
    "wise": true,
    "protective": true,
    "age": 72,
    "interests": ["gardening", "history", "cooking"],
    "communicationStyle": "storytelling and advice-giving"
  }
}
```

### Supportive Brother
```json
{
  "personalityType": "brother",
  "companionName": "Alex",
  "characteristics": {
    "nationality": "Canadian",
    "language": "English",
    "tone": "casual and supportive",
    "understanding": true,
    "supportive": true,
    "protective": true,
    "playful": true,
    "working": true,
    "age": 28,
    "interests": ["sports", "gaming", "music"],
    "communicationStyle": "friendly and encouraging"
  }
}
```

## Features in Detail

### Human-like Responses
The server generates contextually appropriate responses based on:
- Personality type and relationship dynamics
- Individual characteristics and traits
- Conversation history and context
- User's emotional state and needs

### Conversation Memory
Each conversation maintains:
- Complete message history
- Personality settings
- Companion information
- Timestamps for all interactions

### Emotional Intelligence
Companions can:
- Detect when users need support
- Provide appropriate emotional responses
- Share their own problems when configured
- Adapt communication style to user's needs

## Development

This project uses:
- TypeScript for type safety
- Model Context Protocol (MCP) SDK
- Zod for schema validation
- Node.js runtime

## License

MIT License - feel free to use and modify as needed.

## SDK Reference

For more information about the Model Context Protocol, visit: https://github.com/modelcontextprotocol/create-python-server
