# ===== before: web/app.js, sendMsg + disableInput 函数 =====

function sendMsg() {
    var t = inputEl.value.trim(); if (!t) return;
    addMsg("user", t);
    inputEl.value = "";
    disableInput(true);
    if (bridge) {
        requestAnimationFrame(function() {
            requestAnimationFrame(function() {
                bridge.send_message(t);
            });
        });
    } else {
        addMsg("assistant", "连接未就绪");
        disableInput(false);
    }
}

function disableInput(locked) {
    inputEl.disabled = locked;
    sendBtn.disabled = locked;
    if (locked) {
        inputEl.placeholder = "AI 正在回复...";
        inputEl.style.opacity = "0.6";
    } else {
        inputEl.placeholder = "输入消息，按 Enter 发送...";
        inputEl.style.opacity = "1";
        inputEl.focus();
    }
}

function enableInput() { disableInput(false); }