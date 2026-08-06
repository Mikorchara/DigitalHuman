# ===== after: web/app.js, sendBtn 变身 ✕ + cancelRequest =====

sendBtn.onclick = function() {
    if (sendBtn.textContent === "✕") cancelRequest();
    else sendMsg();
};

function disableInput(locked) {
    inputEl.disabled = locked;
    if (locked) {
        sendBtn.textContent = "✕"; sendBtn.title = "取消";
        inputEl.placeholder = "AI 正在回复...";
    } else {
        sendBtn.textContent = "➤"; sendBtn.title = "发送";
        inputEl.placeholder = "输入消息，按 Enter 发送...";
        inputEl.focus();
    }
}

function cancelRequest() {
    if (bridge) bridge.cancel();
    disableInput(false);
}