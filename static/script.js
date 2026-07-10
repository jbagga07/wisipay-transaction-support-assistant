const chatContainer = document.getElementById("chatContainer");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");

// ----------------------------
// Add Message
// ----------------------------
function addMessage(message, sender) {

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message;

    messageDiv.appendChild(content);

    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ----------------------------
// Send Question
// ----------------------------
async function sendQuestion() {

    const question = questionInput.value.trim();

    if (question === "") {
        return;
    }

    // Show user's message
    addMessage(question, "user");

    // Clear textbox
    questionInput.value = "";

    // Disable button while processing
    sendButton.disabled = true;
    sendButton.innerText = "Thinking...";

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const data = await response.json();

        if (data.success) {

            addMessage(data.response, "bot");

        } else {

            addMessage("Error:\n" + data.response, "bot");

        }

    } catch (error) {

        addMessage("Server Error:\n" + error.message, "bot");

    }

    sendButton.disabled = false;
    sendButton.innerText = "Send";
}

// ----------------------------
// Button Click
// ----------------------------
sendButton.addEventListener("click", sendQuestion);

// ----------------------------
// Press Enter
// ----------------------------
questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendQuestion();

    }

});