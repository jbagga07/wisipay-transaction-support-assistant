import os
import sys
import json
import traceback

# Import WisiPay pipeline
from layer1_query_generator import run_layer1
from layer2_retriever import retrieve
from layer3_responder import generate_response

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_QUERIES_FILE = os.path.join(DATA_DIR, "test_queries.txt")
TEST_RESULTS_FILE = os.path.join(DATA_DIR, "test_results.txt")

def parse_queries(file_path):
    queries = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith("Q") and line_stripped.endswith(".") and line_stripped[1:-1].isdigit():
            q_num = int(line_stripped[1:-1])
            query_text = ""
            for next_line in lines[i+1:]:
                next_stripped = next_line.strip()
                if next_stripped:
                    query_text = next_stripped
                    break
            queries.append((q_num, query_text))
    return queries

def main():
    if not os.path.exists(TEST_QUERIES_FILE):
        print(f"Error: {TEST_QUERIES_FILE} not found.")
        sys.exit(1)
        
    print("Parsing queries from test_queries.txt...")
    queries = parse_queries(TEST_QUERIES_FILE)
    print(f"Found {len(queries)} queries.\n")
    
    with open(TEST_RESULTS_FILE, "w", encoding="utf-8") as out:
        out.write("================================================================================\n")
        out.write("  WISIPAY ASSESSMENT 1 — TEST RESULTS\n")
        out.write("================================================================================\n\n")
        
        for q_num, question in queries:
            print(f"Running Query {q_num}...")
            out.write(f"Q{q_num}.\n")
            out.write(f"User Query: {question}\n\n")
            
            try:
                # Run Layer 1
                query_json = run_layer1(question)
                out.write("Layer 1 generated JSON:\n")
                out.write(json.dumps(query_json, indent=2))
                out.write("\n\n")
                
                # Run Layer 2
                retrieved_data = retrieve(query_json)
                
                # Extract and write Layer 2 stats
                stats = retrieved_data.get("retrieval_statistics", {})
                out.write("Layer 2 retrieval statistics:\n")
                out.write(f"Rows Scanned: {stats.get('rows_scanned', 0)}\n")
                out.write(f"Rows Matched: {stats.get('rows_matched', 0)}\n")
                out.write(f"Rows Returned: {stats.get('rows_returned', 0)}\n\n")
                
                # Write Layer 2 retrieved data (excluding retrieval_statistics to keep it clean)
                retrieved_clean = {k: v for k, v in retrieved_data.items() if k != "retrieval_statistics"}
                out.write("Layer 2 retrieved data:\n")
                out.write(json.dumps(retrieved_clean, separators=(",", ":")))
                out.write("\n\n")
                
                # Run Layer 3
                response = generate_response(question, retrieved_data, query_json)
                out.write("Final Layer 3 response:\n")
                out.write(response)
                out.write("\n")
                
            except Exception as e:
                print(f"Error running Query {q_num}: {e}")
                out.write(f"Execution Error: {e}\n")
                traceback.print_exc()
                
            out.write("--------------------------------------------------------------------------------\n\n")
            
    print(f"\nAll queries processed. Results written to {TEST_RESULTS_FILE}")

if __name__ == "__main__":
    main()
