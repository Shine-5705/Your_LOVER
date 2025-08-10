# WhatsApp Personality MCP Server Development Instructions

This project is a Model Context Protocol (MCP) server that creates personality-based AI companions for WhatsApp interactions.

## Key Features
- Multiple personality types (family, romantic, friends)
- Customizable characteristics and traits
- Human-like conversation responses
- Conversation memory and context awareness
- Emotional intelligence and support detection

## Architecture
- TypeScript-based MCP server
- Uses @modelcontextprotocol/sdk for MCP functionality
- Zod for schema validation
- In-memory conversation storage

## Development Guidelines
1. Follow TypeScript best practices
2. Use proper error handling with McpError
3. Validate all inputs with Zod schemas
4. Maintain conversation state and history
5. Generate contextually appropriate responses

## Testing the Server
1. Build: `npm run build`
2. Run: `npm start`
3. Use MCP client to test tools
4. Debug with VS Code MCP integration

## SDK Reference
Model Context Protocol: https://github.com/modelcontextprotocol/create-python-server
