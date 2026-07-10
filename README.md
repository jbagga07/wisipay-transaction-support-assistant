WisiPay Transaction Support Assistant

An AI-powered transaction support assistant built in Python to automate merchant support queries using a layered architecture.

This project was developed under the supervision of Manthan Paliwal for WisiPay to reduce the manual workload of support teams by intelligently retrieving and explaining transaction-related information.

Overview

Support teams frequently receive questions such as:

Why did my transaction fail?
What does this error code mean?
Show the complete transaction history.
What was the provider response?
What are the transaction performance metrics?
Count or list transactions based on different filters.

Instead of manually searching through multiple log files, the assistant understands the user's natural language query, retrieves only the required data, and generates a clear human-readable response.

Architecture

The project follows a 3-Layer AI Architecture.

Layer 1 – Query Understanding
Accepts the user's natural language question.
Uses an LLM to convert the question into a structured retrieval plan.
Identifies filters, intent, required data sources, and output type.
Layer 2 – Retrieval Engine

Performs all business logic without using AI.

Reads transaction logs
Searches provider responses
Retrieves performance metrics
Looks up error codes
Performs filtering
Executes calculations
Returns only the minimum required data

No complete log files are ever sent to the AI.

Layer 3 – Response Generation

Uses AI to convert the retrieved data into a concise, human-readable response.

Since Layer 2 has already completed all retrieval and computation, the AI only focuses on explaining the results.

Data Sources
transactions.log
provider_responses.log
perf_metrics.log
error_codes.json
Key Features
Natural language transaction search
Transaction history retrieval
Error code explanations
Provider response lookup
Performance metric analysis
Merchant support automation
Retrieval-augmented architecture
Minimal context passed to the LLM
Human-readable AI responses
Tech Stack
Python
Flask
Ollama
Gemma 4
HTML
CSS
JavaScript
Project Goal

The objective of this project is to automate merchant support by reducing manual log analysis. Instead of reading multiple files for every support ticket, the assistant retrieves only the relevant information and generates accurate, easy-to-understand responses.
