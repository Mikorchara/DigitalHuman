# 修改日期：2026-08-04

## 修改文件
- `core/ai_client.py` — 完全重写（Coze → DeepSeek） --- modify_0
- `ui/main_window.py` — 仅改函数名（call_coze → call_ai） --- modify_1

## 修改原因
Coze API 连接不稳定，迁移到 DeepSeek API（OpenAI 兼容格式）。
同时标准化接口命名为 `call_ai`（符合 `ai_interface_guide.md` 契约）。

## 修改内容
- 底层库：`requests` 手写 HTTP → `openai` 官方库
- API：Coze Bot API → DeepSeek Chat Completions API
- 人设：Coze 后台配置 → 代码内 `_SYSTEM_PROMPT`
- 函数名：主函数 `call_ai`，保留 `call_coze` 兼容别名
- 新增延迟初始化客户端、分类错误提示
- 修复：`X | None` → `Optional[X]`（Python 3.9 兼容）
- `requirements.txt`：新增 `openai>=1.0.0`

## 影响范围
- `core/ai_client.py`：完全重写
- `ui/main_window.py`：函数名 `call_coze` → `call_ai`
- `requirements.txt`：新增 `openai` 依赖
- 新建 `config.py`：集中管理 API Key 等配置
