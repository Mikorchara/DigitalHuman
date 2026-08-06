# ===== after: web/app.js, sendMsg + disableInput + enableInput =====

function sendMsg() {
    var t = inputEl.value.trim(); if (!t) return;
    addMsg("user", t);
    inputEl.value = "";
    disableInput(true);
    // double rAF：等浏览器完成 DOM 重绘后再发桥接请求
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

// Python 调用解锁
function enableInput() { disableInput(false); }

// ... Python 兼容层末尾新增 ...

function enableInput() { disableInput(false); }