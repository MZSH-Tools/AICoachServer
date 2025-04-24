import requests
import json
from App.Core.QuestionManager import QuestionManager
from App.Core.ConfigManager import ConfigManager

class AIInteraction:
    def __init__(self):
        self.Config = ConfigManager()
        self.ModelURL = self.Config.GetString("模型地址", "http://localhost:11434/api/generate")
        self.ModelName = self.Config.GetString("模型名称", "deepseek-r1:14b")

    @staticmethod
    def BuildPrompt(UserInput="", Explanations=None) -> str:
        PromptText = "你是一个严肃认真的驾校教练，正在帮助学生练习科目一考试，我会为你提供问题解析库，请根据用户输入找到相关问题的解析并回答给用户。"
        PromptText += "如果用户想要开始做下一道题，请你回复四个字符'下一道题'。"
        PromptText += "如果用户问的问题没有在解析库找到相关解析，请你回复四个字符'没有找到'。"
        PromptText += f"用户输入是:{UserInput}。"
        PromptText += f"解析库是{Explanations}。"
        return PromptText

    def QueryStream(self, PromptText: str) -> str:
        Payload = {
            "model": self.ModelName,
            "prompt": PromptText,
            "stream": False
        }
        try:
            Response = requests.post(self.ModelURL, json=Payload, timeout=20)
            Response.raise_for_status()
            Data = Response.json()
            return Data.get("response", "")
        except Exception as Error:
            return f"[请求出错] {str(Error)}"
