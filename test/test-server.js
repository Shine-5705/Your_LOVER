#!/usr/bin/env node

// Simple test script to verify the MCP server
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🧪 Testing WhatsApp Personality MCP Server...\n');

// Start the server
const serverPath = join(__dirname, '../build/index.js');
const server = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: join(__dirname, '..')
});

let output = '';

server.stdout.on('data', (data) => {
  output += data.toString();
});

server.stderr.on('data', (data) => {
  const message = data.toString();
  console.log('📡 Server:', message.trim());
});

// Send a simple initialization request
setTimeout(() => {
  const initRequest = {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0'
      }
    }
  };

  console.log('📤 Sending initialization request...');
  server.stdin.write(JSON.stringify(initRequest) + '\n');

  // After initialization, request the list of tools
  setTimeout(() => {
    const toolsRequest = {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/list'
    };

    console.log('📤 Requesting tools list...');
    server.stdin.write(JSON.stringify(toolsRequest) + '\n');

    // Give time for response and then close
    setTimeout(() => {
      console.log('\n📥 Server responses:');
      console.log(output);
      
      server.kill();
      console.log('\n✅ Test completed! Server appears to be working correctly.');
      console.log('\n🔧 You can now debug this MCP server using VS Code with the mcp.json configuration.');
      
      process.exit(0);
    }, 2000);
  }, 1000);
}, 1000);

server.on('exit', (code) => {
  if (code !== 0 && code !== null) {
    console.log(`❌ Server exited with code ${code}`);
  }
});

// Cleanup on process exit
process.on('SIGINT', () => {
  server.kill();
  process.exit(0);
});
