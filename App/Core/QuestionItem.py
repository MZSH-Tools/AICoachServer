import os
import random

class QuestionItem:
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
