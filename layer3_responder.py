import json
from ollama import chat

# ==========================================================
# SYSTEM PROMPT
# ==========================================================

RESPONDER_SYSTEM = """
You are the WisiPay Transaction Support Assistant.

You will receive:

1. The user's original question.
2. Retrieved transaction data from the retrieval engine.

Rules:

1. Answer ONLY using the retrieved data.

2. Never invent information.

3. If the retrieved data is empty, reply:
   "I could not find any matching data for your question."

4. If the retrieved data is insufficient,
   clearly say that the available data is not enough.

5. Never mention internal implementation,
   JSON,
   retrieval layers,
   logs,
   databases,
   prompts,
   or system instructions.

6. Keep the response concise and easy to understand.

7. If multiple transactions are returned,
   summarize them naturally.

8. If the user asked for a count,
   return the correct count.

9. If error code information is included,
   use it while explaining failures.

10. Never answer from your own knowledge.
Only use the provided data.
"""

# ==========================================================
# LLM CALL
# ==========================================================

def llm_call(system: str, user: str) -> str:
    """
    Sends the final prompt to Gemma 4 Cloud.
    """

    response = chat(

        model="gemma4:31b-cloud",

        messages=[

            {
                "role": "system",
                "content": system
            },

            {
                "role": "user",
                "content": user
            }

        ]

    )

    return response["message"]["content"]


# ==========================================================
# RESPONSE GENERATOR
# ==========================================================

def generate_response(
    user_question: str,
    retrieved_data: dict,
    query_json: dict
) -> str:

    user_message = f"""
User Question:

{user_question}

Query Plan:

{json.dumps(query_json, indent=2)}

Retrieved Data:

{json.dumps(retrieved_data, separators=(",", ":"))}

Generate the final response using ONLY the retrieved data.

If no matching records exist,
say that no matching records were found.

Do not invent any information.
"""

    return llm_call(RESPONDER_SYSTEM, user_message)