from layer1_query_generator import run_layer1
from layer2_retriever import retrieve
from layer3_responder import generate_response


def main():

    print("==========================================")
    print("      WisiPay Transaction Assistant")
    print("Type 'exit', 'quit' or 'stop' to end.")
    print("==========================================")

    while True:

        question = input("\nAsk your question: ").strip()

        if question.lower() in ["exit", "quit", "stop"]:
            print("\nThank you for using WisiPay Assistant.")
            break

        try:

            # ----------------------------
            # Layer 1
            # ----------------------------
            query = run_layer1(question)
            print("----------------------------------------")
            print("----------------------------------------")
            print("----------------------------------------")
            print(query)
            print("----------------------------------------")
            print("----------------------------------------")
            print("----------------------------------------")
            # ----------------------------
            # Layer 2
            # ----------------------------
            retrieved_data = retrieve(query)
            print(retrieved_data)
            
            # Display retrieval statistics if present
            stats = retrieved_data.get("retrieval_statistics")
            if stats:
                print("\n--- Retrieval Statistics ---")
                print(f"Rows Scanned: {stats.get('rows_scanned')}")
                print(f"Rows Matched: {stats.get('rows_matched')}")
                print(f"Rows Returned: {stats.get('rows_returned')}")
                print("----------------------------\n")
                
            print("----------------------------------------")
            print("----------------------------------------")
            print("----------------------------------------")
            # ----------------------------
            # Layer 3
            # ----------------------------
            response = generate_response(
                question,
                retrieved_data,
                query
            )

            print("\n----------------------------------------")
            print("Answer:")
            print("----------------------------------------")
            print(response)

        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
    


