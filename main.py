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

            # ----------------------------
            # Layer 2
            # ----------------------------
            retrieved_data = retrieve(query)

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