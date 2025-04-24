import json
import random
import os
from App.Config.ConfigManager import ConfigManager

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

class QuestionManager:
    _Instance = None

    def __new__(cls):
        if cls._Instance is None:
            cls._Instance = super(QuestionManager, cls).__new__(cls)
            cls._Instance._Initialized = False
        return cls._Instance

    def __init__(self):
        if self._Initialized:
            return
        self._Initialized = True

        self.Config = ConfigManager()
        self.ProjectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        RelativePath = self.Config.GetString("题库路径", "Config/QuestionBank.json")
        self.QuestionPath = os.path.join(self.ProjectRoot, RelativePath)
        self.AllQuestions = []
        self.QuestionPool = []
        self.CurrentQuestion = None
        self.Explanation = []
        self.LoadQuestions()

    def LoadQuestions(self):
        if not os.path.exists(self.QuestionPath):
            print(f"[警告] 题库文件不存在：{self.QuestionPath}")
            return

        with open(self.QuestionPath, "r", encoding="utf-8-sig") as File:
            try:
                Data = json.load(File)
                self.AllQuestions = Data.get("题库", [])
                self.QuestionPool = self.AllQuestions[:]
                self.Explanation = Data.get("公共解析库", [])
            except Exception as Error:
                print(f"[错误] 加载题库失败：{str(Error)}")

    def ShufflePool(self):
        if self.QuestionPool:
            random.shuffle(self.QuestionPool)

    def ResetPool(self):
        self.QuestionPool = self.AllQuestions[:]

    def NextRandomQuestion(self) -> bool:
        if self.Config.GetBool("题库为空时重新加载", True) and not self.QuestionPool:
            self.ResetPool()

        if self.Config.GetBool("每次抽题打乱顺序", True):
            self.ShufflePool()

        if not self.QuestionPool:
            print("[提示] 所有题目已完成，无题可抽。")
            self.CurrentQuestion = None
            return False

        QuestionData = self.QuestionPool.pop(0) if self.Config.GetBool("在题库中移除已抽题目", True) else self.QuestionPool[0]
        self.CurrentQuestion = _QuestionItem(
            QuestionData,
            self.ProjectRoot,
            self.Config.GetBool("打乱选项", True),
            self.Config.GetList("选项编号", ["A", "B", "C", "D", "E", "F"])
        )
        return True

    def GetExplanation(self):
        if self.CurrentQuestion:
            return self.CurrentQuestion.Explanation + self.Explanation
        return self.Explanation

    def CheckAnswer(self, Answer):
        if self.CurrentQuestion is None:
            return False, ["[TEXT] 当前没有题目"]

        StrList = []
        MaxChar = len(self.CurrentQuestion.Options) if self.CurrentQuestion.Type == "多选" else 1

        if len(Answer) > MaxChar:
            StrList.append(f"[TEXT]字符数过多超过题目限制，最多支持{MaxChar}个字符，请重新填写")
            return False, StrList

        for Char in Answer:
            if Char not in self.CurrentQuestion.OptionLabels:
                StrList.append(f"[TEXT]字符'{Char}'不属于选项{self.CurrentQuestion.OptionLabels}, 请重新输入")
                return False, StrList

        Success = True
        for Char in Answer:
            CharIndex = self.CurrentQuestion.OptionLabels.index(Char)
            Explanation = self.CurrentQuestion.Options[CharIndex].get("解析", "")
            if Char in self.CurrentQuestion.CorrectAnswers:
                StrList.append(f"[TEXT]选项{Char}: 正确！")
                if self.Config.GetBool("正确解析", False):
                    StrList.append(f"[TEXT]解析:{Explanation}")
            else:
                Success = False
                StrList.append(f"[TEXT]选项{Char}: 错误！")
                if self.Config.GetBool("错误解析", True):
                    StrList.append(f"[TEXT]解析:{Explanation}")

        return Success, StrList
