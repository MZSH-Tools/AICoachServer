# ================================
# 📡 QueryAIWebSocket
# --------------------------------
# WebSocket 接口：/ws/query-ai
# - 每个连接分配 UUID 标识
# - 接收用户消息
# - 实时返回 AI 回复（分段）
# - 保持长连接
# ================================

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from App.Managers.SessionManager import SessionManager
import asyncio

Router = APIRouter()

@Router.websocket("/ws/query-ai")
async def QueryAIWebSocket(WebSocketObj: WebSocket):
    # 注册连接并自动生成 UUID
    UserId = await SessionManager.Register(WebSocketObj)

    try:
        while True:
            # 接收客户端文本消息
            UserInput = await WebSocketObj.receive_text()
            print(f"[{UserId}] 收到提问：{UserInput}")

            # 模拟流式 AI 回复（1秒一段）
            Sentences = [f"{UserInput} 的回答如下：", "首先……", "然后……", "最后……"]
            for Sentence in Sentences:
                await SessionManager.SendJson(UserId, {
                    "Type": "Text",
                    "Data": Sentence
                })
                await asyncio.sleep(1)

            # 模拟语音（可替换为 edge-tts 合成）
            # AudioBytes = GenerateAudio(Sentence)
            # await SessionManager.SendAudio(UserId, AudioBytes)

    except WebSocketDisconnect:
        await SessionManager.Unregister(UserId)
