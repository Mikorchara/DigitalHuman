# 已知问题 & 解决记录

## 1. PySide6 WebEngine
`pip install PySide6-WebEngine` 不存在 → `PySide6-Essentials + PySide6-Addons`

## 2. Cubism 5 无 live2d.min.js
Framework 改为 TS 源码 → 直接用 SDK Demo dist (sdk_dist/assets/)

## 3. file:// 协议不可用
`../../Framework/...` 相对路径在 `file://` 下解析失败 → 内建 HTTP server

## 4. 手写 WebGL 渲染器不可行（核心教训）
投影矩阵、multiply+screen 着色器、blendMode、mask 渲染无法手写覆盖。
**结论**：直接用 SDK dist。

## 5. Shader 文件不能手写
缺少 SDK Framework 期望的完整 14 个 Shader 文件 → 从 SDK `Framework/Shaders/WebGL/` 复制

## 6. SDK 模型 motion 引用需修复
`model3.json` 内 `motions/Hiyori_m*.json` 与实际文件名 `Haru_m*.json` 不匹配 → 批处理替换

## 7. JS 诊断
`Live2DPage(QWebEnginePage).javaScriptConsoleMessage` → Python 终端

## 8. canvas 归属问题
SDK 在 `document.body` 下动态创建 canvas → MutationObserver 监听 `body > canvas` 自动迁移到 `#live2d-panel` 右侧面板。避免 iframe 隔离导致无法控制 canvas。

## 9. 数字人闪白 + 背景加载一半（已修复）
**原因**：canvas 移动时面板背景短暂露出 → 闪白；canvas.width/height 与 CSS 不同步 → WebGL 只渲染一半。
**修复**：面板背景纯色 `#dbeafe`；移动后 `setTimeout` 强制同步尺寸 + 500ms 轮询兜底。

## 10. "Shader program is not initialized" 刷屏（已修复）
SDK 编译产物在模型切换/初始化时会反复打这个 warning，不影响渲染但刷满终端。
**修复**：在 `Live2DPage.javaScriptConsoleMessage` 中添加关键词过滤，匹配到 "Shader program is not initialized" 时直接 return 不打印。

## 11. setParameterValueById 张嘴无效 / 静止时嘴张很大
**现象**：调 `setParameterValueById('ParamMouthOpenY', 1.0)` 看不出效果；或不发消息时嘴反而一直张着。

**根因**：
- Breath/LipSync 更新器在每帧 `onLateUpdate` 阶段覆盖嘴参数。外部一次性的 `setParameter` 下一帧就被重置。
- `saveParameters()` 永久保存参数到模型内部，下帧 `loadParameters()` 自动恢复。如果 `stopManualLipSync` 只删标志位而不显式复位参数，张嘴脏数据永远循环。

**最终方案**：
1. `lappmodel.ts`：`_lipSyncForm/_lipSyncOpen` 标志位 + `startManualLipSync/stopManualLipSync`
2. `update()` 末尾：`if (_lipSyncForm !== null) { 强设嘴参数 }` → `_model.update()`（渲染）
3. `stopManualLipSync()` 必须同时设回 `ParamMouthForm=1.0, ParamMouthOpenY=0.0`
4. `main.ts`：`clearTimeout` 防止快速连发消息时多个 timer 冲突

**Haru 张嘴正确参数组合**：`ParamMouthForm=-2.0` + `ParamMouthOpenY=1.0`。单个参数看不出。

## 12. 点击右侧人物区无反应，点击左侧却触发随机动作（已修复）

**现象**：
- 点击右侧 Live2D 人物（canvas 区域）不触发动作
- 点击左侧聊天面板却触发随机 Idle 动作
- 在右侧人物区拖动鼠标（pointermove）却有反应

**根因**：
SDK 在 `lappdelegate.ts` 里把 `pointerdown/pointerup` 挂到了 `document` 上，所有页面点击都会进入 `lappsubdelegate.ts` 的事件处理。但坐标转换用的是 `canvas.offsetLeft/offsetTop`，这在 canvas 被 MutationObserver 动态迁移到 `#live2d-panel`（flex 右侧布局）后不准确——`offsetLeft/offsetTop` 相对于父元素，而非文档整体。导致：
- 右侧点击算出的 `localX/localY` 超出 `canvas.width/canvas.height`，被边界检查拦截
- 左侧点击算出的坐标刚好落在 canvas 尺寸范围内，反而触发动作
- 拖动时同样使用了错误的坐标，但因为落在范围内所以有反应

**最终方案**（`lappsubdelegate.ts`）：
1. 统一用 `canvas.getBoundingClientRect()` 替代 `offsetLeft/offsetTop`，精确获取 canvas 在页面中的真实位置
2. `onPointBegan`：先算坐标再判断是否在 canvas 内，只有在范围内才设 `_captured = true` 并调用 `onTouchesBegan`，否则 `_captured = false` 直接返回
3. `onPointMoved` / `onPointEnded` / `onTouchCancel`：先检查 `_captured`，未捕获则直接返回；都用 `getBoundingClientRect()` 计算坐标
4. `onPointEnded` / `onTouchCancel` 保持边界检查作为双重保险

**关键文件**：
- `CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/lappsubdelegate.ts` — 触摸事件处理
- 编译后需同步 `dist/assets/*` → `web/sdk_dist/assets/`，更新 `index.html` 中的 `<script>` 引用

## 12. tsconfig.json baseUrl 弃用警告（可忽略）
TS 5.9 不支持 `ignoreDeprecations`。`npm run build` 完全通过，仅 IDE schema 提示。

## 13. TTS 语音合成部署错误集（2026-06-28）

| 错误 | 原因 | 修复 |
|------|------|------|
| `ModuleNotFoundError: edge_tts` | 虚拟环境未安装 | `pip install edge-tts pygame` |
| `pygame.error: mixer not initialized` | worker 线程读时长未 init mixer | `_synth_worker` 内自己 `pygame.mixer.init()` |
| 口型不触发 | daemon 线程 `QTimer` 无效 | 改用主线程 `QTimer` + `queue.Queue` 轮询 |
| 回复内容不更新 | `__pycache__` 缓存旧 `.pyc` | 每次改 `.py` 后 `Remove-Item __pycache__ -Recurse -Force` |
| `RuntimeError: Event loop is closed` | Windows Python 3.9 daemon 线程清理警告 | 无害，不影响功能 |
| 长文本口型差 ~3s | 标点停顿机制累积偏差 | 取消标点特殊处理，所有字符均分总时长 |

## 14. 背景图不生效 / CSS 改 background 无效（2026-07-14）

**现象**：多次修改 CSS 和图片文件都无法改变 Live2D 区域的背景。

**根因**：背景由 **SDK WebGL 精灵** 渲染，不是 CSS。`lappdefine.ts:42` 的 `BackImageName` 决定文件名，`lappview.ts:136-145` 把图片加载为 `LAppSprite` 画在 canvas 上，CSS 的 `background` 被 canvas 完全遮住。

**换背景正确流程**：
1. 图片放到 `web/Resources/` 下
2. 改 `lappdefine.ts:42` 的 `BackImageName`
3. `npm run build` → 同步 `dist/assets/` → 更新 `index.html <script>`
