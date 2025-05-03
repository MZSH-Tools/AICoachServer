# ==========================================
# 📂 PathManager - 项目路径管理器（单例）
# ------------------------------------------
# 统一管理常用目录和文件路径
# 例如：Data目录、题库文件、图片目录等
# ==========================================

import os

class _PathManager:
    def __init__(self):
        CurrentDir = os.path.dirname(os.path.abspath(__file__))
        self._ProjectRoot = os.path.abspath(os.path.join(CurrentDir, "../.."))

    # ====== 基础目录 ======
    def GetProjectRoot(self) -> str:
        return self._ProjectRoot

    def GetSourceDir(self):
        return os.path.join(self._ProjectRoot, "Source")

    def GetConfigDir(self):
        return os.path.join(self._ProjectRoot, "Config")

    def GetDataDir(self) -> str:
        return os.path.join(self._ProjectRoot, "Data")

    def GetAssetsDir(self) -> str:
        return os.path.join(self._ProjectRoot, "Assets")

    # ====== 具体资源路径 ======
    def GetQuestionBankPath(self) -> str:
        return os.path.join(self.GetDataDir(), "QuestionBank.json")

    def GetConfigPath(self) -> str:
        return os.path.join(self.GetConfigDir(), "Settings.yaml")

    def GetImagesDir(self) -> str:
        return os.path.join(self.GetAssetsDir(), "Images")

    def GetAudioDir(self) -> str:
        return os.path.join(self.GetAssetsDir(), "Audio")

PathManager = _PathManager()
