import os
import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

# Create FastAPI app
app = FastAPI()

# Create MCP server
mcp = FastMCP("Turing2 Personality Chat MCP 🚀")

# Mount MCP JSON-RPC at root "/"
mcp.mount_to_fastapi(app, path="/")

# Optional: simple GET endpoint for browser/health check
@app.get("/health")
def health():
    return {"status": "ok", "service": "MCP server running"}

if __name__ == "__main__":
    # Use Render's PORT (default to 10000 for local dev)
    PORT = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
