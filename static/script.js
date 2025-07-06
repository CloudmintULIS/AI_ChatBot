async function sendMessage() {
  const input = document.getElementById("message-input");
  const message = input.value.trim();
  if (!message) return;

  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<div><b>Bạn:</b> ${message}</div>`;

  const res = await fetch("/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  });
  const data = await res.json();

  chatBox.innerHTML += `<div><b>AI:</b> ${data.reply}</div>`;
  input.value = "";

  const audio = new Audio(data.audio);
  audio.play();
}
