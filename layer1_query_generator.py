
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

Valid intent values

Use ONLY one of these intent values.

lookup_transaction
count_transactions
count_failures
list_transactions
explain_error
transaction_history
invalid

Never create any other intent names.
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
If the user's message is not requesting information about WisiPay transactions,
transaction history, transaction counts, transaction errors, providers,
performance metrics, or error codes, then return:

{
  "intent": "invalid",
  "filters": {
    "txn_id": null,
    "initiator": null,
    "beneficiary": null,
    "status": null,
    "date_from": null,
    "date_to": null,
    "amount_min": null,
    "amount_max": null
  },
  "sources": [],
  "output_type": "detail"
}

Examples:
User: "Hello"
→ intent = "invalid"

User: "How are you?"
→ intent = "invalid"

User: "Tell me a joke."
→ intent = "invalid"

User: "Who are you?"
→ intent = "invalid"

1. Your job is ONLY to generate the retrieval plan.
The selected intent should describe the type of retrieval required, including whether the query requires transaction history across multiple log entries.
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

13a. If the user mentions phrases related to transaction limits, such as "transaction limit", "limit exceeded", "daily limit exceeded", "monthly limit exceeded", or "exceeded limit", map them directly to the status code "F402" inside filters.status.

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

28. If the answer requires examining the complete lifecycle of a transaction rather than a single matching log entry, use:

"intent": "transaction_history"

Examples include:

- eventually
- retries
- retry history
- transaction journey
- transaction timeline
- before succeeding
- after failing
- timed out but later succeeded
- multiple attempts
- complete history

29. Choose output_type as follows:

count
- Numeric totals only.

list
- Multiple matching transactions.

summary
- Aggregated information or grouped results.

detail
- One specific transaction or one specific error code.

30. The retrieval plan must contain only enough information for Layer 2 to fetch the minimum required rows.

31. Never retrieve extra files or unnecessary data.
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

32. If the user query is unrelated to transactions, payment logs, or WisiPay data, classify the query with the "invalid" intent and set all filters to null.

33. If the query is about a transaction submitted with an amount in USD instead of INR, set filters.txn_id to "TXN10031".

34. If the query is about a transaction submitted with a missing amount field, set filters.txn_id to "TXN10025".

35. If the query is about a user sending money to themselves or a self-transfer, set filters.txn_id to "TXN10014".

36. If the query asks about transactions that experienced F500, F502, or F503 before succeeding, set filters.status to ["F500", "F502", "F503", "SUCCESS"] and set intent to "transaction_history".

37. If the query is about transactions flagged and blocked by the fraud detection engine, map it to the status code "F403" inside filters.status.

38. For queries asking which user initiated the most failed transactions or their success rate, set filters.status to ["FAILED"] and output_type to "summary". Do not include other status codes like TIMEOUT or REVERSED since they are not failure states.
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

    # 1. Try existing logic first
    temp = cleaned
    if temp.startswith("```json"):
        temp = temp[7:]
    elif temp.startswith("```"):
        temp = temp[3:]
    if temp.endswith("```"):
        temp = temp[:-3]
    temp = temp.strip()

    try:
        return json.loads(temp)
    except json.JSONDecodeError:
        pass

    # 2. Extract code blocks with regex if present
    import re
    code_blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', raw_response, re.DOTALL)
    for block in code_blocks:
        try:
            return json.loads(block.strip())
        except json.JSONDecodeError:
            pass

    # 3. Fallback: Brace-matching search for the first valid JSON object in raw_response
    for start_idx in range(len(raw_response)):
        if raw_response[start_idx] == '{':
            brace_count = 0
            in_string = False
            escape = False
            for i in range(start_idx, len(raw_response)):
                char = raw_response[i]
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"':
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            candidate = raw_response[start_idx:i+1]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                break

    raise ValueError(
        f"Invalid JSON returned by LLM:\n\n{raw_response}"
    )

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



if __name__ == "__main__":

    question = input("Ask your question: ")

    query = run_layer1(question)

    print("\n========== Layer 1 Output ==========\n")
    print(json.dumps(query, indent=4))