# ==========================================
# 📡 SessionManager - WebSocket 会话池（重构稳定版）
# ------------------------------------------
#  功能：
#   • Register   —— 注册并 accept（只此一次）
#   • Unregister —— 断线清理，不重复 close
#   • SendJson / SendText —— 统一安全发送
# ==========================================

from typing import Dict, Optional
from uuid import uuid4
from starlette.websockets import WebSocket, WebSocketState

class _SessionManager:
    def __init__(self):
        self.ActiveConnections: Dict[str, WebSocket] = {}

    # ---------- 注册 ----------
    async def Register(self, WS: WebSocket) -> str:
        await WS.accept()                          # ✅ 只在这里 accept 一次
        UserId = str(uuid4())
        self.ActiveConnections[UserId] = WS
        print(f"[连接建立] 客户端 {UserId}")
        return UserId

    # ---------- 注销 ----------
    async def Unregister(self, UserId: str):
        WS: Optional[WebSocket] = self.ActiveConnections.pop(UserId, None)
        if WS and WS.application_state == WebSocketState.CONNECTED:
            await WS.close()
        print(f"[断开连接] 客户端 {UserId}")

    # ---------- 工具 ----------
    def Get(self, UserId: str) -> Optional[WebSocket]:
        return self.ActiveConnections.get(UserId)

    async def _SafeSend(self, WS: WebSocket, Payload: dict):
        try:
            await WS.send_json(Payload)
        except Exception as Err:
            print(f"[发送异常] {Err}")

    async def SendJson(self, UserId: str, Data: dict):
        WS = self.Get(UserId)
        if WS:
            await self._SafeSend(WS, Data)

    async def SendText(self, UserId: str, Text: str):
        await self.SendJson(UserId, {"Event": "Message", "Data": Text})

# ✅ 单例实例
SessionManager = _SessionManager()
