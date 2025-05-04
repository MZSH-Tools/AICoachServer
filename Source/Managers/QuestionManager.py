# ==========================================
# 📦 QuestionManager - 题库与状态管理器
# ==========================================

import os
import json
import random
from typing import List, Optional
from Source.Managers.PathManager import PathManager
from Source.Managers.ConfigManager import ConfigManager

class QuestionItem:
    def __init__(self, RawData: dict, RootPath: str, RandomOption: bool, OptionLabels: List[str]):
        self.ID = RawData.get("题目ID")
        self.Type = RawData.get("题目类型", "单选")
        self.Stem = RawData.get("题目", {}).get("文本", "")
        self.Image = self.ResolveImagePath(RawData.get("题目", {}).get("图片"), RootPath)
        self.Parse = RawData.get("题目解析", "")
        self.Options = RawData.get("选项", [])
        self.OptionLabels = OptionLabels[:len(self.Options)]

        if RandomOption:
            random.shuffle(self.Options)

        for Option in self.Options:
            Option["真实图片路径"] = self.ResolveImagePath(Option.get("图片"), RootPath)

        self.CorrectAnswers = [self.OptionLabels[i] for i, Option in enumerate(self.Options) if Option.get("是否正确")]
        self.Explanation = RawData.get("解析库", [])

    @staticmethod
    def ResolveImagePath(RelativePath: Optional[str], RootPath: str) -> str:
        if not RelativePath:
            return ""
        return os.path.join(RootPath, "Assets/Images", RelativePath)

class _QuestionManager:
    def __init__(self):
        self.ProjectRoot = PathManager.GetProjectRoot()
        self.QuestionBank: dict[str, dict] = {}
        self.QuestionDict: dict[str, QuestionItem] = {}  # 用户题目缓存
        self.LoadQuestionBank()

    def LoadQuestionBank(self):
        BankPath = os.path.join(self.ProjectRoot, ConfigManager.GetString("题目路径", "Data/QuestionBank.json"))
        if not os.path.exists(BankPath):
            print(f"[题库加载失败] 未找到文件：{BankPath}")
            return
        try:
            with open(BankPath, "r", encoding="utf-8-sig") as f:
                Data = json.load(f)
                self.QuestionBank = {Item["题目ID"]: Item for Item in Data.get("题库", [])}
                print(f"[题库加载成功] 共加载题目 {len(self.QuestionBank)} 道")
        except Exception as e:
            print(f"[题库解析失败] {e}")

    def NextQuestion(self, UserId: str, Params: dict, Result: dict):
        Exclude = Params.get("Exclude", [])
        RandomOption = Params.get("RandomOption", True)
        OptionLabels = Params.get("OptionLabels", ["A", "B", "C", "D"])

        Candidates = [Q for Qid, Q in self.QuestionBank.items() if Qid not in Exclude]
        if not Candidates:
            Result["Success"] = False
            Result["Question"] = []
            Result["ErrorStr"] = "没有筛选出来的题目"
            return
            
        Raw = random.choice(Candidates)
        Question = QuestionItem(Raw, self.ProjectRoot, RandomOption, OptionLabels)
        self.QuestionDict[UserId] = Question
        
        Result["Success"] = True
        Result["Question"] = self.FormatQuestionAsText(Question)

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

    def CheckAnswer(self, UserId: str, Params: dict, Result: dict):
        Result["Success"] = False
        Question = self.QuestionDict.get(UserId)
        if not Question:
            Result["ShowStr"] = "未找到绑定题目"
            return
        UserAnswer = Params.get("Answer", "").strip().upper()

        if UserAnswer == "":
            Result["ShowStr"] = "不能输入为空，请输入正确的答案"
            return

        UserAnswerArray = []
        for char in UserAnswer:
            if char not in Question.OptionLabels:
                Result["ShowStr"] = f"无效的选项: {char}"
                return
            UserAnswerArray.append(char)
            
        if len(UserAnswerArray) > 1 and Question.Type != "多选":
            Result["ShowStr"] = f"非多选题不能输入多个选项，请重新输入"
            return
            
        Result["Success"] = True
        AnswerStr = ""
        if len(UserAnswerArray) == len(Question.CorrectAnswers) and all(
                answer in Question.CorrectAnswers for answer in UserAnswerArray):
            AnswerStr = "回答正确！"
            if Params.get("ParseOnAnswerRight", False):
                AnswerStr += f"\n题目解析: {Question.Parse}"
        else:
            AnswerStr = "回答错误！"
            AnswerStr += f"正确答案是 {','.join(Question.CorrectAnswers)}"
            if Params.get("ParseOnAnswerError", True):
                AnswerStr += f"\n题目解析: {Question.Parse}"

        Result["ShowStr"] = AnswerStr

    def ClearUserQuestion(self, UserId: str):
        self.QuestionDict.pop(UserId, None)


# ✅ 单例
QuestionManager = _QuestionManager()
