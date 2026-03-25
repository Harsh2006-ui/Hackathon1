# agent.py

from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY
from membrain_client import search_memory, add_memory

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")


def response_text(response):
    if not response:
        return ""

    if hasattr(response, "output_text") and response.output_text:
        return response.output_text

    chunks = []
    for item in getattr(response, "output", []) or []:
        if isinstance(item, dict) and item.get("type") == "text":
            chunks.append(item.get("text", ""))
        elif hasattr(item, "text") and item.text:
            chunks.append(item.text)

    return "\n".join(chunks).strip()


def run_agent(user_input):

    # ✅ STEP 0 — HANDLE DATE DIRECTLY (NO AI)
    today = datetime.now().strftime("%B %d, %Y")

    if "date" in user_input.lower():
        memory = search_memory(user_input)
        return f"Today's date is {today}", None, memory

    # 🔍 STEP 1 — SEARCH MEMORY
    memory = search_memory(user_input)
    context = str(memory.get("interpreted", {}))

    # 🧠 STEP 2 — GENERATE RESPONSE
    prompt = f"""
You are a personal AI.

IMPORTANT:
You MUST use this date.
Current date: {today}

Use memory if relevant.

Memory:
{context}

User:
{user_input}

Answer:
"""

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        answer = response_text(response)
    except Exception as e:
        return f"Error: {e}", None, memory

    # 🧾 STEP 3 — FACT EXTRACTION
    fact_prompt = f"""
Extract ONLY if it's useful long-term:

Allowed:
- Preferences
- Decisions
- Constraints

If nothing useful → return NONE

User: {user_input}
AI: {answer}
"""

    try:
        fact_response = client.responses.create(
            model="gpt-4o-mini",
            input=fact_prompt
        )
        fact = response_text(fact_response).strip()
    except Exception:
        fact = None

    # 💾 STEP 4 — STORE MEMORY
    if fact and fact.upper() != "NONE":
        result = add_memory(
            content=fact,
            tags=["scope.user"]
        )

    return answer, fact, memory
