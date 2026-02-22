// const chatToggle = document.getElementById("chat-toggle");
// const chatContainer = document.getElementById("chat-container");
// const closeChat = document.getElementById("close-chat");
// const typing = document.getElementById("typing");

// chatToggle.onclick = () => chatContainer.style.display = "flex";
// closeChat.onclick = () => chatContainer.style.display = "none";

// function sendMessage() {
//     let input = document.getElementById("user-input");
//     let message = input.value.trim();
//     if (message === "") return;

//     let chatBox = document.getElementById("chat-box");

//     let userDiv = document.createElement("div");
//     userDiv.className = "user-message";
//     userDiv.innerText = message;
//     chatBox.appendChild(userDiv);

//     input.value = "";
//     chatBox.scrollTop = chatBox.scrollHeight;

//     typing.style.display = "block";

//     fetch("/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: message })
//     })
//     .then(res => res.json())
//     .then(data => {
//         typing.style.display = "none";
//         let botDiv = document.createElement("div");
//         botDiv.className = "bot-message";
//         botDiv.innerText = data.reply;
//         chatBox.appendChild(botDiv);
//         chatBox.scrollTop = chatBox.scrollHeight;
//     });
// }

// // Enter key support
// document.getElementById("user-input")
// .addEventListener("keypress", function(e) {
//     if (e.key === "Enter") sendMessage();
// });


// Get DOM elements
const chatToggle = document.getElementById("chat-toggle");
const chatContainer = document.getElementById("chat-container");
const closeChat = document.getElementById("close-chat");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const chatBox = document.getElementById("chat-box");
const typing = document.getElementById("typing");

// Resize functionality
let isResizing = false;
let resizeDirection = null;
let currentWidth = 420;
let currentHeight = 600;
let startX = 0;
let startY = 0;
let startLeft = 0;
let startTop = 0;

const resizeHandles = {
    'bottom-right': document.getElementById("resize-bottom-right"),
    'right': document.getElementById("resize-right"),
    'bottom': document.getElementById("resize-bottom"),
    'left': document.getElementById("resize-left"),
    'top': document.getElementById("resize-top")
};

// Add event listeners to all resize handles
Object.entries(resizeHandles).forEach(([direction, handle]) => {
    handle.addEventListener("mousedown", (e) => startResize(e, direction));
});

function startResize(e, direction) {
    isResizing = true;
    resizeDirection = direction;
    startX = e.clientX;
    startY = e.clientY;
    currentWidth = chatContainer.offsetWidth;
    currentHeight = chatContainer.offsetHeight;
    startLeft = chatContainer.offsetLeft;
    startTop = chatContainer.offsetTop;
    
    document.addEventListener("mousemove", resize);
    document.addEventListener("mouseup", stopResize);
    e.preventDefault();
}

function resize(e) {
    if (!isResizing) return;
    
    const diffX = e.clientX - startX;
    const diffY = e.clientY - startY;
    
    let newWidth = currentWidth;
    let newHeight = currentHeight;
    let newLeft = startLeft;
    let newTop = startTop;
    
    switch(resizeDirection) {
        case 'bottom-right':
            newWidth = currentWidth + diffX;
            newHeight = currentHeight + diffY;
            break;
        case 'right':
            newWidth = currentWidth + diffX;
            break;
        case 'bottom':
            newHeight = currentHeight + diffY;
            break;
        case 'left':
            newWidth = currentWidth - diffX;
            newLeft = startLeft + diffX;
            break;
        case 'top':
            newHeight = currentHeight - diffY;
            newTop = startTop + diffY;
            break;
    }
    
    // Apply min and max constraints
    newWidth = Math.max(300, Math.min(newWidth, window.innerWidth - 40));
    newHeight = Math.max(400, Math.min(newHeight, window.innerHeight - 140));
    
    // Prevent going off-screen
    newLeft = Math.max(0, newLeft);
    newTop = Math.max(0, newTop);
    
    chatContainer.style.width = newWidth + "px";
    chatContainer.style.height = newHeight + "px";
    
    if (resizeDirection === 'left' || resizeDirection === 'bottom-right') {
        chatContainer.style.left = newLeft + "px";
    }
    if (resizeDirection === 'top' || resizeDirection === 'bottom-right') {
        chatContainer.style.top = newTop + "px";
    }
}

function stopResize() {
    isResizing = false;
    resizeDirection = null;
    document.removeEventListener("mousemove", resize);
    document.removeEventListener("mouseup", stopResize);
}

// Chat toggle functionality
chatToggle.addEventListener("click", () => {
    chatContainer.classList.toggle("active");
    if (chatContainer.classList.contains("active")) {
        userInput.focus();
    }
});

// Close chat functionality
closeChat.addEventListener("click", () => {
    chatContainer.classList.remove("active");
});

// Close chat when clicking outside (optional enhancement)
document.addEventListener("click", (e) => {
    if (!chatContainer.contains(e.target) && !chatToggle.contains(e.target)) {
        // Keep it open for better UX - remove this if you want auto-close
        // chatContainer.classList.remove("active");
    }
});

// Send message function
function sendMessage() {
    const message = userInput.value.trim();
    
    if (message === "") return;

    // Clear input
    userInput.value = "";

    // Add user message to chat
    addMessageToChat(message, "user");

    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show typing indicator
    typing.classList.add("active");

    // Send to backend
    fetch("/chat", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        typing.classList.remove("active");
        
        if (data.reply) {
            addMessageToChat(data.reply, "bot");
        } else {
            addMessageToChat("Sorry, I couldn't process your request. Please try again.", "bot");
        }
        
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
        typing.classList.remove("active");
        addMessageToChat("Sorry, there was an error connecting to the server. Please try again.", "bot");
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Re-focus input
    userInput.focus();
}

// Add message to chat display
function addMessageToChat(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = sender === "user" ? "user-message" : "bot-message";

    if (sender === "user") {
        messageDiv.innerHTML = `
            <div class="message-content">${escapeHtml(message)}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <span class="message-avatar">🤖</span>
            <div class="message-content">${escapeHtml(message)}</div>
        `;
    }

    chatBox.appendChild(messageDiv);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Send message on Enter key
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message on button click
sendBtn.addEventListener("click", sendMessage);

// Auto-focus input when chat opens
chatToggle.addEventListener("click", () => {
    setTimeout(() => {
        if (chatContainer.classList.contains("active")) {
            userInput.focus();
        }
    }, 100);
});

// Optional: Prevent form submission if embedded in a form
document.addEventListener("submit", (e) => {
    if (e.target.contains(userInput)) {
        e.preventDefault();
    }
});