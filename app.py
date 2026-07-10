from flask import Flask, render_template, request, jsonify

from layer1_query_generator import run_layer1
from layer2_retriever import retrieve
from layer3_responder import generate_response

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()

        question = data.get("question", "").strip()

        if question == "":
            return jsonify({
                "success": False,
                "response": "Please enter a question."
            })

        # -----------------------------
        # Layer 1
        # -----------------------------
        query = run_layer1(question)

        # -----------------------------
        # Layer 2
        # -----------------------------
        retrieved_data = retrieve(query)

        # -----------------------------
        # Layer 3
        # -----------------------------
        response = generate_response(
            question,
            retrieved_data,
            query
        )

        return jsonify({

            "success": True,

            "question": question,

            "response": response,

            "query": query,

            "retrieval_statistics":
                retrieved_data.get(
                    "retrieval_statistics",
                    {}
                )

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "response": str(e)

        })


if __name__ == "__main__":
    app.run(debug=True)