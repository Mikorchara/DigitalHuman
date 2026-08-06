# ===== before: web/app.js, L56-61（sendMsg 函数）=====

function sendMsg() {
    var t = inputEl.value.trim(); if (!t) return;
    addMsg("user", t); inputEl.value = "";
    if (bridge) bridge.send_message(t);
    else addMsg("assistant", "连接未就绪");
}