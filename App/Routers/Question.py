from fastapi import APIRouter, Body
from App.Core.QuestionManager import QuestionManager
from App.Core.AIInteraction import AIInteraction

Router = APIRouter(prefix="/api")

Manager = QuestionManager()
AI = AIInteraction()

@Router.get("/next-question")
def GetNextQuestion():
    if Manager.NextRandomQuestion():
        Question = Manager.CurrentQuestion
        return {
            "题目ID": Question.ID,
            "题目类型": Question.Type,
            "题目文本": Question.Stem,
            "图片URL": Question.Image.replace("\\", "/").replace("assets/Images", "/assets"),
            "选项": [
                {
                    "编号": Label,
                    "文本": Opt["文本"],
                    "图片URL": Opt.get("真实图片路径", "").replace("\\", "/").replace("assets/Images", "/assets")
                }
                for Label, Opt in zip(Question.OptionLabels, Question.Options)
            ]
        }
    return { "错误": "无可用题目" }

@Router.post("/check-answer")
def CheckAnswer(Data = Body(...)):
    Answer = Data.get("answer", "")
    Done, Result = Manager.CheckAnswer(Answer)
    return {
        "答题完成": Done,
        "评语": Result
    }

@Router.post("/query-ai")
def QueryAI(Data = Body(...)):
    Input = Data.get("input", "")
    Explanation = Manager.GetExplanation()
    Prompt = AI.BuildPrompt(Input, Explanation)
    Result = AI.QueryStream(Prompt)
    return { "回复": Result }
