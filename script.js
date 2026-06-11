const API_URL = "http://127.0.0.1:8000/chat";

/* =========================
   USER ID (STABLE MEMORY)
========================= */
let USER_ID = localStorage.getItem("user_id");

if (!USER_ID) {
    USER_ID = crypto.randomUUID();
    localStorage.setItem("user_id", USER_ID);
}

/* =========================
   ADD MESSAGE
========================= */
function addMessage(text, type) {
    const chat = document.getElementById("chatContainer");

    const msg = document.createElement("div");
    msg.className = `message ${type}`;
    msg.innerText = text;

    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;

    return msg;
}

/* =========================
   NEW CHAT
========================= */
function newChat() {
    USER_ID = crypto.randomUUID();
    localStorage.setItem("user_id", USER_ID);

    document.getElementById("chatContainer").innerHTML = `
        <div class="welcome">
            <h1>Welcome 👋</h1>
            <p>Ask anything...</p>
        </div>
    `;
}

/* =========================
   SEND MESSAGE
========================= */
async function sendMessage() {
    const input = document.getElementById("messageInput");
    const question = input.value.trim();

    if (!question) return;

    // remove welcome
    const welcome = document.querySelector(".welcome");
    if (welcome) welcome.remove();

    // show user message
    addMessage(question, "user");

    input.value = "";

    // loading message
    const loadingMsg = addMessage("Typing...", "bot");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: USER_ID,
                question: question
            })
        });

        const data = await response.json();

        loadingMsg.remove();
        addMessage(data.answer, "bot");

    } catch (error) {
        loadingMsg.remove();
        addMessage("Error: Backend not responding", "bot");
        console.error(error);
    }
}

/* =========================
   ENTER KEY SUPPORT
========================= */
document.getElementById("messageInput")
.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});