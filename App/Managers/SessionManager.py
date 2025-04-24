# ==========================================
# 📡 SessionManager - WebSocket连接会话池
# ------------------------------------------
# 单例管理所有客户端的 WebSocket 长连接：
# - 自动注册连接
# - 自动断线清理
# - 支持推送文本 / JSON / 音频
# ==========================================

from typing import Dict
from fastapi import WebSocket


class _SessionManager:
    def __init__(self):
        self.ActiveConnections: Dict[str, WebSocket] = {}

    async def Register(self, WebSocketObj: WebSocket) -> str:
        await WebSocketObj.accept()
        from uuid import uuid4
        UserId = str(uuid4())
        self.ActiveConnections[UserId] = WebSocketObj
        print(f"[连接建立] 客户端 {UserId}")
        return UserId

    async def Unregister(self, UserId: str):
        WS = self.ActiveConnections.get(UserId)
        if WS:
            await WS.close()
            del self.ActiveConnections[UserId]
            print(f"[断开连接] 客户端 {UserId}")

    def Get(self, UserId: str) -> WebSocket | None:
        return self.ActiveConnections.get(UserId)

    async def SendText(self, UserId: str, Message: str):
        WS = self.Get(UserId)
        if WS:
            await WS.send_text(Message)

    async def SendJson(self, UserId: str, Data: dict):
        WS = self.Get(UserId)
        if WS:
            await WS.send_json(Data)

    async def SendAudio(self, UserId: str, Audio: bytes):
        WS = self.Get(UserId)
        if WS:
            await WS.send_bytes(Audio)


# ✅ 导出单例
SessionManager = _SessionManager()
