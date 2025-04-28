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

    def GetAppFolder(self):
        return os.path.join(self._ProjectRoot, "App")

    def GetConfigFolder(self):
        return os.path.join(self._ProjectRoot, "Config")

    def GetDataFolder(self) -> str:
        return os.path.join(self._ProjectRoot, "Data")

    def GetAssetsFolder(self) -> str:
        return os.path.join(self._ProjectRoot, "Assets")

    # ====== 具体资源路径 ======
    def GetQuestionBankPath(self) -> str:
        return os.path.join(self.GetDataFolder(), "QuestionBank.json")

    def GetConfigPath(self) -> str:
        return os.path.join(self.GetConfigFolder(), "Settings.yaml")

    def GetImagesFolder(self) -> str:
        return os.path.join(self.GetAssetsFolder(), "Images")

    def GetAudioFolder(self) -> str:
        return os.path.join(self.GetAssetsFolder(), "Audio")

PathManager = _PathManager()
