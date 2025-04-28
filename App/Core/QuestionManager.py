# ==========================================
# 📘 QuestionManager - 单例题库管理器
# ------------------------------------------
# 用于加载与访问题库数据（JSON）
# 支持按题目ID获取题目、随机抽题、判题等操作。
# 模块加载时自动读取 ConfigManager 中配置的题库路径。
# 提供单例接口 QuestionManager 供全局使用。
# ==========================================

import os
import json
import random
from typing import Optional

from App.Managers.PathManager import PathManager
from App.Managers.ConfigManager import ConfigManager


class _QuestionItem:
    def __init__(self, RawData: dict, RootPath: str, RandomOption: bool, OptionLabels: list[str]):
        self.ID = RawData.get("题目ID")
        self.Type = RawData.get("题目类型", "单选")
        self.Stem = RawData.get("题目", {}).get("文本", "")
        self.Image = self.ResolveImagePath(RawData.get("题目", {}).get("图片"), RootPath)
        self.Options = RawData.get("选项", [])
        self.OptionLabels = OptionLabels[:len(self.Options)]
        if RandomOption:
            random.shuffle(self.Options)
        for Option in self.Options:
            Option["真实图片路径"] = self.ResolveImagePath(Option.get("图片"), RootPath)
        self.CorrectAnswers = [self.OptionLabels[i] for i, Option in enumerate(self.Options) if Option.get("是否正确")]
        self.Explanation = RawData.get("解析库", [])

    @staticmethod
    def ResolveImagePath(RelativePath, RootPath):
        if not RelativePath:
            return ""
        ImageRoot = os.path.join(RootPath, "Assets/Images")
        AbsolutePath = os.path.join(ImageRoot, RelativePath)
        return AbsolutePath if os.path.exists(AbsolutePath) else ""


class _QuestionManager:
    def __init__(self):
        self.Config = ConfigManager
        self.ProjectRoot = PathManager.GetProjectRoot()
        self.QuestionPath = PathManager.GetQuestionBankPath()
        self.AllQuestions = []
        self.Explanation = []
        self.LoadQuestions()

    def LoadQuestions(self):
        if not os.path.exists(self.QuestionPath):
            print(f"[题库管理] 题库文件不存在：{self.QuestionPath}")
            return

        try:
            with open(self.QuestionPath, "r", encoding="utf-8-sig") as File:
                Data = json.load(File)
                self.AllQuestions = Data.get("题库", [])
                self.Explanation = Data.get("公共解析库", [])
                print(f"[题库管理] 已加载 {len(self.AllQuestions)} 道题")
        except Exception as Err:
            print(f"[题库管理] 加载失败：{Err}")

    def GetExplanationById(self, QuestionID) -> list:
        Question = self.GetQuestionById(QuestionID)
        if Question:
            return Question.Explanation + self.Explanation
        return self.Explanation

    def GetQuestionById(self, QuestionID, RandomOption=True, OptionLabels=None) -> Optional[_QuestionItem]:
        for Item in self.AllQuestions:
            if Item.get("题目ID") == QuestionID:
                return _QuestionItem(
                    Item,
                    self.ProjectRoot,
                    RandomOption,
                    OptionLabels or self.Config.GetList("选项编号", ["A", "B", "C", "D"])
                )
        return None

    def GetRandomQuestion(self, ExcludeIDs: list[str] = None, RandomOption=True, OptionLabels=None) -> Optional[_QuestionItem]:
        Pool = [Q for Q in self.AllQuestions if Q.get("题目ID") not in (ExcludeIDs or [])]
        if not Pool:
            return None
        if self.Config.GetBool("每次抽题打乱顺序", True):
            random.shuffle(Pool)
        return _QuestionItem(
            Pool[0],
            self.ProjectRoot,
            RandomOption,
            OptionLabels or self.Config.GetList("选项编号", ["A", "B", "C", "D"])
        )

    def CheckAnswer(self, Question: _QuestionItem, Answer: str) -> tuple[bool, list[str]]:
        if Question is None:
            return False, ["[TEXT] 当前没有题目"]

        StrList = []
        MaxChar = len(Question.Options) if Question.Type == "多选" else 1

        if len(Answer) > MaxChar:
            StrList.append(f"[TEXT] 字符数超过限制，最多支持{MaxChar}个字符")
            return False, StrList

        for Char in Answer:
            if Char not in Question.OptionLabels:
                StrList.append(f"[TEXT] 字符 '{Char}' 不属于选项 {Question.OptionLabels}")
                return False, StrList

        Success = True
        for Char in Answer:
            CharIndex = Question.OptionLabels.index(Char)
            Explanation = Question.Options[CharIndex].get("解析", "")
            if Char in Question.CorrectAnswers:
                StrList.append(f"[TEXT] 选项 {Char}: 正确！")
                if self.Config.GetBool("正确解析", False):
                    StrList.append(f"[TEXT] 解析: {Explanation}")
            else:
                Success = False
                StrList.append(f"[TEXT] 选项 {Char}: 错误！")
                if self.Config.GetBool("错误解析", True):
                    StrList.append(f"[TEXT] 解析: {Explanation}")

        return Success, StrList


# ✅ 全局单例实例
QuestionManager = _QuestionManager()

