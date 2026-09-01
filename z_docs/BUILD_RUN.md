# 环境配置与运行指南 — Digital Human Chat

## 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.9+（建议 3.10+） |
| Node.js | 仅改 Live2D TS 源码时需要（SDK 编译） |
| OS | Windows（其他平台需相应调整） |

## 1. 创建虚拟环境与安装依赖

```powershell
cd d:\digital_human
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. 配置密钥（重要）

真实 API Key **不进入仓库**。首次运行前：

1. 复制模板：`copy config.example.py config.py`
2. 在 `config.py` 中填入真实 `LLM_API_KEY`；
   或设置环境变量（优先级更高）：
   ```powershell
   $env:DEEPSEEK_API_KEY = "sk-..."
   ```

> `config.py` 已被 `.gitignore` 排除，不会上传。

## 3. 运行程序

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned ; d:\digital_human\.venv\Scripts\Activate.ps1 ; $env:PYTHONPATH="." ; python d:\digital_human\main.py
```

## 4. 修改 Live2D TypeScript 后重新编译部署

```powershell
cd CubismSdkForWeb-5-r.5\Samples\TypeScript\Demo
npm run build
# → 把 dist/assets/* 覆盖到 web/sdk_dist/assets/
# → 更新 web/index.html 中 <script src="sdk_dist/assets/..."> 的文件名
```

## 5. 修改 Python 后清理缓存

```powershell
Get-ChildItem -Recurse __pycache__ | Remove-Item -Recurse -Force
```

## 6. 常见问题

- 网络/代理问题导致 DeepSeek 连接失败 → 见 `z_docs/troubleshooting.md`
- Live2D 背景/模型修改 → 见 `z_docs/deep-dive/`
