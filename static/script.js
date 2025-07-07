const chatbox = document.getElementById("chatbox");

// ✅ Thêm tin nhắn vào khung chat
function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "message " + sender;
  const label = sender === "user" ? "Bạn" : "🤖 AI";
  div.textContent = `${label}: ${text}`;
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}

// ✅ Đọc văn bản bằng giọng nói
function speak(text) {
  const synth = window.speechSynthesis;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "vi-VN";
  synth.speak(utter);
}

// ✅ Gửi tin nhắn khi nhấn nút hoặc Enter
async function sendMessage() {
  const input = document.getElementById("message-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  try {
    const res = await fetch("/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    });

    const data = await res.json();
    addMessage(data.reply, "bot");
    speak(data.reply);
  } catch (err) {
    addMessage("❌ Không kết nối được với server!", "bot");
  }
}

// ✅ Ghi âm giọng nói bằng Web Speech API
function startListening() {
  const synth = window.speechSynthesis;

  // ✅ Ngắt nói nếu đang nói
  if (synth.speaking) {
    synth.cancel();  // Dừng nói ngay
  }

  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "vi-VN";
  recognition.start();

  // ➕ Bật hiệu ứng glowing cho nút micro
  document.querySelector(".mic-button").classList.add("listening");

  recognition.onresult = async function(event) {
    const message = event.results[0][0].transcript;
    addMessage(message, "user");

    // 🔴 Tắt hiệu ứng glowing
    document.querySelector(".mic-button").classList.remove("listening");

    try {
      const response = await fetch("/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      const data = await response.json();
      addMessage(data.reply, "bot");
      speak(data.reply);  // Nói lại phản hồi mới
    } catch (error) {
      addMessage("❌ Lỗi phản hồi từ server!", "bot");
    }
  };

  recognition.onerror = function() {
    alert("Không nghe thấy gì hoặc microphone bị lỗi. Vui lòng thử lại.");
    document.querySelector(".mic-button").classList.remove("listening");
  };

  recognition.onend = function() {
    document.querySelector(".mic-button").classList.remove("listening");
  };
}


// ✅ Gửi tin nhắn khi nhấn Enter
document.getElementById("message-input").addEventListener("keydown", function(e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
