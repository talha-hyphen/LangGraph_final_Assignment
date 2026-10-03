# google_calender_mcp.py
import os
from datetime import datetime
from tzlocal import get_localzone
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

credentials_path = os.path.abspath("gcp-oauth.keys.json")

async def get_calendar_agent():
    client = MultiServerMCPClient(
        {
            "google_calendar": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "-s", "@sudomcp/google-calendar-mcp", "start"],
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

    local_tz = str(get_localzone())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_prompt = f"""
You are an assertive assistant managing Google Calendar.
Current Local Time: {now_str} ({local_tz})

RULES:
1. Execute tools immediately when basic info is provided.
2. Default duration: 30 minutes. Default calendar: "primary".
3. Calculate relative dates ("tomorrow", "next Monday") from current time ({now_str}).
"""

    return create_react_agent(model, tools, prompt=system_prompt)