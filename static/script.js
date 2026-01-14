async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const logBox = document.getElementById("log-box");

    const userText = inputField.value;
    if (!userText) return;

    // Show User Message
    chatBox.innerHTML += `<div class="message user">${userText}</div>`;
    inputField.value = "";

    try {
        const response = await fetch("/secure_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: userText })
        });
        const data = await response.json();

        // FIX: Replaces < and > so browser treats them as text, not code
        let safePrompt = data.privacy_metadata.sanitized_prompt
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        const secretCount = data.privacy_metadata.secrets_hidden;

        // Update Logs
        logBox.innerHTML += `
            <div class="log-entry">
                <strong>🔒 OUTGOING:</strong><br>
                User sent ${userText.length} chars.
            </div>
            <div class="log-entry alert">
                <strong>🛡️ INTERCEPTED:</strong><br>
                Sensitive data detected! Removed ${secretCount} secrets.<br>
                <span style="color: #facc15">Sending to Cloud: "${safePrompt}"</span>
            </div>
        `;

        chatBox.innerHTML += `<div class="message bot">${data.response}</div>`;

        chatBox.scrollTop = chatBox.scrollHeight;
        logBox.scrollTop = logBox.scrollHeight;

    } catch (error) {
        console.error("Error:", error);
        chatBox.innerHTML += `<div class="message bot" style="color:red">Error connecting to server.</div>`;
    }
}