# ==========================================
# 📘 ConfigManager - YAML配置管理器（单例）
# ------------------------------------------
# 用于加载与访问全局配置项，如模型地址池、题库路径、选项设置等。
# 支持字符串、布尔、列表格式读取。
# 加载自 Config/Settings.yaml，仅加载一次，全局复用。
# ==========================================

import os
import yaml


class _ConfigManager:
    def __init__(self):
        self.ConfigData = {}
        self.BasePath = os.path.abspath(os.path.join(os.getcwd(), "App"))
        self.ConfigPath = os.path.join(self.BasePath, "../Config/Settings.yaml")
        self.Load()

    def Load(self):
        if not os.path.exists(self.ConfigPath):
            print(f"[ConfigManager] 配置文件不存在：{self.ConfigPath}")
            return

        try:
            with open(self.ConfigPath, "r", encoding="utf-8") as File:
                self.ConfigData = yaml.safe_load(File)
                print(f"[ConfigManager] 配置已加载：{self.ConfigPath}")
        except Exception as Err:
            print(f"[ConfigManager] 加载失败：{Err}")

    def GetString(self, Key: str, Default: str = "") -> str:
        return str(self.ConfigData.get(Key, Default))

    def GetBool(self, Key: str, Default: bool = False) -> bool:
        return bool(self.ConfigData.get(Key, Default))

    def GetList(self, Key: str, Default: list = None) -> list:
        return self.ConfigData.get(Key, Default or [])

    def GetPath(self, RelativePath: str) -> str:
        return os.path.abspath(os.path.join(self.BasePath, "..", RelativePath))


# ✅ 全局单例导出
ConfigManager = _ConfigManager()
