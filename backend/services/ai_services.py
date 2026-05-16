import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def decide_action(
    event: str,
    memory_summary: str,
    instructions: list[str]
):

    formatted_instructions = "\n".join(
        f"- {instruction}"
        for instruction in instructions
    )

    prompt = f"""
You are an order supervisor. Decide what action to take based on the event.

Event: {event}

Memory:
{memory_summary}

Instructions:
{formatted_instructions}

Rules:
- order_created: no_action, just monitor
- payment_confirmed: no_action, all good
- payment_failed: message_payments_team only
- shipment_created: no_action, all good
- shipment_delayed: message_logistics_team and message_customer
- delivered: no_action, order complete
- refund_requested: create_internal_note and message_payments_team
- customer_message_received: message_customer only
- fulfillment_issue: message_fulfillment_team only

Only trigger actions that make sense for the event.

Return JSON:
{{"actions":["..."],"reason":"..."}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an AI workflow engine."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=200
    )

    text = response.choices[0].message.content.strip()

    try:
        return json.loads(text)

    except Exception:
        return {
            "actions": ["no_action"],
            "reason": "Failed to parse AI response"
        }


def compress_memory(memory: str) -> str:

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Compress workflow history into structured operational memory. "
                    "Treat delays, failures, escalations, pending payments, "
                    "refunds, warehouse problems, cancellations, and customer complaints  as issues. "
                    "Use only short keywords or short phrases. "
                    "Preserve all statuses, issues, actions, and instructions."
                )
            },
            {
                "role": "user",
                "content": f"""
            Return ONLY this format:

            Statuses: <all statuses in order separated by ->>
            Issues: <all detected issues separated by commas>
            Actions: <important actions separated by commas>
            Instructions: <active instructions separated by commas>
            Last Event: <latest event>

            Workflow History:
            {memory}
            """
            
            }
        ]
    )

    return response.choices[0].message.content.strip()