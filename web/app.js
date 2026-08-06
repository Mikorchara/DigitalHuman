let bridge = null;
new QWebChannel(qt.webChannelTransport, function(ch) { bridge = ch.objects.bridge; });

// ── Live2D canvas 管理 ──────────────────────────────────
// 核心原则：只用 CSS 控制 canvas 显示尺寸，不碰 canvas.width/height。
// 因为设置 canvas.width/height 会立即清空 WebGL 绘制缓冲区 → 闪白。
// Live2D SDK 内部用 clientWidth/clientHeight 计算视口矩阵，CSS 尺寸足矣。
var panel = document.getElementById("live2d-panel");
var _canvasAdopted = false;

function adoptCanvas(c) {
    if (_canvasAdopted && c.parentElement === panel) return;
    
    panel.appendChild(c);
    c.style.width = "100%";
    c.style.height = "100%";
    c.style.display = "block";
    _canvasAdopted = true;

    // 仅首次设置一次 canvas 内部分辨率（让 SDK 视口矩阵匹配）
    // 注意：这一步仍会清空 WebGL 缓冲区，但只发生一次
    // 我们用 requestAnimationFrame 确保在下一帧前 SDK 已重新绘制
    var w = panel.clientWidth;
    var h = panel.clientHeight;
    if (w > 0 && h > 0 && (c.width !== w || c.height !== h)) {
        c.width = w; c.height = h;
    }
    console.log("[Live2D] canvas adopted (" + c.width + "x" + c.height + ")");
}

// MutationObserver 捕获 SDK 动态创建的 canvas
var observer = new MutationObserver(function(mutations) {
    for (var i = 0; i < mutations.length; i++) {
        var nodes = mutations[i].addedNodes;
        for (var j = 0; j < nodes.length; j++) {
            if (nodes[j].tagName === "CANVAS") adoptCanvas(nodes[j]);
        }
    }
});
observer.observe(document.body, { childList: true, subtree: true });

// 兜底轮询：前 3 秒每 300ms 扫一次，找到就停
var pollCount = 0;
var pollTimer = setInterval(function() {
    pollCount++;
    if (_canvasAdopted || pollCount > 10) { clearInterval(pollTimer); return; }
    var cans = document.querySelectorAll("canvas");
    for (var k = 0; k < cans.length; k++) adoptCanvas(cans[k]);
}, 300);

// Chat
var msgsEl = document.getElementById("chat-messages");
var inputEl = document.getElementById("chat-input");
var sendBtn = document.getElementById("send-btn");
sendBtn.onclick = function() {
    if (sendBtn.disabled) return;
    if (sendBtn.textContent === "✕") cancelRequest();
    else sendMsg();
};
inputEl.onkeydown = function(e) {
    if (e.key === "Enter" && !inputEl.disabled) sendMsg();
};

function sendMsg() {
    var t = inputEl.value.trim();
    if (!t && !_fileContent) return;

    var displayText = t || "";      // 聊天区显示（可能只是文件名）
    var sendText = t || "";         // 发给 AI（可能包含全文）

    if (_fileContent) {
        sendText = "[文件: " + _fileName + "]\n" + _fileContent + "\n[/文件]" + (t ? "\n\n" + t : "");
        displayText = "📄 " + _fileName + (t ? "\n" + t : "");
        _fileContent = null; _fileName = null;
        document.getElementById("file-status").textContent = "";
    }

    addMsg("user", displayText);     // 界面简洁
    inputEl.value = "";
    disableInput(true);

    if (bridge) {
        requestAnimationFrame(function() {
            requestAnimationFrame(function() {
                bridge.send_message(sendText);  // AI 收全文
            });
        });
    } else {
        addMsg("assistant", "连接未就绪");
        disableInput(false);
    }
}

function disableInput(locked) {
    inputEl.disabled = locked;
    if (locked) {
        sendBtn.textContent = "✕";
        sendBtn.title = "取消";
        inputEl.placeholder = "AI 正在回复...";
        inputEl.style.opacity = "0.6";
    } else {
        sendBtn.textContent = "➤";
        sendBtn.title = "发送";
        inputEl.placeholder = "输入消息，按 Enter 发送...";
        inputEl.style.opacity = "1";
        inputEl.focus();
    }
}

// 取消当前 AI 请求
function cancelRequest() {
    if (bridge) bridge.cancel();
    disableInput(false);
}
function addMsg(role, text) {
    var d = document.createElement("div");
    d.className = "msg " + role;
    d.textContent = text;
    msgsEl.appendChild(d);
    msgsEl.scrollTop = msgsEl.scrollHeight;
}
// ---- Live2D 控制桥接（调用 SDK 暴露的 window.Live2D API） ----
function setExpression(id) {
    if (window.Live2D) { window.Live2D.setExpression(id); }
    else { console.warn("[Expr] Live2D API not ready"); }
}
function setParameter(p) {
    if (window.Live2D) { window.Live2D.setParameter(p.id, p.value); }
    else { console.warn("[Param] Live2D API not ready"); }
}
function playMotion(m) {
    if (window.Live2D) { window.Live2D.playMotion(m.group, m.no); }
    else { console.warn("[Motion] Live2D API not ready"); }
}
// Speech lip sync: rhythmical mouth open/close based on text
function startSpeechLipSync(p) {
    if (window.Live2D) { window.Live2D.startSpeechLipSync(p.text, p.durMs || 5000); }
    else { console.warn("[Speech] Live2D API not ready"); }
}
function stopLipSync() {
    if (window.Live2D) { window.Live2D.stopLipSync(); }
    else { console.warn("[LipSync] Live2D API not ready"); }
}
function setAutoIdle(enabled) {
    if (window.Live2D) { window.Live2D.setAutoIdle(enabled); }
    else { console.warn("[AutoIdle] Live2D API not ready"); }
}

// Python 兼容层 — main_window.py send_to_web("addMessage", {role, content})
function addMessage(obj) { addMsg(obj.role, obj.content); }

// Python 调用：解锁输入框
function enableInput() { disableInput(false); }

// TTS 语音开关
function toggleTTS() {
    if (bridge) bridge.toggle_tts();
}
function setTTSState(enabled) {
    var btn = document.getElementById("tts-btn");
    if (enabled) {
        btn.textContent = "🔊"; btn.title = "语音: 开";
        btn.style.opacity = "1";
    } else {
        btn.textContent = "🔇"; btn.title = "语音: 关";
        btn.style.opacity = "0.4";
    }
}

// ── 上下文面板 ──────────────────────────────────────────
var ctxPanel = document.getElementById("context-panel");

function toggleContextPanel() {
    var visible = ctxPanel.style.display !== "none";
    if (visible) {
        ctxPanel.style.display = "none";
        document.getElementById("chat-panel").style.display = "";
    } else {
        document.getElementById("chat-panel").style.display = "none";
        ctxPanel.style.display = "";
        if (bridge) bridge.request_history();  // 请求历史数据
    }
}

function showHistory(history) {
    var list = document.getElementById("context-list");
    list.innerHTML = "";
    for (var i = 0; i < history.length; i++) {
        var m = history[i];
        var div = document.createElement("div");
        div.className = "ctx-msg ctx-" + m.role;
        div.textContent = (m.role === "user" ? "User : " : "Robot : ") + m.content;
        list.appendChild(div);
    }
    if (history.length === 0) {
        list.innerHTML = '<div class="ctx-empty">暂无对话历史</div>';
    }
}

function undoRound() {
    if (bridge) bridge.undo_round();
}

function clearAllContext() {
    if (bridge) bridge.clear_context();
}

function summarizeContext() {
    if (bridge) bridge.summarize_context();
}

// ── 参考资料 ──────────────────────────────────────────
function showReference(text) {
    document.getElementById("context-ref-editor").value = text || "";
}

function saveReference() {
    var text = document.getElementById("context-ref-editor").value;
    if (bridge) bridge.save_reference(text);
}

// 打开上下文面板时自动加载参考资料
var _origToggleContext = toggleContextPanel;
toggleContextPanel = function() {
    _origToggleContext();
    if (document.getElementById("context-panel").style.display !== "none" && bridge) {
        bridge.request_reference();
    }
};

// ── 人设面板 ──────────────────────────────────────────
var personaPanel = document.getElementById("persona-panel");
var _defaultPersona = "你叫 Haru，是一个活泼可爱的桌面虚拟助手。\n请用简洁、自然的中文回答，像朋友聊天一样。\n每次回复控制在 2-5 句话。";

function togglePersonaPanel() {
    var visible = personaPanel.style.display !== "none";
    if (visible) {
        personaPanel.style.display = "none";
        document.getElementById("chat-panel").style.display = "";
    } else {
        document.getElementById("chat-panel").style.display = "none";
        personaPanel.style.display = "";
        if (bridge) bridge.request_persona();
    }
}

function showPersona(text) {
    document.getElementById("persona-editor").value = text || "";
}

function savePersona() {
    var text = document.getElementById("persona-editor").value;
    if (bridge) bridge.save_persona(text);
}

function resetPersona() {
    document.getElementById("persona-editor").value = _defaultPersona;
}

// ── 文件输入 ──────────────────────────────────────────
var _fileContent = null;   // 待附加的文件内容
var _fileName = null;

function toggleFileInput() {
    var row = document.getElementById("file-input-row");
    var input = document.getElementById("file-path");
    if (row.style.display === "none") {
        row.style.display = "";
        input.focus();
    } else {
        row.style.display = "none";
        _fileContent = null;
        _fileName = null;
        document.getElementById("file-status").textContent = "";
    }
}

function loadFile() {
    var path = document.getElementById("file-path").value.trim();
    if (!path) return;
    document.getElementById("file-status").textContent = "加载中...";
    if (bridge) bridge.request_file(path);
}

function fileContent(data) {
    _fileContent = data.text;
    _fileName = data.name;
    document.getElementById("file-status").textContent = "✅ " + data.name + " (" + data.text.length + " 字)";
    document.getElementById("file-path").value = "";
}

function fileError(msg) {
    _fileContent = null;
    _fileName = null;
    document.getElementById("file-status").textContent = "❌ " + msg;
}
