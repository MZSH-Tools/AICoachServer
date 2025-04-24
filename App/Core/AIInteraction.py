# ==========================================
# 🤖 AIInteraction - 模型调用封装（单例）
# ------------------------------------------
# 用于与 Ollama 模型服务交互：
# - 支持流式生成回复（StreamReply）
# - 自动使用模型地址池（ModelPoolManager）
# - 使用配置中心获取模型名
# - 作为 WebSocket 或 HTTP 问答的模型底层引擎
# ==========================================

import httpx
import json
from App.Config.ConfigManager import ConfigManager
from App.Managers.ModelPoolManager import ModelPoolManager


class _AIInteraction:
    def __init__(self):
        self.Config = ConfigManager
        self.ModelName = self.Config.GetString("模型名称", "deepseek-r1:14b")

    async def StreamReply(self, PromptText: str):
        """
        调用支持 stream=true 的模型 API 接口，返回生成中的 token 片段。
        """
        Url = await ModelPoolManager.GetAvailableNode()
        if not Url:
            yield "[ERROR] 当前无可用模型服务节点"
            return

        try:
            async with httpx.AsyncClient(timeout=None) as Client:
                Request = Client.build_request(
                    method="POST",
                    url=Url.Url,
                    json={
                        "model": self.ModelName,
                        "prompt": PromptText,
                        "stream": True
                    }
                )
                async with Client.stream(Request.method, Request.url, content=Request.content) as Response:
                    async for Line in Response.aiter_lines():
                        if not Line.strip():
                            continue
                        try:
                            Chunk = json.loads(Line)
                            if Chunk.get("done"):
                                break
                            Text = Chunk.get("response", "")
                            if Text:
                                yield Text
                        except Exception as Error:
                            yield f"[ERROR] 无法解析模型输出：{Error}"
        finally:
            ModelPoolManager.ReleaseNode(Url)


# ✅ 单例实例暴露
AIInteraction = _AIInteraction()

