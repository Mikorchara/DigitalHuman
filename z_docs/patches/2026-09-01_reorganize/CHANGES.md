# 修改日期：2026-09-01

## 修改文件
- `config.py` — 取消 git 跟踪，加入 `.gitignore`（密钥不入库） ---  modify_0(注)
- `config.example.py` — 新增配置模板（占位密钥 + 使用说明） ---  新增
- `.gitignore` — 新增 `config.py` 排除规则 ---  小改动
- `core/ai_client.py` — API Key 错误提示补充环境变量说明 ---  modify_0
- `AGENTS.md` — 按新规范整体重写（含修改规则，路径 z_dous→z_docs） ---  完全重写
- `README.md` — 目录结构/文档导航更新（z_dous→z_docs） ---  多处小改动
- `z_dous/` → `z_docs/` — 文档目录重命名与重组 ---  git mv

## 修改原因
1. **安全**：`config.py` 曾含明文 API Key 且被上传到 git（私有仓库），需将其排除并改为模板 + 环境变量方式。
2. **文档结构清晰**：按统一规范重组文档目录，删除旧补丁历史（git 历史中可恢复），重置 code_review 为空白。

## 修改内容
### 安全（密钥外置）
- `git rm --cached config.py`：取消跟踪，本地保留
- `.gitignore` 增加 `config.py`
- 新增 `config.example.py`：占位密钥 + "复制为 config.py 或设环境变量"说明
- `ai_client.py`：错误提示改为"请检查 config.py 或设置环境变量 DEEPSEEK_API_KEY"

### 文档重组（z_dous → z_docs）
- 保留：`troubleshooting.md`、`code_review.md`（重置为空白）
- 新建：`ROADMAP.md`、`BUILD_RUN.md`、`structure.md`
- 保留 `deep-dive/`（architecture、l2d-internals + 归档 日志/接口指南/known_issues）
- 删除：旧 `patches/` 全部内容、`others/` 冗余（code-review 副本、forMe）、`test_poem.txt`
- `AGENTS.md` 重写：项目信息 / 目标范围 / 架构决策 / 环境依赖 / 协作规范 / 修改规范
- `README.md` 同步更新

## 影响范围
- 代码运行不受影响（config.py 仍存在本地，未删）
- 克隆新环境需：`copy config.example.py config.py` 并填写密钥
- 文档路径全部改为 `z_docs/`
