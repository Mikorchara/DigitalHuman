# Live2D 内部机制 — Haru 模型

> 面向需要修改 Live2D 行为的开发者。

---

## 模型文件结构

```
web/Resources/Haru/
├── Haru.moc3             模型本体（二进制）：顶点、网格、骨骼、默认参数值
├── Haru.model3.json       总索引：纹理/motion/物理/Pose 路径 + 参数分组
├── Haru.cdi3.json         参数清单：所有可调参数名和分组
├── Haru.physics3.json     物理模拟：头发、衣服摆动参数
├── Haru.pose3.json        姿势约束：限制参数取值范围（防穿模）
├── Haru.userdata3.json    点击区域 + 事件触发配置（当前闲置）
├── Haru.2048/             纹理图片（2 张 2048×2048 PNG）
├── motions/               逐帧动画数据
│   ├── Haru_m_idle_01.motion3.json  ~ Haru_m_idle_10.motion3.json
│   └── Haru_m_tap_body_01.motion3.json
└── back_class_normal.png  背景图（WebGL 精灵渲染）
```

---

## 关键参数

### 嘴部控制

张嘴的正确组合（两个参数必须同时设）：

| 参数 | 张嘴值 | 闭嘴值 |
|------|--------|--------|
| `ParamMouthForm` | **-2.0** | 1.0 |
| `ParamMouthOpenY` | **1.0** | 0.0 |

> ⚠️ 单独设其中一个参数看不出效果，必须成对设置。

### 默认姿势

默认姿势**不是代码定义的**，是建模师在 Live2D Cubism Editor 中设定的参数值，**直接烘焙在 `Haru.moc3` 二进制文件中**。

不播放动作时，角色保持这个烘焙的初始姿态不变（`_autoIdle=false`）。

---

## 已修改的 SDK 源文件

这些文件位于 `CubismSdkForWeb-5-r.5/Samples/TypeScript/Demo/src/`。修改后需重新编译部署。

### `lappmodel.ts` — 模型生命周期

```typescript
// 改动点 1：停用自动待机循环
_autoIdle = false;  // 原值: true

// 改动点 2：手动 LipSync 覆盖
_lipSyncForm: number | null = null;   // ParamMouthForm 的目标值
_lipSyncOpen: number | null = null;   // ParamMouthOpenY 的目标值

// update() 末尾：每帧检查标志位，覆盖嘴参数
if (this._lipSyncForm !== null) {
  // 强设嘴参数 → _model.update() 渲染
}
```

**停止 LipSync 时必须显式复位**：
```typescript
stopManualLipSync() {
  // 不能只删标志位！必须设回默认值
  ParamMouthForm = 1.0;
  ParamMouthOpenY = 0.0;
}
```

### `lappsubdelegate.ts` — 触摸事件

**改动**：点击坐标计算从 `offsetLeft/offsetTop` 改为 `getBoundingClientRect()`。

原始码用 `canvas.offsetLeft` 计算坐标，在 canvas 被 MutationObserver 迁移到 flex 右侧布局后不准确。改用 `getBoundingClientRect()` 获取相对于视口的真实位置。

### `main.ts` — 顶层 API

**改动**：
- 暴露 `window.Live2D` 全局 API
- Speech lip sync v4：`totalMs / 字符数` 精确平分，每周期 ±40ms 抖动 + 幅度 ±15%
- `clearTimeout` 防止快速连发消息时 timer 冲突

---

## 动作系统

### 三层架构

| 层 | 位置 | 说明 |
|----|------|------|
| **素材数据** | `motions/*.motion3.json` | 逐帧动画曲线，不改 |
| **动作引擎** | `Framework/src/motion/` | SDK 底层实现，不改 |
| **动作编排** | `Demo/src/` | 可改后重新编译 |

### 可用动作

Haru 有 10 个 Idle 动作 + 1 个 TapBody 动作。不播放时角色保持 `.moc3` 烘焙的初始姿态。

### 点击交互

`lapplive2dmanager.ts` 中的逻辑：
- 点击**头部**区域 → `setRandomExpression()`（随机表情）
- 点击**身体/其他** → `startRandomMotion(Idle, Force)`（随机动作）

---

## 背景渲染

背景由 **SDK WebGL 精灵** (`LAppSprite`) 渲染，**不受 CSS 控制**。

换背景的正确流程：
1. 图片放到 `web/Resources/`
2. 修改 `lappdefine.ts:42` 的 `BackImageName`
3. `npm run build` → 同步 dist → 更新 `index.html` 引用
