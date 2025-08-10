#!/usr/bin/env node

// Demo script showing how to use the WhatsApp Personality MCP Server
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🎭 WhatsApp Personality MCP Server Demo\n');

// Start the server
const serverPath = join(__dirname, '../build/index.js');
const server = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: join(__dirname, '..')
});

let messageId = 1;

function sendMCPRequest(method, params = {}) {
  const request = {
    jsonrpc: '2.0',
    id: messageId++,
    method: method,
    params: params
  };
  
  console.log(`📤 Sending: ${method}`);
  server.stdin.write(JSON.stringify(request) + '\n');
}

let responses = '';
server.stdout.on('data', (data) => {
  responses += data.toString();
});

server.stderr.on('data', (data) => {
  console.log('📡 Server:', data.toString().trim());
});

// Demo sequence
setTimeout(() => {
  console.log('1️⃣ Initializing MCP connection...');
  sendMCPRequest('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'demo-client', version: '1.0.0' }
  });
}, 500);

setTimeout(() => {
  console.log('2️⃣ Getting available tools...');
  sendMCPRequest('tools/list');
}, 1500);

setTimeout(() => {
  console.log('3️⃣ Creating a girlfriend personality...');
  sendMCPRequest('tools/call', {
    name: 'create_personality',
    arguments: {
      conversationId: 'demo_girlfriend',
      personalityType: 'girlfriend',
      companionName: 'Sarah',
      characteristics: {
        nationality: 'American',
        age: 25,
        caring: true,
        understanding: true,
        romantic: true,
        interests: ['cooking', 'movies', 'travel'],
        customTraits: 'She loves surprises and always remembers important dates'
      }
    }
  });
}, 2500);

setTimeout(() => {
  console.log('4️⃣ Chatting with Sarah...');
  sendMCPRequest('tools/call', {
    name: 'chat_with_companion',
    arguments: {
      conversationId: 'demo_girlfriend',
      message: 'Hi Sarah! I had a really tough day at work today. My boss was being really difficult.'
    }
  });
}, 3500);

setTimeout(() => {
  console.log('5️⃣ Creating a wise grandfather...');
  sendMCPRequest('tools/call', {
    name: 'create_personality',
    arguments: {
      conversationId: 'demo_grandpa',
      personalityType: 'grandfather',
      companionName: 'George',
      characteristics: {
        nationality: 'Italian',
        age: 75,
        wise: true,
        caring: true,
        interests: ['gardening', 'history', 'cooking'],
        customTraits: 'He has many life stories and always gives great advice'
      }
    }
  });
}, 4500);

setTimeout(() => {
  console.log('6️⃣ Asking grandpa for advice...');
  sendMCPRequest('tools/call', {
    name: 'chat_with_companion',
    arguments: {
      conversationId: 'demo_grandpa',
      message: 'Grandpa George, I need some advice. Should I take a new job opportunity that pays more but requires moving to another city?'
    }
  });
}, 5500);

setTimeout(() => {
  console.log('7️⃣ Listing all conversations...');
  sendMCPRequest('tools/call', {
    name: 'list_active_conversations',
    arguments: {}
  });
}, 6500);

setTimeout(() => {
  console.log('\n📥 All Server Responses:');
  console.log('=' * 50);
  
  // Parse and display responses nicely
  const lines = responses.split('\n').filter(line => line.trim());
  lines.forEach((line, index) => {
    try {
      const response = JSON.parse(line);
      console.log(`\n Response ${index + 1}:`);
      console.log(JSON.stringify(response, null, 2));
    } catch (e) {
      console.log(`Raw: ${line}`);
    }
  });
  
  server.kill();
  console.log('\n✅ Demo completed!');
  process.exit(0);
}, 7500);

// Cleanup
process.on('SIGINT', () => {
  server.kill();
  process.exit(0);
});
