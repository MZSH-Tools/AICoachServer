# ==========================================
# 📘 ConfigManager - 全局配置与路径管理器（单例）
# ------------------------------------------
# 统一管理配置加载、数据目录、资源目录（图片、音频等）
# ==========================================

import os
import yaml
from App.Managers.PathManager import PathManager

class _ConfigManager:
    def __init__(self):
        self._ConfigPath = PathManager.GetConfigPath()
        self.ConfigData = {}
        self.Load()

    def Load(self):
        if not os.path.exists(self._ConfigPath):
            print(f"[ConfigManager] 配置文件不存在：{self._ConfigPath}")
            return
        try:
            with open(self._ConfigPath, "r", encoding="utf-8") as File:
                self.ConfigData = yaml.safe_load(File)
                print(f"[ConfigManager] 配置已加载：{self._ConfigPath}")
        except Exception as Err:
            print(f"[ConfigManager] 加载失败：{Err}")

    # ====== 配置项读取接口 ======
    def GetString(self, Key: str, Default: str = "") -> str:
        return str(self.ConfigData.get(Key, Default))

    def GetBool(self, Key: str, Default: bool = False) -> bool:
        return bool(self.ConfigData.get(Key, Default))

    def GetList(self, Key: str, Default: list = None) -> list:
        return self.ConfigData.get(Key, Default or [])

# ✅ 单例实例导出
ConfigManager = _ConfigManager()
