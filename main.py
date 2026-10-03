# main.py
import os
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from google_calender_mcp import get_calendar_agent
from email_mcp import get_email_agent

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def main():
    print("⚡ Initializing Multi-Agent System...")

    # Load sub-agents
    calendar_agent = await get_calendar_agent()
    email_agent = await get_email_agent()

    # Wrap sub-agents as tools for the supervisor
    @tool
    async def calendar_tool(query: str) -> str:
        """Use this tool for calendar tasks: scheduling, reading meetings, updating/deleting events."""
        result = await calendar_agent.ainvoke({"messages": [("user", query)]})
        return result["messages"][-1].content

    @tool
    async def email_tool(query: str) -> str:
        """Use this tool for email tasks: checking inbox, sending emails, drafting messages."""
        result = await email_agent.ainvoke({"messages": [("user", query)]})
        return result["messages"][-1].content

    supervisor_tools = [calendar_tool, email_tool]
    
    supervisor_model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=GROQ_API_KEY
    )

    supervisor_prompt = (
        "You are the main Assistant Supervisor. "
        "Route calendar queries to calendar_tool and email queries to email_tool. "
        "If a query requires both (e.g., 'Check my meetings today and email the schedule to Alex'), "
        "call both tools in sequence and present a unified summary."
    )

    supervisor = create_react_agent(supervisor_model, supervisor_tools, prompt=supervisor_prompt)

    print("🤖 Supervisor System Ready!")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = await supervisor.ainvoke({"messages": [("user", user_input)]})
        print(f"\n🤖 Assistant: {response['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())