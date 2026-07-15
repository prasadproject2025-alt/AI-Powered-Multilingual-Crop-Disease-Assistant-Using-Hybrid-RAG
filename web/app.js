const sendBtn = document.getElementById("send-btn");
const voiceBtn = document.getElementById("voice-btn");
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const languageSelect = document.getElementById("language-select");

// --- Send message ---
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

async function sendMessage() {
  const query = userInput.value.trim();
  if (!query) return;

  const lang = languageSelect.value;
  appendMessage("user", query);
  userInput.value = "";

  const responseBox = appendMessage("bot", "⏳ Thinking...");

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, language: lang })
    });

    const data = await res.json();
    responseBox.textContent = data.response || "No response received.";
    updateKnowledgePanel(data.kb_match);
  } catch (err) {
    responseBox.textContent = "⚠️ Server error: " + err.message;
  }
}

// --- Append message to chat ---
function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add(sender === "user" ? "user-msg" : "bot-msg");
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
  return msg;
}

// --- Update Knowledge Panel ---
function updateKnowledgePanel(kb) {
  if (!kb || kb === "No match") {
    document.getElementById("crop-name").textContent = "–";
    document.getElementById("disease-name").textContent = "–";
    document.getElementById("symptom-list").innerHTML = "<li>–</li>";
    document.getElementById("solution-text").textContent = "–";
    return;
  }

  document.getElementById("crop-name").textContent = kb.crop || "–";
  document.getElementById("disease-name").textContent = kb.disease || "–";

  const symptoms = kb.symptoms ? kb.symptoms.split(",") : [];
  document.getElementById("symptom-list").innerHTML =
    symptoms.map(s => `<li>${s}</li>`).join("");

  document.getElementById("solution-text").textContent =
    kb.solution || "–";
}

// --- Voice input (SpeechRecognition API) ---
voiceBtn.addEventListener("click", () => {
  if (!("webkitSpeechRecognition" in window)) {
    alert("Speech recognition not supported in this browser.");
    return;
  }
  const recognition = new webkitSpeechRecognition();
  recognition.lang = languageSelect.value === "en" ? "en-US" : "hi-IN";
  recognition.start();
  voiceBtn.textContent = "🎙️ Listening…";

  recognition.onresult = event => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    voiceBtn.textContent = "🎙️ Speak";
  };

  recognition.onerror = () => {
    voiceBtn.textContent = "🎙️ Speak";
  };
});
