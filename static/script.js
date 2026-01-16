// --- GLOBAL STATE ---
let attachedContext = ""; // Stores the clean PDF text
let attachedFilename = ""; // Stores the name for display

// Allow "Enter" to send
document.getElementById("user-input").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const secretField = document.getElementById("custom-secrets");
    const chatBox = document.getElementById("chat-box");
    const logBox = document.getElementById("log-box");
    const fileBadge = document.getElementById("file-badge"); // We will create this dynamically

    let userText = inputField.value.trim();
    if (!userText && !attachedContext) return; // Don't send empty

    // 1. Get Custom Secrets
    const secretList = secretField ? secretField.value.split(',').map(s => s.trim()).filter(s => s.length > 0) : [];

    // 2. SHOW USER MESSAGE
    // If we have a file attached, show a little icon in the user's bubble
    let displayHtml = userText;
    if (attachedFilename) {
        displayHtml = `<span style="font-size:0.8em; opacity:0.7">📎 Attached: ${attachedFilename}</span><br>${userText}`;
    }

    chatBox.innerHTML += `
        <div class="message user">
            <div class="msg-content">${displayHtml}</div>
        </div>`;
    
    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // 3. CONSTRUCT THE FULL PROMPT (The "Context Memory" Logic)
    let finalPrompt = userText;
    
    if (attachedContext) {
        // We inject the document context into the prompt
        finalPrompt = `I am sharing a document with you. Please use this content to answer my question.\n\nDOCUMENT CONTENT:\n${attachedContext}\n\nMY QUESTION:\n${userText}`;
    }

    // Loading Indicator
    const typingId = "typing-" + Date.now();
    chatBox.innerHTML += `
        <div class="message bot" id="${typingId}">
            <div class="msg-content"><span class="typing-dots">Encrypting & Thinking...</span></div>
        </div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // Send Prompt + Custom Secrets
        const response = await fetch("/secure_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                prompt: finalPrompt,
                custom_secrets: secretList 
            })
        });
        const data = await response.json();

        // Remove Loading
        document.getElementById(typingId).remove();

        // Show Response
        const formattedResponse = marked.parse(data.response);
        chatBox.innerHTML += `
            <div class="message bot">
                <div class="msg-content markdown-body">${formattedResponse}</div>
            </div>`;

        // Update Logs
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        let safePrompt = data.privacy_metadata.sanitized_prompt
            .replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const secretCount = data.privacy_metadata.secrets_hidden;

        logBox.innerHTML += `
            <div class="log-entry">
                <span class="timestamp">[${time}]</span> 🔒 <strong>OUTGOING:</strong> Sent ${finalPrompt.length} chars (Msg + Doc).
            </div>
            <div class="log-entry alert">
                <span class="timestamp">[${time}]</span> 🛡️ <strong>INTERCEPTED:</strong><br>
                <span class="indent">Removed <span class="highlight-red">${secretCount} secrets</span>.</span><br>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
        logBox.scrollTop = logBox.scrollHeight;

        // 4. CLEAR CONTEXT (So we don't send the CV again next time)
        attachedContext = "";
        attachedFilename = "";
        if (fileBadge) fileBadge.remove(); // Remove the visual badge

    } catch (error) {
        console.error(error);
        document.getElementById(typingId).innerHTML = `<div class="msg-content" style="color:red">Error. Check console.</div>`;
    }
}

// --- PDF UPLOAD LOGIC ---
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('pdf-upload');

// Handle Click
if (dropZone) dropZone.addEventListener('click', () => fileInput.click());

// Handle File Selection
if (fileInput) fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) await handleFileUpload(file);
});

async function handleFileUpload(file) {
    const chatBox = document.getElementById("chat-box");
    const logBox = document.getElementById("log-box");

    // Show "Processing" message
    chatBox.innerHTML += `
        <div class="message bot">
            <div class="msg-content">📄 Reading <strong>${file.name}</strong>...</div>
        </div>`;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload_pdf", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        // --- HERE IS THE MAGIC CHANGE ---
        // Instead of just printing it, we SAVE it to memory
        attachedContext = data.safe_content;
        attachedFilename = data.filename;

        // Show "Attached" Success Message in Chat
        chatBox.innerHTML += `
            <div class="message bot">
                <div class="msg-content">
                    ✅ <strong>File Attached!</strong><br>
                    I have redacted ${data.secrets_removed} secrets from this PDF.<br>
                    <em>You can now ask me questions about it.</em>
                </div>
            </div>`;
        
        // Add a Floating Badge above the text input so user knows it's there
        const inputArea = document.querySelector('.input-area');
        // Remove old badge if exists
        const oldBadge = document.getElementById("file-badge");
        if(oldBadge) oldBadge.remove();

        const badge = document.createElement("div");
        badge.id = "file-badge";
        badge.innerHTML = `📎 <strong>${data.filename}</strong> attached to next message`;
        badge.style.cssText = "background:#3b82f6; color:white; padding:5px 10px; border-radius:10px 10px 0 0; font-size:0.8rem; margin-left:10px; width:fit-content;";
        
        // Insert badge before the input area
        inputArea.parentNode.insertBefore(badge, inputArea);

        chatBox.scrollTop = chatBox.scrollHeight;

        // Log it
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        logBox.innerHTML += `
            <div class="log-entry alert">
                <span class="timestamp">[${time}]</span> 📄 <strong>FILE MEMORY:</strong><br>
                <span class="indent">Loaded ${data.filename} into context.</span>
            </div>
        `;
        
    } catch (error) {
        console.error(error);
        chatBox.innerHTML += `<div class="message bot" style="color:red">Error processing file.</div>`;
    }
}