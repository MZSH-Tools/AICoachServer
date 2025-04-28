# ==========================================
# 🌐 QueryAIWebSocket - WebSocket 总路由
# ------------------------------------------
# 接入点：/ws/query-ai
# - 每个客户端自动分配 UUID 标识
# - 支持事件类型分发（如 NextQuestion、CheckAnswer）
# - 事件结构：{ "Event": "事件名", "Params": { ... } }
# - 所有处理函数独立解耦，参数自解析
# ==========================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from App.Managers.SessionManager import SessionManager
from App.Core.QuestionManager import QuestionManager, _QuestionItem

Router = APIRouter()


# ============================
# 🎯 事件处理函数注册表
# ============================
EventRouter = {}


def RegisterEvent(Name):
    def Decorator(Func):
        EventRouter[Name] = Func
        return Func
    return Decorator


# ============================
# 🚪 主接入路由
# ============================
@Router.websocket("/ws/query-ai")
async def QueryAIWebSocket(WebSocketObj: WebSocket):
    UserId = await SessionManager.Register(WebSocketObj)

    try:
        while True:
            RawMsg = await WebSocketObj.receive_json()
            Event = RawMsg.get("Event")
            Params = RawMsg.get("Params", {})

            if Event in EventRouter:
                await EventRouter[Event](UserId, Params)
            else:
                await SessionManager.SendJson(UserId, {
                    "Event": "Error",
                    "Data": f"未知事件类型：{Event}"
                })

    except WebSocketDisconnect:
        await SessionManager.Unregister(UserId)


# ============================
# 📤 事件：NextQuestion
# ============================
@RegisterEvent("NextQuestion")
async def HandleNextQuestion(UserId: str, Params: dict):
    Exclude = Params.get("Exclude", [])
    RandomOption = Params.get("RandomOption", True)
    OptionLabels = Params.get("OptionLabels", ["A", "B", "C", "D"])

    Question = QuestionManager.GetRandomQuestion(Exclude, RandomOption, OptionLabels)
    if Question:
        await SessionManager.SendJson(UserId, {
            "Event": "NextQuestion",
            "Data": Question.__dict__  # 可改为 ToDict() 更优
        })


# ============================
# 📤 事件：CheckAnswer
# ============================
@RegisterEvent("CheckAnswer")
async def HandleCheckAnswer(UserId: str, Params: dict):
    Raw = Params.get("Question")
    Answer = Params.get("Answer", "")
    OptionLabels = Raw.get("OptionLabels", ["A", "B", "C", "D"])

    Question = _QuestionItem(Raw, QuestionManager.ProjectRoot, False, OptionLabels)
    Success, Feedback = QuestionManager.CheckAnswer(Question, Answer)

    await SessionManager.SendJson(UserId, {
        "Event": "CheckAnswer",
        "Data": {
            "Success": Success,
            "Feedback": Feedback
        }
    })

