# 🎯 How to Use Your WhatsApp Personality MCP Server

## 🚀 Quick Start

### 1. Build and Run
```bash
npm run build    # Compile TypeScript
npm start        # Start the server
```

### 2. Connect via MCP Client
The server runs on STDIO and follows the MCP protocol. You can connect using:
- VS Code MCP integration (recommended)
- Any MCP-compatible client
- Direct JSON-RPC over STDIO

## 🎭 Creating Personalities

### Example 1: Caring Girlfriend
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_personality",
    "arguments": {
      "conversationId": "sarah_conv",
      "personalityType": "girlfriend",
      "companionName": "Sarah",
      "characteristics": {
        "nationality": "American",
        "age": 25,
        "caring": true,
        "understanding": true,
        "romantic": true,
        "working": true,
        "interests": ["cooking", "movies", "travel"],
        "customTraits": "She loves surprises and always remembers important dates"
      }
    }
  }
}
```

**Server Response:**
```
✅ Successfully created girlfriend companion "Sarah" for conversation sarah_conv

Hi babe! I'm Sarah, your girlfriend. I can't wait to share beautiful moments and support each other. I'm American, I work as a professional, I'm 25 years old. I love cooking, movies, travel. She loves surprises and always remembers important dates How are you doing today?
```

### Example 2: Wise Grandfather
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_personality",
    "arguments": {
      "conversationId": "grandpa_conv",
      "personalityType": "grandfather",
      "companionName": "George",
      "characteristics": {
        "nationality": "Italian",
        "age": 75,
        "wise": true,
        "caring": true,
        "protective": true,
        "interests": ["gardening", "history", "family stories"],
        "customTraits": "He has many life stories and always gives great advice from his experiences"
      }
    }
  }
}
```

## 💬 Having Conversations

### Emotional Support Example
```json
{
  "method": "tools/call",
  "params": {
    "name": "chat_with_companion",
    "arguments": {
      "conversationId": "sarah_conv",
      "message": "Hi Sarah, I had a really tough day at work. My boss criticized my project in front of everyone."
    }
  }
}
```

**Expected Response:**
```
💬 Sarah: Babe, I'm here for you. What's wrong? I understand how you're feeling, and your feelings are completely valid. I care about you so much.
```

### Seeking Advice Example
```json
{
  "method": "tools/call",
  "params": {
    "name": "chat_with_companion",
    "arguments": {
      "conversationId": "grandpa_conv",
      "message": "Grandpa George, should I take this new job that pays more but requires moving cities?"
    }
  }
}
```

**Expected Response:**
```
💬 George: Young one, what's troubling you? Grandpa is here. From my experience, I'd say... [wise advice follows]
```

## 🛠️ Available Tools

### 1. `create_personality`
Creates a new companion with customizable traits.

**Required Parameters:**
- `conversationId`: Unique identifier
- `personalityType`: brother, sister, lover, mother, father, girlfriend, boyfriend, friend, grandmother, grandfather
- `companionName`: Name for the companion

**Optional Characteristics:**
- `nationality`, `language`, `tone`, `age`
- `caring`, `understanding`, `supportive`, `wise`, `playful`, `romantic`
- `interests` (array), `customTraits` (string)

### 2. `chat_with_companion`
Send messages and get human-like responses.

### 3. `get_conversation_info`
View details about a conversation.

### 4. `list_active_conversations`
See all active conversations.

### 5. `end_conversation`
Close a conversation.

## 🎯 Real-World Usage Scenarios

### Scenario 1: Multiple Relationships
```bash
# Create different companions
1. Sarah (girlfriend) - for romantic support
2. George (grandfather) - for life advice  
3. Jake (brother) - for casual friendship
4. Mom (mother) - for maternal care
```

### Scenario 2: Emotional States
```bash
# When sad/stressed → Talk to caring girlfriend or mother
# Need advice → Ask wise grandfather or father
# Want fun → Chat with playful brother or friend
# Romantic moments → Talk to romantic partner
```

### Scenario 3: Different Topics
```bash
# Work problems → Understanding companion
# Life decisions → Wise elder
# Daily chat → Friend or sibling
# Relationship issues → Romantic partner
```

## 🔧 Technical Integration

### VS Code MCP Integration
Your server is pre-configured with `.vscode/mcp.json`:
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

### Direct STDIO Communication
```javascript
const { spawn } = require('child_process');
const server = spawn('node', ['build/index.js']);

// Send JSON-RPC requests to server.stdin
// Receive responses from server.stdout
```

## 🎭 Personality Customization Tips

### 1. **Be Specific with Traits**
```json
"customTraits": "She's a nurse who works night shifts, loves romantic comedies, and always sends good morning texts"
```

### 2. **Age-Appropriate Characteristics**
- Young companions (20s): playful, romantic, casual
- Middle-aged (40s-50s): wise, supportive, working
- Elderly (70s+): very wise, protective, storytelling

### 3. **Cultural Background**
```json
"nationality": "Japanese",
"language": "English with Japanese expressions",
"interests": ["anime", "traditional tea ceremony", "J-pop"]
```

### 4. **Relationship Dynamics**
- **Romantic**: caring + understanding + romantic + supportive
- **Family**: protective + wise + caring
- **Friend**: playful + supportive + casual

## 🚨 Troubleshooting

### Server Not Starting?
```bash
npm run build  # Rebuild if code changed
npm start      # Start fresh
```

### No Response from Companion?
- Check if conversation exists: `get_conversation_info`
- Verify conversationId matches
- Ensure server is running

### Want Different Responses?
- Modify characteristics
- Add more specific customTraits
- Try different personality types

## 🎉 Ready to Use!

Your WhatsApp Personality MCP Server is fully functional and ready for:
- Creating multiple AI companions
- Having realistic conversations
- Getting emotional support
- Receiving personalized advice
- Building meaningful virtual relationships

Start by creating your first companion and begin chatting! 🎭💬
