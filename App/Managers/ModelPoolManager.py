# ==========================================
# 📦 ModelPoolManager - 单例模型地址池管理器
# ------------------------------------------
# 本模块初始化后自动加载模型地址池
# - 使用 ConfigManager 读取配置
# - 模块加载时即完成初始化
# - 外部可直接使用 GetAvailableNode() / ReleaseNode()
# ==========================================

import asyncio
import httpx
import uuid
from collections import deque
from typing import Optional
from App.Managers.ConfigManager import ConfigManager


class ModelNode:
    def __init__(self, Url: str):
        self.Url = Url
        self.InUse = False
        self.TaskId = None


class _ModelPoolManager:
    def __init__(self):
        self.UrlPool: list[ModelNode] = []
        self.WaitingQueue: deque = deque()
        self.Config = ConfigManager
        self.InitPool()

    def InitPool(self):
        Urls = self.Config.GetList("模型地址池", [])
        self.UrlPool = [ModelNode(Url) for Url in Urls]
        print(f"[模型池初始化] 已加载 {len(self.UrlPool)} 个模型节点")

    async def GetAvailableNode(self) -> Optional[ModelNode]:
        TaskId = str(uuid.uuid4())

        while True:
            for Node in self.UrlPool:
                if Node.InUse:
                    continue
                if not await self.Ping(Node.Url):
                    continue
                Node.InUse = True
                Node.TaskId = TaskId
                print(f"[模型分配] 使用节点：{Node.Url}")
                return Node

            Future = asyncio.get_event_loop().create_future()
            self.WaitingQueue.append(Future)
            print("[模型排队] 所有节点忙，等待空闲...")
            await Future

    def ReleaseNode(self, Node: ModelNode):
        print(f"[释放节点] {Node.Url}")
        Node.InUse = False
        Node.TaskId = None

        if self.WaitingQueue:
            Future = self.WaitingQueue.popleft()
            if not Future.done():
                Future.set_result(True)

    async def Ping(self, Url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as Client:
                Resp = await Client.get(Url.replace("/generate", "/tags"))
                return Resp.status_code == 200
        except Exception:
            return False


# ✅ 单例实例导出，外部统一使用这个对象
ModelPoolManager = _ModelPoolManager()
