# ==========================================
# 🌐 QueryAIWebSocket - WebSocket 路由（稳定版）
# ------------------------------------------
#  路径：/ws/ai-coach      ※ Main.py 中 include_router 时不再加 prefix
#  特点：
#   • 入口不 accept，交给 SessionManager.Register
#   • 事件装饰器 @RegisterEvent，新增参数校验
#   • 任何异常只打印日志 & 友好回复，不炸链接
# ==========================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from Source.Managers.SessionManager import SessionManager
from Source.Managers.QuestionManager import QuestionManager
from Source.Managers.AIInteractionManager import AIInteractionManager

Router = APIRouter()

# ---------- 事件表 ----------
EventRouter = {}
def RegisterEvent(Name):          # 🎯 装饰器
    def Decorator(Func):
        EventRouter[Name] = Func
        return Func
    return Decorator

# ---------- 主入口 ----------
@Router.websocket("/ws/ai-coach")
async def QueryAIWebSocket(WS: WebSocket):
    UserId = await SessionManager.Register(WS)     # 💡 这里会 accept

    try:
        while True:
            try:
                Msg = await WS.receive_json()
            except WebSocketDisconnect:
                break
            except Exception as Err:
                print(f"[解析异常] {Err}")
                await SessionManager.SendText(UserId, "非法消息格式")
                continue

            Event = Msg.get("Event")
            Params = Msg.get("Params") or {}

            Handler = EventRouter.get(Event)
            if not Handler:
                await SessionManager.SendText(UserId, f"未知事件：{Event}")
                continue

            try:
                await Handler(UserId, Params)
            except Exception as Err:
                print(f"[处理 {Event} 异常] {Err}")
                await SessionManager.SendText(UserId, f"{Event} 处理出错")

    finally:
        await SessionManager.Unregister(UserId)

# ---------- 事件：NextQuestion ----------
@RegisterEvent("NextQuestion")
async def HandleNextQuestion(UserId: str, Params: dict):
    Result = dict()
    QuestionManager.NextQuestion(UserId, Params, Result)
    await SessionManager.SendJson(UserId, {
        "Event": "NextQuestion",
        "Data": Result
    })

# ---------- 事件：CheckAnswer ----------
@RegisterEvent("CheckAnswer")
async def HandleCheckAnswer(UserId: str, Params: dict):
    Result = dict()
    QuestionManager.CheckAnswer(UserId, Params, Result)

    await SessionManager.SendJson(UserId, {
        "Event": "CheckAnswer",
        "Data": Result
    })
#
# ---------- 事件：AskAI ----------
@RegisterEvent("AskAI")
async def HandleAskAI(UserId: str, Params: dict):
    Result = dict()
    async for Tok in AIInteractionManager.AskAI(UserId, Params, Result):
        await SessionManager.SendJson(UserId, {"Event": "StreamReply", "Data": Result})
