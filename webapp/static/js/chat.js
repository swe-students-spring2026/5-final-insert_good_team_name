const socket = io();

const room = ROOM_ID.split("_").sort().join("_");

socket.emit("join_room", { room: room });

function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value;
    if (!message.trim()) return;
    socket.emit("send_message", { room: room, message: message });
    input.value = "";

    const indicator = document.getElementById("sent-indicator");
    indicator.style.display = "block";
    setTimeout(() => { indicator.style.display = "none"; }, 2000);
}

socket.on("receive_message", (data) => {
    const messagesDiv = document.getElementById("messages");
    const wrapper = document.createElement("div");
    const isMine = data.sender === current_user_id;
    wrapper.className = `message-wrapper ${isMine ? "wrapper-mine" : "wrapper-theirs"}`;

    const senderLabel = document.createElement("span");
    senderLabel.className = "message-sender";
    senderLabel.textContent = isMine ? "You" : other_name;
    senderLabel.style.textAlign = isMine ? "right" : "left";

    const div = document.createElement("div");
    div.className = `message ${isMine ? "message-mine" : "message-theirs"}`;
    div.innerHTML = `<p>${data.message}</p>`;

    if (!isMine) wrapper.appendChild(senderLabel);
    wrapper.appendChild(div);
    if (isMine) wrapper.appendChild(senderLabel);

    messagesDiv.appendChild(wrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});