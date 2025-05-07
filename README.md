# AICoachServer

AICoachServer 是一套基于 **FastAPI + WebSocket** 的驾考 AI 练习后端。它负责题库管理、模型推理流式回复、WebSocket 会话管理以及静态资源（题目图片）托管，开箱即用，适合与任何前端（网页 / 桌面 / 移动端）对接。

---

## ✨ Features

| 模块 | 关键特性 |
|------|----------|
| `QueryAIWebSocket` | WebSocket 路由，事件装饰器分发 (`NextQuestion` / `CheckAnswer` / `AskAI`) |
| `SessionManager`   | 会话注册 / 注销 / 统一安全发送，支持多客户端并发 |
| `QuestionManager`  | 题库加载、随机出题、答题判定、解析合并 |
| `ModelPoolManager` | 多节点模型地址池、实时健康检测、排队调度 |
| `AIInteractionManager` | Ollama API 封装，流式 Token 推送 |
| `PathManager` & `ConfigManager` | 跨平台路径与 YAML 配置读取 |
| 静态资源托管 | `/Assets/**` 自动映射为 `http(s)://<Host>:<Port>/Assets/**` |

---

## ⚙️ Configuration (`Settings.yaml`)

```yaml
模型名称: deepseek-r1:14b
模型地址池:
  - http://127.0.0.1:11434/api/generate
题目路径: Data/QuestionBank.json
```

---

## 📦 Environment Setup

### Conda

```bash
conda env create -f environment.yaml
conda activate AICoachServer
```

### pip

```bash
pip install -r requirements.txt
```

---

## 🛰️ WebSocket API

| Event | Params Example                                                | Response                                       |
|-------|---------------------------------------------------------------|------------------------------------------------|
| `NextQuestion` | `{ "RandomOption": true, "OptionLabels": ["A","B","C","D"] }` | `{ "Event":"NextQuestion", "Params": Params }` |
| `CheckAnswer`  | `{ "UserInput": "A" }`                                        | `{ "Event":"CheckAnswer", "Params": Params }`               |
| `AskAI`        | `{ "UserInput": "为什么答案选B？" }`                                 | `{ "Event":"StreamReply", "Params": Params }`               |

---

## 📬 Contact

Need a custom Unreal Engine plugin or Python automation?<br>
**Email:** <mengzhishanghun@outlook.com>

---

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE) for details.
