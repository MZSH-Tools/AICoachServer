# ==========================================
# 🤖 AIInteraction - 模型调用封装（单例）
# ------------------------------------------
# 用于与 Ollama 模型服务交互：
# - 支持流式生成回复（StreamReply）
# - 自动使用模型地址池（ModelPoolManager）
# - 使用配置中心获取模型名
# - 作为 WebSocket 或 HTTP 问答的模型底层引擎
# ==========================================
from typing import AsyncGenerator

import httpx
import json
from Source.Managers.ConfigManager import ConfigManager
from Source.Managers.ModelPoolManager import ModelPoolManager
from Source.Managers.QuestionManager import QuestionManager


class _AIInteractionManager:
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


    async def AskAI(self, UserId: str, Params: dict, Result: dict)-> AsyncGenerator[str, None]:
        ErrorShow = "抱歉没有找到相关问题解析，已发送后台管理人员接收。"
        Prompt = "你是一个严肃认真的驾校教练，正在帮助学生练习科目一考试，我会为你提供问题解析库，请根据用户输入找到相关问题的解析并回答给用户。"
        #Prompt += "如果用户想要开始做下一道题，请你回复四个字符'下一道题'。"
        Prompt += f"如果用户问的问题没有在解析库找到相关解析，请你不要进行任何修改直接回复以下字符'{ErrorShow}'。"
        UserInput = Params.get("UserInput", "")
        Prompt += f"用户输入是:{UserInput}。"
        Question = QuestionManager.QuestionDict.get(UserId)
        if not Question:
            Result["Success"] = False
            ErrorStr = "当前没有可用的题目信息，请先生成题目。"
            Result["ErrorStr"] = ErrorStr
            yield f"[ERROR] {ErrorStr}"
            return
        ExplanationMap = dict(Question.ExplanationMap)
        ExplanationMap.update(QuestionManager.ExplanationMap)
        Prompt += f"解析库是{ExplanationMap}。"

        Result["Success"] = True
        Result["Text"] = ""
        Result["Chunk"] = ""
        Result["Done"] = False
        Result["IsThinking"] = False
        async for Chunk in self.StreamReply(Prompt):
            if Chunk == "<think>":
                Result["IsThinking"] = True
                yield Chunk
            if Chunk == "</think>":
                Result["IsThinking"] = False
                yield Chunk
            Result["Chunk"] = Chunk
            Result["Text"] += Chunk
            yield Chunk
        Result["Done"] = True

# ✅ 单例实例暴露
AIInteractionManager = _AIInteractionManager()

