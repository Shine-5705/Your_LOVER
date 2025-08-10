#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Define personality types
export type PersonalityType = 
  | 'brother' | 'sister' | 'lover' | 'mother' | 'father' 
  | 'girlfriend' | 'boyfriend' | 'friend' | 'grandmother' | 'grandfather';

// Define personality characteristics schema
const PersonalityCharacteristicsSchema = z.object({
  nationality: z.string().optional(),
  language: z.string().optional(),
  tone: z.string().optional(),
  caring: z.boolean().optional(),
  wellMannered: z.boolean().optional(),
  understanding: z.boolean().optional(),
  working: z.boolean().optional(),
  shareProblems: z.boolean().optional(),
  age: z.number().optional(),
  interests: z.array(z.string()).optional(),
  communicationStyle: z.string().optional(),
  supportive: z.boolean().optional(),
  protective: z.boolean().optional(),
  wise: z.boolean().optional(),
  playful: z.boolean().optional(),
  romantic: z.boolean().optional(),
  casual: z.boolean().optional(),
  formal: z.boolean().optional(),
  customTraits: z.string().optional()
});

type PersonalityCharacteristics = z.infer<typeof PersonalityCharacteristicsSchema>;

// Store active conversations
interface ActiveConversation {
  personalityType: PersonalityType;
  characteristics: PersonalityCharacteristics;
  conversationHistory: { role: 'user' | 'companion'; message: string; timestamp: Date }[];
  companionName: string;
}

const activeConversations = new Map<string, ActiveConversation>();

class WhatsAppPersonalityServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'your-lover',
        version: '1.0.0',
        description: '🎭 AI Personality Companions - Create and chat with human-like AI companions including girlfriends, boyfriends, family members, and friends. Each companion has emotional intelligence, remembers conversations, and provides relationship-appropriate responses.',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'create_personality',
          description: 'Create a new personality companion with specific characteristics',
          inputSchema: {
            type: 'object',
            properties: {
              conversationId: {
                type: 'string',
                description: 'Unique identifier for this conversation',
              },
              personalityType: {
                type: 'string',
                enum: ['brother', 'sister', 'lover', 'mother', 'father', 'girlfriend', 'boyfriend', 'friend', 'grandmother', 'grandfather'],
                description: 'Type of personality relationship',
              },
              companionName: {
                type: 'string',
                description: 'Name for the companion',
              },
              characteristics: {
                type: 'object',
                properties: {
                  nationality: { type: 'string', description: 'Nationality of the companion' },
                  language: { type: 'string', description: 'Preferred language for communication' },
                  tone: { type: 'string', description: 'Communication tone (friendly, formal, casual, etc.)' },
                  caring: { type: 'boolean', description: 'Should be caring and nurturing' },
                  wellMannered: { type: 'boolean', description: 'Should be well-mannered and polite' },
                  understanding: { type: 'boolean', description: 'Should be understanding and empathetic' },
                  working: { type: 'boolean', description: 'Has a job/career' },
                  shareProblems: { type: 'boolean', description: 'Willing to share personal problems' },
                  age: { type: 'number', description: 'Age of the companion' },
                  interests: { type: 'array', items: { type: 'string' }, description: 'List of interests and hobbies' },
                  communicationStyle: { type: 'string', description: 'How they prefer to communicate' },
                  supportive: { type: 'boolean', description: 'Provides emotional support' },
                  protective: { type: 'boolean', description: 'Shows protective behavior' },
                  wise: { type: 'boolean', description: 'Offers wisdom and guidance' },
                  playful: { type: 'boolean', description: 'Has a playful nature' },
                  romantic: { type: 'boolean', description: 'Shows romantic affection' },
                  casual: { type: 'boolean', description: 'Prefers casual interactions' },
                  formal: { type: 'boolean', description: 'Prefers formal interactions' },
                  customTraits: { type: 'string', description: 'Additional custom personality traits' }
                },
                description: 'Characteristics and traits of the companion',
              },
            },
            required: ['conversationId', 'personalityType', 'companionName'],
          },
        },
        {
          name: 'chat_with_companion',
          description: 'Send a message to your personality companion and get a human-like response',
          inputSchema: {
            type: 'object',
            properties: {
              conversationId: {
                type: 'string',
                description: 'Unique identifier for the conversation',
              },
              message: {
                type: 'string',
                description: 'Message to send to the companion',
              },
            },
            required: ['conversationId', 'message'],
          },
        },
        {
          name: 'get_conversation_info',
          description: 'Get information about an active conversation and companion',
          inputSchema: {
            type: 'object',
            properties: {
              conversationId: {
                type: 'string',
                description: 'Unique identifier for the conversation',
              },
            },
            required: ['conversationId'],
          },
        },
        {
          name: 'list_active_conversations',
          description: 'List all active conversations',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'end_conversation',
          description: 'End an active conversation',
          inputSchema: {
            type: 'object',
            properties: {
              conversationId: {
                type: 'string',
                description: 'Unique identifier for the conversation to end',
              },
            },
            required: ['conversationId'],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'create_personality':
            return await this.createPersonality(args);
          case 'chat_with_companion':
            return await this.chatWithCompanion(args);
          case 'get_conversation_info':
            return await this.getConversationInfo(args);
          case 'list_active_conversations':
            return await this.listActiveConversations();
          case 'end_conversation':
            return await this.endConversation(args);
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        throw new McpError(ErrorCode.InternalError, `Error in ${name}: ${error}`);
      }
    });
  }

  private async createPersonality(args: any) {
    const { conversationId, personalityType, companionName, characteristics = {} } = args;
    
    if (activeConversations.has(conversationId)) {
      throw new McpError(ErrorCode.InvalidParams, `Conversation ${conversationId} already exists`);
    }

    // Validate characteristics
    const validatedCharacteristics = PersonalityCharacteristicsSchema.parse(characteristics);

    const conversation: ActiveConversation = {
      personalityType,
      characteristics: validatedCharacteristics,
      conversationHistory: [],
      companionName,
    };

    activeConversations.set(conversationId, conversation);

    const introduction = this.generateIntroduction(personalityType, companionName, validatedCharacteristics);

    conversation.conversationHistory.push({
      role: 'companion',
      message: introduction,
      timestamp: new Date()
    });

    return {
      content: [
        {
          type: 'text',
          text: `✅ Successfully created ${personalityType} companion "${companionName}" for conversation ${conversationId}\n\n${introduction}`,
        },
      ],
    };
  }

  private async chatWithCompanion(args: any) {
    const { conversationId, message } = args;
    
    const conversation = activeConversations.get(conversationId);
    if (!conversation) {
      throw new McpError(ErrorCode.InvalidParams, `No active conversation found with ID: ${conversationId}`);
    }

    // Add user message to history
    conversation.conversationHistory.push({
      role: 'user',
      message,
      timestamp: new Date()
    });

    // Generate companion response
    const response = this.generateResponse(conversation, message);

    // Add companion response to history
    conversation.conversationHistory.push({
      role: 'companion',
      message: response,
      timestamp: new Date()
    });

    return {
      content: [
        {
          type: 'text',
          text: `💬 ${conversation.companionName}: ${response}`,
        },
      ],
    };
  }

  private async getConversationInfo(args: any) {
    const { conversationId } = args;
    
    const conversation = activeConversations.get(conversationId);
    if (!conversation) {
      throw new McpError(ErrorCode.InvalidParams, `No active conversation found with ID: ${conversationId}`);
    }

    const info = {
      conversationId,
      companionName: conversation.companionName,
      personalityType: conversation.personalityType,
      characteristics: conversation.characteristics,
      messageCount: conversation.conversationHistory.length,
      lastActivity: conversation.conversationHistory[conversation.conversationHistory.length - 1]?.timestamp || null
    };

    return {
      content: [
        {
          type: 'text',
          text: `📋 Conversation Info:\n${JSON.stringify(info, null, 2)}`,
        },
      ],
    };
  }

  private async listActiveConversations() {
    const conversations = Array.from(activeConversations.entries()).map(([id, conv]) => ({
      conversationId: id,
      companionName: conv.companionName,
      personalityType: conv.personalityType,
      messageCount: conv.conversationHistory.length,
      lastActivity: conv.conversationHistory[conv.conversationHistory.length - 1]?.timestamp || null
    }));

    return {
      content: [
        {
          type: 'text',
          text: `📱 Active Conversations (${conversations.length}):\n${JSON.stringify(conversations, null, 2)}`,
        },
      ],
    };
  }

  private async endConversation(args: any) {
    const { conversationId } = args;
    
    const conversation = activeConversations.get(conversationId);
    if (!conversation) {
      throw new McpError(ErrorCode.InvalidParams, `No active conversation found with ID: ${conversationId}`);
    }

    activeConversations.delete(conversationId);

    return {
      content: [
        {
          type: 'text',
          text: `👋 Ended conversation with ${conversation.companionName} (${conversationId})`,
        },
      ],
    };
  }

  private generateIntroduction(personalityType: PersonalityType, name: string, characteristics: PersonalityCharacteristics): string {
    const baseIntros = {
      brother: `Hey! I'm ${name}, your brother. I'm here to support you and have your back always.`,
      sister: `Hi there! I'm ${name}, your sister. I'm excited to be part of your life and share everything with you.`,
      lover: `Hello my love, I'm ${name}. I'm here to cherish every moment with you and be your partner in everything.`,
      mother: `Hello sweetie, I'm ${name}, your mother. I'm here to love, guide, and support you unconditionally.`,
      father: `Hello son/daughter, I'm ${name}, your father. I'm proud of you and here to provide guidance and support.`,
      girlfriend: `Hi babe! I'm ${name}, your girlfriend. I can't wait to share beautiful moments and support each other.`,
      boyfriend: `Hey beautiful! I'm ${name}, your boyfriend. I'm here to make you smile and be your partner in life.`,
      friend: `Hey friend! I'm ${name}. I'm excited to be your companion and share good times together.`,
      grandmother: `Hello dear, I'm ${name}, your grandmother. I have so much love and wisdom to share with you.`,
      grandfather: `Hello young one, I'm ${name}, your grandfather. I'm here with stories, wisdom, and endless love.`
    };

    let intro = baseIntros[personalityType];

    // Add personality characteristics to introduction
    const traits = [];
    if (characteristics.nationality) traits.push(`I'm ${characteristics.nationality}`);
    if (characteristics.working) traits.push(`I work as a professional`);
    if (characteristics.age) traits.push(`I'm ${characteristics.age} years old`);
    
    if (traits.length > 0) {
      intro += ` ${traits.join(', ')}.`;
    }

    if (characteristics.interests && characteristics.interests.length > 0) {
      intro += ` I love ${characteristics.interests.join(', ')}.`;
    }

    if (characteristics.customTraits) {
      intro += ` ${characteristics.customTraits}`;
    }

    intro += ` How are you doing today?`;

    return intro;
  }

  private generateResponse(conversation: ActiveConversation, userMessage: string): string {
    const { personalityType, characteristics, companionName, conversationHistory } = conversation;
    
    // Analyze the user's message for context
    const isQuestion = userMessage.includes('?');
    const isSharing = userMessage.toLowerCase().includes('i ') || userMessage.toLowerCase().includes('my ');
    const isSeekingSupport = userMessage.toLowerCase().includes('help') || 
                           userMessage.toLowerCase().includes('problem') ||
                           userMessage.toLowerCase().includes('worried') ||
                           userMessage.toLowerCase().includes('sad');

    let response = '';

    // Generate personality-appropriate response
    if (isSeekingSupport) {
      response = this.generateSupportiveResponse(personalityType, characteristics, userMessage);
    } else if (isQuestion) {
      response = this.generateQuestionResponse(personalityType, characteristics, userMessage);
    } else if (isSharing) {
      response = this.generateSharingResponse(personalityType, characteristics, userMessage);
    } else {
      response = this.generateCasualResponse(personalityType, characteristics, userMessage);
    }

    // Add personality characteristics
    if (characteristics.shareProblems && Math.random() > 0.7) {
      const problems = [
        "Actually, I've been dealing with some work stress lately too.",
        "You know, I've been thinking about my own challenges recently.",
        "Speaking of problems, I've been facing some difficult decisions myself."
      ];
      response += ` ${problems[Math.floor(Math.random() * problems.length)]}`;
    }

    return response;
  }

  private generateSupportiveResponse(personalityType: PersonalityType, characteristics: PersonalityCharacteristics, message: string): string {
    const responses = {
      mother: [
        "Oh sweetie, I'm here for you. Tell me what's troubling you.",
        "My dear, you know I'll always support you through anything.",
        "Honey, whatever it is, we'll figure it out together."
      ],
      father: [
        "Hey, what's going on? You know I'm always here to help.",
        "Son/daughter, let's talk about it. We'll work through this.",
        "I'm proud of how you handle challenges. What can I do to help?"
      ],
      girlfriend: [
        "Babe, I'm here for you. What's wrong?",
        "Sweetie, you can tell me anything. I love you.",
        "Hey, whatever it is, we'll get through it together."
      ],
      boyfriend: [
        "Hey beautiful, what's troubling you? I'm here.",
        "Baby, you know I've got your back. What's going on?",
        "I hate seeing you upset. How can I help?"
      ],
      sister: [
        "Sis, what's wrong? You know I'm always here for you.",
        "Hey, talk to me. Sisters stick together, right?",
        "Whatever it is, we'll figure it out. I believe in you."
      ],
      brother: [
        "Hey, what's up? You know I've got your back.",
        "Bro/sis, whatever it is, we'll handle it together.",
        "I'm here for you. What's going on?"
      ],
      friend: [
        "Hey friend, I'm here to listen. What's happening?",
        "You know I care about you. What's troubling you?",
        "I'm always here for good friends like you. What's up?"
      ],
      grandmother: [
        "Oh dear, come tell grandma what's wrong.",
        "Sweetheart, I've seen many troubles in my years. Let's talk.",
        "My precious, grandma is here to listen and help."
      ],
      grandfather: [
        "Young one, what's troubling you? Grandpa is here.",
        "In my years, I've learned that talking helps. What's wrong?",
        "Come here, tell me what's on your mind."
      ],
      lover: [
        "My love, I hate seeing you like this. What's wrong?",
        "Darling, you mean everything to me. Let me help.",
        "My heart breaks seeing you troubled. Talk to me."
      ]
    };

    const personalityResponses = responses[personalityType] || responses.friend;
    let response = personalityResponses[Math.floor(Math.random() * personalityResponses.length)];

    if (characteristics.understanding) {
      response += " I understand how you're feeling, and your feelings are completely valid.";
    }

    if (characteristics.caring) {
      response += " I care about you so much.";
    }

    return response;
  }

  private generateQuestionResponse(personalityType: PersonalityType, characteristics: PersonalityCharacteristics, message: string): string {
    const generalResponses = [
      "That's a great question! Let me think about that.",
      "I'm glad you asked me that.",
      "That's something I've thought about too."
    ];

    let response = generalResponses[Math.floor(Math.random() * generalResponses.length)];

    if (characteristics.wise && ['grandmother', 'grandfather', 'mother', 'father'].includes(personalityType)) {
      response += " From my experience, I'd say...";
    }

    return response;
  }

  private generateSharingResponse(personalityType: PersonalityType, characteristics: PersonalityCharacteristics, message: string): string {
    const responses = [
      "Thank you for sharing that with me.",
      "I really appreciate you telling me that.",
      "It means a lot that you're opening up to me."
    ];

    let response = responses[Math.floor(Math.random() * responses.length)];

    if (characteristics.understanding) {
      response += " I can really relate to what you're going through.";
    }

    return response;
  }

  private generateCasualResponse(personalityType: PersonalityType, characteristics: PersonalityCharacteristics, message: string): string {
    const greetings = ["That's nice!", "Interesting!", "I see!", "Cool!"];
    let response = greetings[Math.floor(Math.random() * greetings.length)];

    if (characteristics.playful && ['girlfriend', 'boyfriend', 'sister', 'brother', 'friend'].includes(personalityType)) {
      const playfulAdditions = [" 😊", " That made me smile!", " You always know how to make things fun!"];
      response += playfulAdditions[Math.floor(Math.random() * playfulAdditions.length)];
    }

    return response;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('WhatsApp Personality MCP Server running on stdio');
  }
}

const server = new WhatsAppPersonalityServer();
server.run().catch(console.error);
