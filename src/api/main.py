"""
FastAPIメインアプリケーション

Web APIサーバーのエントリーポイントです。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

# FastAPIアプリケーションの作成
app = FastAPI(
    title="StudyTracker API",
    description="学習進捗管理システムのWeb API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "StudyTracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
