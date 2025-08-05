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
    description="""
    ## 学習進捗管理システムのWeb API
    
    ### 機能
    - �� **学習記録の管理**: 作成・読み取り・更新・削除
    - �� **統計情報**: カテゴリ別・難易度別・時系列分析
    - �� **検索・フィルタ**: 柔軟な検索機能
    - 📄 **ページネーション**: 大量データの効率的な表示
    
    ### 認証
    現在は認証なしで動作しています。
    
    ### 使用方法
    1. 各エンドポイントをクリックして詳細を確認
    2. "Try it out"ボタンで実際にAPIをテスト
    3. レスポンス例を参考にフロントエンド開発
    
    ### 開発者向け情報
    - **Base URL**: `http://localhost:8000/api/v1`
    - **Swagger UI**: `/docs`
    - **ReDoc**: `/redoc`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "学習記録",
            "description": "学習記録の作成・読み取り・更新・削除",
        },
        {
            "name": "統計情報",
            "description": "学習データの分析・統計情報",
        },
        {
            "name": "システム",
            "description": "システム情報・ヘルスチェック",
        },
    ],
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


@app.get("/", tags=["システム"])
async def root():
    """ルートエンドポイント"""
    return {
        "message": "StudyTracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1",
        "health": "/health",
    }


@app.get("/health", tags=["システム"])
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "service": "StudyTracker API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)