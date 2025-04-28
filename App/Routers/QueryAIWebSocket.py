# ==========================================
# 🌐 QueryAIWebSocket - WebSocket 总路由
# ------------------------------------------
# 接入点：/ws/ai-coach
# - 每个客户端自动分配 UUID 标识
# - 支持事件类型分发（如 NextQuestion、CheckAnswer、AskAI）
# - 事件结构：{ "Event": "事件名", "Params": { ... } }
# ==========================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from App.Managers.SessionManager import SessionManager
from App.Core.QuestionManager import QuestionManager, _QuestionItem
from App.Core.AIInteraction import AIInteraction

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
@Router.websocket("/ws/ai-coach")
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
            "Data": Question.__dict__
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

# ============================
# 📤 事件：AskAI（自由提问）
# ============================
@RegisterEvent("AskAI")
async def HandleAskAI(UserId: str, Params: dict):
    QuestionId = Params.get("QuestionId", "")
    Query = Params.get("Query", "")

    ExplanationList = QuestionManager.GetExplanationById(QuestionId)

    PromptText = BuildPrompt(Query, ExplanationList)

    async for Token in AIInteraction.StreamReply(PromptText):
        await SessionManager.SendJson(UserId, {
            "Event": "StreamReply",
            "Data": Token
        })

# ============================
# 🔧 辅助函数
# ============================
def BuildPrompt(UserInput, Explanations):
    Prompt = "你是一个严肃认真的驾校教练，正在帮助学生练习科目一考试。"
    Prompt += "根据提供的解析库内容，准确回答学生提出的问题。如果找不到答案，请回复'没有找到'。"
    Prompt += f"用户提问：{UserInput}\n"
    Prompt += f"解析库：{Explanations}\n"
    return Prompt
