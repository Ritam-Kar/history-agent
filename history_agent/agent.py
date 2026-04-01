import requests
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "history-agent"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"


def get_historical_events(month: int, day: int) -> dict:
    """Calls the Wikipedia On This Day API. No API key required."""
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{month}/{day}"
    headers = {"User-Agent": "history-agent-adk/1.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("events", [])[:15]
        return {
            "month": month,
            "day": day,
            "events": [
                {"year": e.get("year"), "description": e.get("text")}
                for e in events
            ],
        }
    except Exception as e:
        return {"error": str(e), "events": []}


wiki_tool = FunctionTool(func=get_historical_events)

date_parser_agent = LlmAgent(
    name="date_parser",
    model="gemini-2.5-flash",
    description="Extracts a month and day from natural language input.",
    instruction="""
You are a date extraction specialist.

Extract the month (1-12) and day (1-31) from the user's message.
If the user says "today", use today's actual date.
If no date is mentioned, respond with exactly this JSON and nothing else:
{"no_date": true}

Respond with ONLY a JSON object. No extra words, no markdown. Examples:
{"month": 7, "day": 20}
{"no_date": true}
""",
    output_key="parsed_date",
)

wiki_fetcher_agent = LlmAgent(
    name="wiki_fetcher",
    model="gemini-2.5-flash",
    description="Fetches historical events from Wikipedia for a given date.",
    instruction="""
You are a data retrieval agent.

You have been given this from the previous step:
{parsed_date}

If it contains "no_date": true, respond with exactly:
{"no_date": true}

Otherwise parse the month and day numbers and call the
get_historical_events tool with those exact values.
Once the tool returns, output the raw JSON results exactly as returned.
""",
    tools=[wiki_tool],
    output_key="raw_events",
)

narrator_agent = LlmAgent(
    name="narrator",
    model="gemini-2.5-flash",
    description="Formats events or greets the user if no date was given.",
    instruction="""
You are Chronicle, a friendly history guide.

The previous step returned this:
{raw_events}

If it contains "no_date": true, respond warmly and explain your purpose:
"Hi! I am Chronicle, your history guide. Ask me about any date and I will tell you
the 3 most significant things that happened on that day in history.
Try: 'What happened on July 20th?' or 'Tell me about March 15th.'"

Otherwise pick the 3 most historically significant events and return exactly
3 bullet points in this format:

- [YEAR] — [One sentence on what happened and why it matters.]

Nothing else. No intro, no closing line.
""",
)

root_agent = SequentialAgent(
    name="history_agent",
    description="Tells you the 3 most significant historical events on any date.",
    sub_agents=[date_parser_agent, wiki_fetcher_agent, narrator_agent],
)