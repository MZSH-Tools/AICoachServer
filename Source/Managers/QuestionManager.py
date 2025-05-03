# ==========================================
# 📦 QuestionManager - 题库与状态管理器
# ==========================================

import os
import json
import random
from Source.Managers.PathManager import PathManager
from Source.Core.QuestionItem import QuestionItem


class _QuestionManager:
    def __init__(self):
        self.ProjectRoot = PathManager.GetProjectRoot()
        self.QuestionBank: dict[str, dict] = {}
        self.QuestionDict: dict[str, QuestionItem] = {}  # 用户题目缓存
        self.LoadQuestionBank()

    def LoadQuestionBank(self):
        BankPath = os.path.join(self.ProjectRoot, "Assets/Data/题库.json")
        if not os.path.exists(BankPath):
            print(f"[题库加载失败] 未找到文件：{BankPath}")
            return
        try:
            with open(BankPath, "r", encoding="utf-8") as f:
                Data = json.load(f)
                self.QuestionBank = {Item["题目ID"]: Item for Item in Data.get("题库", [])}
                print(f"[题库加载成功] 共加载题目 {len(self.QuestionBank)} 道")
        except Exception as e:
            print(f"[题库解析失败] {e}")

    def GetRandomQuestion(self, UserId: str, Params: dict) -> list[str] | None:
        Exclude = Params.get("Exclude", [])
        RandomOption = Params.get("RandomOption", True)
        OptionLabels = Params.get("OptionLabels", ["A", "B", "C", "D"])

        Candidates = [Q for Qid, Q in self.QuestionBank.items() if Qid not in Exclude]
        if not Candidates:
            return None

        Raw = random.choice(Candidates)
        Question = QuestionItem(Raw, self.ProjectRoot, RandomOption, OptionLabels)
        self.QuestionDict[UserId] = Question
        return self.FormatQuestionAsText(Question)

    def FormatQuestionAsText(self, Question: QuestionItem) -> list[str]:
        Lines = []
        if Question.Stem:
            Lines.append(f"[TEXT]  {Question.Stem}")
        if Question.Image:
            Lines.append(f"[IMAGE] {Question.Image}")
        for Label, Option in zip(Question.OptionLabels, Question.Options):
            if Option.get("文本"):
                Lines.append(f"[TEXT]  [{Label}] {Option['文本']}")
            if Option.get("真实图片路径"):
                Lines.append(f"[IMAGE] {Option['真实图片路径']}")
        return Lines

    def EvaluateAnswer(self, UserId: str, Answer: str) -> tuple[bool, str]:
        Question = self.QuestionDict.get(UserId)
        if not Question:
            return False, "未找到绑定题目"
        return self.CheckAnswer(Question, Answer)

    def CheckAnswer(self, Question: QuestionItem, Answer: str) -> tuple[bool, str]:
        if not Answer:
            return False, "未作答"
        if Answer in Question.CorrectAnswers:
            return True, "回答正确"
        return False, f"回答错误，正确答案是：{'、'.join(Question.CorrectAnswers)}"

    def ClearUserQuestion(self, UserId: str):
        self.QuestionDict.pop(UserId, None)


# ✅ 单例
QuestionManager = _QuestionManager()
