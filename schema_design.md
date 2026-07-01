# WisiPay Assessment 1

# schema_design.md

## JSON Schema Design

## Overview

The purpose of this schema is to define a fixed JSON contract between the LLM (Layer 1) and the Python Retrieval Engine (Layer 2).

The LLM is responsible only for understanding the user's natural language question and converting it into a structured JSON object.

The Python Retriever is responsible only for reading this JSON object, retrieving the required information from the data files, and returning the matching records.

Keeping this contract fixed ensures that both layers remain independent. The LLM never performs data retrieval, and the retriever never performs natural language understanding.

---

# Overall JSON Structure

```json
{
    "intent": "string",

    "filters": {
        "txn_id": "string | null",
        "initiator": "string | null",
        "beneficiary": "string | null",
        "status": ["string"] | null,
        "date_from": "YYYY-MM-DD | null",
        "date_to": "YYYY-MM-DD | null",
        "amount_min": "number | null",
        "amount_max": "number | null"
    },

    "sources": [
        "transactions",
        "provider_responses",
        "perf_metrics",
        "error_codes"
    ],

    "output_type": "count | list | summary | detail"
}
```

---

# Field Design and Rationale

## 1. intent

Type

```
string
```

Required

```
Yes
```

Purpose

Represents the user's primary objective.

Examples

```
lookup_transaction
count_transactions
count_failures
explain_error
list_transactions
```

Reason for inclusion

The retriever needs to understand what type of operation should be performed. Different intents require different retrieval strategies.

For example,

* count_transactions returns only a count.
* explain_error requires joining multiple files.
* lookup_transaction retrieves one transaction.

Keeping the intent separate from filters makes the retrieval logic much cleaner.

---

## 2. filters.txn_id

Type

```
string | null
```

Required

```
Optional
```

Purpose

Stores the transaction ID if the user mentions one.

Example

```
TXN10039
```

Reason

Transaction ID uniquely identifies a transaction and allows direct lookup without scanning unrelated records.

---

## 3. filters.initiator

Type

```
string | null
```

Required

```
Optional
```

Purpose

Stores the name of the transaction initiator.

Example

```
Rohan Mehta
```

Reason

Allows the retriever to filter all transactions initiated by a particular user.

---

## 4. filters.beneficiary

Type

```
string | null
```

Required

```
Optional
```

Purpose

Stores the beneficiary name.

Reason

Allows searching transactions received by a particular beneficiary.

---

## 5. filters.status

Type

```
List[String] | null
```

Required

```
Optional
```

Purpose

Stores one or more transaction status values.

Examples

```
SUCCESS

FAILED

PENDING

TIMEOUT

F207

F311
```

Reason

Some user questions involve multiple status values.

For example,

"Show SUCCESS and FAILED transactions."

Using a list allows multiple values without changing the schema.

---

## 6. filters.date_from

Type

```
String | null
```

Format

```
YYYY-MM-DD
```

Purpose

Represents the beginning of a date range.

Reason

Allows date-based filtering while keeping the schema flexible.

---

## 7. filters.date_to

Type

```
String | null
```

Format

```
YYYY-MM-DD
```

Purpose

Represents the end of a date range.

Reason

Works together with date_from to support date interval queries.

---

## 8. filters.amount_min

Type

```
Number | null
```

Purpose

Represents the minimum transaction amount.

Reason

Allows queries such as

"Show transactions greater than ₹5000."

---

## 9. filters.amount_max

Type

```
Number | null
```

Purpose

Represents the maximum transaction amount.

Reason

Allows queries such as

"Show transactions below ₹1000."

---

## 10. sources

Type

```
List[String]
```

Required

```
Yes
```

Allowed Values

```
transactions

provider_responses

perf_metrics

error_codes
```

Purpose

Specifies exactly which data files the retriever should access.

Reason

This field is the most important part of the schema.

Instead of loading every available file, the retriever opens only the files listed in this field.

Examples

Simple transaction count

```
[
    "transactions"
]
```

Failure explanation

```
[
    "transactions",
    "provider_responses",
    "error_codes"
]
```

Performance investigation

```
[
    "transactions",
    "perf_metrics"
]
```

This minimizes unnecessary file access and ensures that only relevant information is sent to Layer 3.

---

## 11. output_type

Type

```
String
```

Required

```
Yes
```

Allowed Values

```
count

list

summary

detail
```

Purpose

Specifies the expected format of the final response.

Reason

Different user questions require different response styles.

Examples

count

```
How many failed transactions occurred today?
```

list

```
List all pending transactions.
```

summary

```
Summarize today's failures.
```

detail

```
Why did TXN10039 fail?
```

This allows Layer 3 to generate responses in the correct format.

---

# Design Principles

The schema was designed using the following principles:

* Fixed JSON structure for every query.
* Separation of responsibilities between the LLM and Python.
* Only relevant files are accessed.
* Unused fields are set to null rather than removed.
* Easy to extend by adding new filters without changing the overall structure.
* Supports all assessment test cases without requiring modifications to the schema.

---

# Example Output

User Question

```
Why did TXN10039 fail?
```

Expected Layer 1 Output

```json
{
    "intent": "explain_error",

    "filters": {
        "txn_id": "TXN10039",
        "initiator": null,
        "beneficiary": null,
        "status": null,
        "date_from": null,
        "date_to": null,
        "amount_min": null,
        "amount_max": null
    },

    "sources": [
        "transactions",
        "provider_responses",
        "error_codes"
    ],

    "output_type": "detail"
}
```

---

# Conclusion

This schema provides a consistent communication contract between the LLM and the Python retriever. It supports all required assessment scenarios while ensuring that only the necessary data sources are accessed. The design keeps each layer independent, reduces unnecessary data retrieval, and makes the system easy to maintain and extend.
