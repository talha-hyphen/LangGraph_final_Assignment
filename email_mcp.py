# email_mcp.py
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

credentials_path = os.path.abspath("gcp-oauth.keys.json")

async def get_email_agent():
    client = MultiServerMCPClient(
        {
            "gmail": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "-s", "@gongrzhe/server-gmail-autoauth-mcp", "start"],
                "env": {
                    "GOOGLE_OAUTH_CREDENTIALS": credentials_path
                },
            }
        }
    )

    tools = await client.get_tools()

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    system_prompt = (
        "You are an assistant that manages Gmail emails. "
        "Use the provided tools to read, search, draft, or send emails. "
        "Execute actions directly and use smart defaults for missing details."
    )

    return create_react_agent(model, tools, prompt=system_prompt)