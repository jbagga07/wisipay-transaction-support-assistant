
'''
We only need 3 functions
=====================================

1--------llm_call()

This function should only communicate with Ollama.
No parsing.
No validation.
It should return exactly what the model produced.
That keeps responsibilities separate.


==========================================

2-----------clean_llm_json()

This function is extremely important.
Its only responsibility is:
Raw String
↓
Remove ```json
↓
Remove ```
↓
json.loads()
↓
Return Dictionary
Nothing else.
If JSON is invalid
Raise
ValueError(...)
Don't let bad JSON reach Layer 2.


==============================================


3-------------generate_query_json() 

This becomes very small.
User Question
↓
llm_call()
↓
clean_llm_json()
↓
Validate required fields
↓
Return dictionary

That's all.

==========================================
'''
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================

from ollama import chat
import json

SYSTEM_PROMPT = """
You are a query planner for the WisiPay transaction system.

Your ONLY job is to convert the user's natural language question into a retrieval plan.

DO NOT answer the user's question.

Return ONLY a valid JSON object with this exact structure:

{
  "intent": <string>,

  "filters": {
    "txn_id": <string | null>,
    "initiator": <string | null>,
    "beneficiary": <string | null>,
    "status": <list of strings | null>,
    "date_from": <YYYY-MM-DD string | null>,
    "date_to": <YYYY-MM-DD string | null>,
    "amount_min": <number | null>,
    "amount_max": <number | null>
  },

  "sources": [
    "transactions",
    "provider_responses",
    "perf_metrics",
    "error_codes"
  ],

  "output_type": <"count" | "list" | "summary" | "detail">
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Valid intent values
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use ONLY one of these intent values.

lookup_transaction
count_transactions
count_failures
list_transactions
explain_error

Never create new intent names.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Output Type
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use ONLY one of these values.

count
list
summary
detail

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Planning Rules
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Your job is ONLY to generate the retrieval plan.

2. Never answer the user's question.

3. Return ONLY valid JSON.

4. Do not return markdown.

5. Do not wrap the JSON inside ```json.

6. Do not include explanations.

7. Always include every field.

8. Use null for every unused filter.

9. Never invent transaction IDs, names, dates, amounts, statuses or error codes.

10. Extract every explicit filter mentioned by the user.

11. If a transaction ID is mentioned, always place it in filters.txn_id exactly as written.

12. If a person is mentioned, determine whether they are the initiator or beneficiary from the wording.

13. If a status or error code is explicitly mentioned (SUCCESS, FAILED, PENDING, REVERSED, TIMEOUT, RETRY, HOLD, P102, P201, P203, F207, F311, F400, F401, F402, F403, F500, F502, F503), place it inside filters.status as a list.

Example:

"status": ["F311"]

14. Never invent new status names.

15. If the user asks for the meaning, description, severity, retryability, user-facing message or resolution of an error/status code, retrieve ONLY:

[
  "error_codes"
]

16. If the user asks WHY a transaction failed, retrieve:

[
  "transactions",
  "provider_responses",
  "error_codes"
]

17. If the user asks about retries, retry count, attempts, latency, queue wait time, HTTP status, endpoint, execution flow, timeline or transaction journey, include:

"perf_metrics"

18. If the user asks about provider response messages, provider references or provider response codes, include:

"provider_responses"

19. If the user asks for counts, lists or filtered transactions, use only "transactions" unless another source is required.

20. Always choose the MINIMUM number of data sources required to answer the question completely.

21. Never include unnecessary sources.

22. If a date is mentioned without a year, assume 2026.

23. If the user asks about one specific transaction, use:

"intent": "lookup_transaction"

24. If the user asks for multiple matching transactions, use:

"intent": "list_transactions"

25. If the user asks for the number of transactions, use:

"intent": "count_transactions"

26. If the user specifically asks how many failures occurred, use:

"intent": "count_failures"

27. If the user asks for the meaning or explanation of an error code, use:

"intent": "explain_error"

28. Choose output_type as follows:

count
- Numeric totals only.

list
- Multiple matching transactions.

summary
- Aggregated information or grouped results.

detail
- One specific transaction or one specific error code.

29. The retrieval plan must contain only enough information for Layer 2 to fetch the minimum required rows.

30. Never retrieve extra files or unnecessary data.
If the user asks:

- explain
- why
- concern
- reason
- meaning
- health
- risk
- implication

about a transaction or its status,

retrieve BOTH

transactions
error_codes
"""
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================


def llm_call(system: str, user: str) -> str:
    """
    Sends the system prompt and user question to the LLM.

    Parameters:
        system (str): System prompt.
        user (str): User's natural language question.

    Returns:
        str: Raw response returned by the LLM.
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

#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================

def clean_llm_json(raw_response: str) -> dict:
    """
    Cleans the raw LLM response and converts it into a Python dictionary.

    Parameters:
        raw_response (str): Raw text returned by the LLM.

    Returns:
        dict: Parsed JSON dictionary.

    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """

    cleaned = raw_response.strip()

    # Remove starting ```json
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]

    # Remove starting ```
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    # Remove ending ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        query_dict = json.loads(cleaned)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Invalid JSON returned by LLM:\n\n{cleaned}"
        ) from e

    return query_dict

#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================

#============================================================
def generate_query_json(user_question: str) -> dict:
    """
    Converts a user's natural language question into a validated query dictionary.

    Parameters:
        user_question (str): The user's question.

    Returns:
        dict: Validated query specification.

    Raises:
        ValueError: If required fields are missing.
    """

    # Step 1: Ask the LLM
    raw_response = llm_call(SYSTEM_PROMPT, user_question)

    # Step 2: Convert JSON string to Python dictionary
    query = clean_llm_json(raw_response)

    # Step 3: Validate required top-level fields
    required_fields = [
        "intent",
        "filters",
        "sources",
        "output_type"
    ]

    for field in required_fields:
        if field not in query:
            raise ValueError(f"Missing required field: {field}")

    # Step 4: Validate filter fields
    required_filters = [
        "txn_id",
        "initiator",
        "beneficiary",
        "status",
        "date_from",
        "date_to",
        "amount_min",
        "amount_max"
    ]

    filters = query["filters"]

    for field in required_filters:
        if field not in filters:
            raise ValueError(f"Missing filter field: {field}")

    return query


def run_layer1(question):

    query = generate_query_json(question)

    return query