# ==========================================
# 🚀 Main.py - AICoach服务器主程序入口
# ------------------------------------------
# - 创建FastAPI应用
# - 挂载静态资源
# - 开启CORS跨域
# - 注册WebSocket路由
# - 支持直接运行启动服务器（uvicorn.run）
# ==========================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from Source.Routers import QueryAIWebSocket
import os

# 创建 FastAPI 应用
App = FastAPI()

# 启用 CORS（允许本地前端访问）
App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 安全需求可改成指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态资源目录（用于题目图片访问）
AssetsPath = os.path.join(os.getcwd(), "Assets/Images")
if not os.path.exists(AssetsPath):
    os.makedirs(AssetsPath)
App.mount("Source/Assets", StaticFiles(directory=AssetsPath), name="assets")

# 注册WebSocket路由
App.include_router(QueryAIWebSocket.Router)

# ==========================================
# ✅ 支持直接运行调试
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "Source.Main:Source",        # 这里是 文件名:FastAPI实例名
        host="127.0.0.1",   # 本地开发用127.0.0.1，正式部署可改成0.0.0.0
        port=8000,
        reload=True        # 自动热重载（开发模式必开）
    )
