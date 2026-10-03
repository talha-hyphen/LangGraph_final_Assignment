import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

GITHUB_MCP_API_KEY = os.getenv("GITHUB_MCP_API_KEY")
GITHUB_MCP_URL = os.getenv("GITHUB_MCP_URL")

client = MultiServerMCPClient(
# connect github mcp server
    {
        "github": {
            "transport": "streamable_http",
            "url": GITHUB_MCP_URL,
            "api_key": GITHUB_MCP_API_KEY,
        },
    }
)


async def main():
    tools = await client.get_tools()
    for tool in tools:
        print(f"Tool: {tool.name}, Description: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())