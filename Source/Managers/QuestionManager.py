# ==========================================
# 📦 QuestionManager - 题库与题目状态管理器
# ------------------------------------------
# 管理题库加载、题目抽取、判题、绑定用户状态
# ==========================================

import os
import json
import random
from typing import Optional
from Source.Core.QuestionItem import QuestionItem
from App.Managers.PathManager import PathManager


class _QuestionManager:
    def __init__(self):
        self.ProjectRoot = PathManager.ProjectRoot
        self.QuestionBank: dict[str, dict] = {}
        self.QuestionDict: dict[str, QuestionItem] = {}  # UserId → 当前题目
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

    def GetRandomQuestion(self, UserId: str, Exclude: list[str], RandomOption=True, OptionLabels=["A", "B", "C", "D"]):
        Candidates = [Q for Qid, Q in self.QuestionBank.items() if Qid not in Exclude]
        if not Candidates:
            return None
        Raw = random.choice(Candidates)
        Question = QuestionItem(Raw, self.ProjectRoot, RandomOption, OptionLabels)
        self.QuestionDict[UserId] = Question
        return Question

    def GetExplanationById(self, Qid: str) -> str:
        Raw = self.QuestionBank.get(Qid)
        return "\n".join(Raw.get("解析库", [])) if Raw else ""

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
