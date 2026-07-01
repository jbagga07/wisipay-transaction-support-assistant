'''. retrieve(query_json)	Master function	All

'''
from datetime import datetime
import json
import os
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.log")

PROVIDER_RESPONSE_FILE = os.path.join(
    DATA_DIR,
    "provider_responses.log"
)

PERF_METRICS_FILE = os.path.join(
    DATA_DIR,
    "perf_metrics.log"
)

ERROR_CODES_FILE = os.path.join(
    DATA_DIR,
    "error_codes.json"
)



'''
parse_log_line(line)
Job

Reads one line from a log file and converts it into a Python dictionary.

Example input:

2026-05-01T09:12:03Z | TXN_ID=TXN10001 | STATUS=SUCCESS

Output:

{
    "timestamp": "2026-05-01 09:12:03",
    "txn_id": "TXN10001",
    "status": "SUCCESS"
}
'''

def parse_log_line(line):

    # Remove spaces and newline
    line = line.strip()

    # Ignore blank lines
    if line == "":
        return None

    # Ignore comments
    if line.startswith("#"):
        return None

    # Split the line into parts
    # Split the line into parts
    parts = line.split(" | ")

    # Ignore malformed lines
    if len(parts) == 0:
        return None

    # First value is always the timestamp
    timestamp = parts[0].strip()

# Normalize timestamp format
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")

    data = {
        "timestamp": timestamp
    }
    # Remaining values are KEY=VALUE
    for part in parts[1:]:

        if "=" not in part:
            continue

        key, value = part.split("=", 1)

        key = key.strip().lower()
        value = value.strip()

        # Normalize transaction IDs
        if key == "txn_id":
            value = value.upper()

        # Empty values become empty strings
        if value == "":
            value = ""

        data[key] = value

    return data



#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

#===================================================================================

'''
apply_filters(transaction, filters)
Job
Checks if a transaction satisfies all the filters.
Example:
Transaction:
{
    "txn_id":"TXN10001",
    "status":"SUCCESS",
    "amount":"2500 INR"
}
Filters:
{
    "status":["SUCCESS"],
    "amount_min":2000
}
Returns:
True
or
False
'''
def apply_filters(transaction, filters):

    # Transaction ID
    if filters["txn_id"] is not None:
        if transaction.get("txn_id", "").upper() != filters["txn_id"].upper():
            return False

    # Initiator
    if filters["initiator"] is not None:
        if transaction.get("initiator", "").lower() != filters["initiator"].lower():
            return False

    # Beneficiary
    if filters["beneficiary"] is not None:
        if transaction.get("beneficiary", "").lower() != filters["beneficiary"].lower():
            return False

    # Status / Error Code
    if filters["status"] is not None:
        if transaction.get("status") not in filters["status"]:
            return False
        # Date From
    if filters["date_from"] is not None:

        transaction_date = datetime.strptime(
            transaction["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        ).date()

        filter_date = datetime.strptime(
            filters["date_from"],
            "%Y-%m-%d"
        ).date()

        if transaction_date < filter_date:
            return False


    # Date To
    if filters["date_to"] is not None:

        transaction_date = datetime.strptime(
            transaction["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        ).date()

        filter_date = datetime.strptime(
            filters["date_to"],
            "%Y-%m-%d"
        ).date()

        if transaction_date > filter_date:
            return False
        
        
            # Convert amount into a number
    amount = parse_amount(transaction.get("amount", ""))


    # Minimum Amount
    if filters["amount_min"] is not None:

        if amount is None:
            return False

        if amount < filters["amount_min"]:
            return False


    # Maximum Amount
    if filters["amount_max"] is not None:

        if amount is None:
            return False

        if amount > filters["amount_max"]:
            return False
    return True

'''
parse_amount(amount_text)
Job

Converts

"2,500.00 INR"

into

2500.0

so numerical comparisons become possible.
'''
def parse_amount(amount_text):

    try:
        return float(
            amount_text.split()[0].replace(",", "")
        )
    except:
        return None

#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

'''
This is the main search function.

It

opens transactions.log
reads every line
parses it
applies filters
stores matching transactions

Returns:

[
    {...},
    {...},
    {...}
]
'''

def query_transactions(filters):

    results = []

    with open(TRANSACTION_FILE, "r", encoding="utf-8") as file:

        for line in file:

            transaction = parse_log_line(line)

            if transaction is None:
                continue

            if apply_filters(transaction, filters):
                results.append(transaction)

    return results


'''
deduplicate_transactions(rows)
Job

Suppose the log contains

TXN10001 SUCCESS
TXN10001 FAILED
TXN10001 REVERSED

It keeps only one record (the last one encountered in the current implementation).

Useful for questions like:

"How many unique transactions?"
'''
def deduplicate_transactions(rows):

    latest_transactions = {}

    for row in rows:

        txn_id = row["txn_id"]

        latest_transactions[txn_id] = row

    return list(latest_transactions.values())

'''
group_by_txn_id(rows)
Job
Groups all entries belonging to the same transaction.

Example:

Input

[
 TXN10001,
 TXN10001,
 TXN10002
]

Output

{
   "TXN10001":[...,...],
   "TXN10002":[...]
}

Useful when you want the entire history of each transaction.
'''
def group_by_txn_id(rows):

    grouped_transactions = {}

    for row in rows:

        txn_id = row["txn_id"]

        if txn_id not in grouped_transactions:
            grouped_transactions[txn_id] = []

        grouped_transactions[txn_id].append(row)

    return grouped_transactions
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

'''
get_txn_ids(rows)
Job
Extracts unique transaction IDs from a list of transactions.

Example:

Input:

[
 {"txn_id":"TXN101"},
 {"txn_id":"TXN102"},
 {"txn_id":"TXN101"}
]

Output:

{
   "TXN101",
   "TXN102"
}

Used to fetch provider responses or performance metrics for the same transactions.
'''
def get_txn_ids(results):

    transactions = results.get("transactions", [])

    txn_ids = set()

    for transaction in transactions:
        txn_ids.add(transaction["txn_id"].upper())

    return txn_ids


#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

'''
query_provider_responses(filters, txn_ids)
Job
Searches provider_response.log for transactions matching the given IDs.

It:

Opens provider_response.log
Parses each line
Keeps only transactions whose txn_id is present in txn_ids
Returns:

[
    {...},
    {...},
    {...}
]
This is used to fetch response details for specific transactions.
'''
def query_provider_responses(filters, txn_ids):

    results = []

    with open(PROVIDER_RESPONSE_FILE, "r", encoding="utf-8") as file:

        for line in file:

            provider_response = parse_log_line(line)

            if provider_response is None:
                continue

            if provider_response.get("txn_id", "").upper() in txn_ids:
                results.append(provider_response)

    return results
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

'''
query_perf_metrics(filters, txn_ids)
Job
Searches perf_metrics.log for transactions matching the given IDs.

It:

Opens perf_metrics.log
Parses each line
Keeps only transactions whose txn_id is present in txn_ids
Returns:

[
    {...},
    {...},
    {...}
]
Used to fetch performance data for transactions.
'''
def query_perf_metrics(filters, txn_ids):

    results = []

    with open(PERF_METRICS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            metric = parse_log_line(line)

            if metric is None:
                continue

            if metric.get("txn_id", "").upper() in txn_ids:
                results.append(metric)

    return results
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
'''
lookup_error_codes(codes)
Job

Looks up error codes in error_codes.json.

Input:

["E1001", "E1004"]

Output:

{
  "E1001": { ... },
  "E1004": { ... }
}

Used to provide detailed error explanations to the user.
'''
def lookup_error_codes(codes):

    with open(ERROR_CODES_FILE, "r", encoding="utf-8") as file:

        data = json.load(file)

    results = {}

    for error in data["error_codes"]:

        if error["code"] in codes:
            results[error["code"]] = error

    return results

#===================================================================================
#===================================================================================
#===================================================================================
'''
get_status_codes(results)
Job
Extracts unique status codes from transactions.

Used when you need to show all possible statuses present in the current results.

Example:

If transactions have statuses:
"SUCCESS", "FAILED", "PENDING"

Output:

{
    "SUCCESS",
    "FAILED",
    "PENDING"
}
'''
def get_status_codes(results):

    transactions = results.get("transactions", [])

    status_codes = set()

    for transaction in transactions:

        if "status" in transaction:
            status_codes.add(transaction["status"])

    return status_codes
# ==========================================================
# ==========================================================
# ==========================================================
# ==========================================================
# ==========================================================
# ==========================================================
'''
retrieve(query)
Job

This is the main retrieval orchestrator.

It receives a query_json dictionary and returns retrieved data.

How it works:

Extracts filters.

If all filters are empty, returns {}.

Calls appropriate functions based on query.sources:

Transactions
Provider responses
Performance metrics
Error codes
Then returns a dictionary like:

{
  "transactions": [...],
  "provider_responses": [...],
  "perf_metrics": [...]
}
'''
def retrieve(query):
    filters = query.get("filters", {})

    if all(value is None for value in filters.values()):
        return {}
    results = {}

    sources = query.get("sources", [])

    filters = query.get("filters", {})

    if "transactions" in sources:

        transactions = query_transactions(filters)

        if (
            query.get("intent") == "count_transactions"
            or query.get("output_type") == "count"
        ):
            transactions = deduplicate_transactions(transactions)

        results["transactions"] = transactions

    if "provider_responses" in sources:

        txn_ids = get_txn_ids(results)

        results["provider_responses"] = query_provider_responses(
            filters,
            txn_ids
        )

    if "perf_metrics" in sources:

        txn_ids = get_txn_ids(results)

        results["perf_metrics"] = query_perf_metrics(
            filters,
            txn_ids
        )

    if "error_codes" in sources:

        status_codes = get_status_codes(results)

        results["error_codes"] = lookup_error_codes(
            status_codes
        )

    return results


# ==========================================================
# TESTING LAYER 2
# ==========================================================
# ==========================================================
# ==========================================================
# ==========================================================

# ==========================================================
# TESTING LAYER 2
# ==========================================================
