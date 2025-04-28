from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from App.Routers import QueryAIWebSocket
import os

# 创建 FastAPI 应用
App = FastAPI()

# 启用 CORS（允许跨域请求，便于本地前端访问）
App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 若有安全需求可改为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态资源目录，用于题图访问
AssetsPath = os.path.join(os.getcwd(), "Assets/Images")
if not os.path.exists(AssetsPath):
    os.makedirs(AssetsPath)
App.mount("/assets", StaticFiles(directory=AssetsPath), name="assets")


# 注册路由模块
App.include_router(QueryAIWebSocket.Router)
