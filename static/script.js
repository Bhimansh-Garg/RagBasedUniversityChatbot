const chatToggle = document.getElementById("chat-toggle");
const chatContainer = document.getElementById("chat-container");
const closeChat = document.getElementById("close-chat");
const typing = document.getElementById("typing");

chatToggle.onclick = () => chatContainer.style.display = "flex";
closeChat.onclick = () => chatContainer.style.display = "none";

function sendMessage() {
    let input = document.getElementById("user-input");
    let message = input.value.trim();
    if (message === "") return;

    let chatBox = document.getElementById("chat-box");

    let userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.innerText = message;
    chatBox.appendChild(userDiv);

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    typing.style.display = "block";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        typing.style.display = "none";
        let botDiv = document.createElement("div");
        botDiv.className = "bot-message";
        botDiv.innerText = data.reply;
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

// Enter key support
document.getElementById("user-input")
.addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});
