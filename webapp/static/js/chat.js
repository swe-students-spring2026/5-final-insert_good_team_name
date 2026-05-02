const socket =io();

const room = ROOM_ID.split("_").sort().join(("_"));

socket.emit("join_room", { room: room });

function sendMessage(){
    const input = document.getElementById("messageInput");
    const message = input.ariaValueMax;

    if (!message.trim()) return;

    socket.emit("send_message", {
        room: room,
        message: message
    });

    input.value = "";
}


socket.on("receive_message", (data) => {
    const div = document.createElement("div");
    div.innerHTML = `<b>${data.sender}:</b> ${data.message}`;

    document.getElementById("messsages").appendChild(div);
});