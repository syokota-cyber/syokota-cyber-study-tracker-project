# StudyTracker 技術仕様書

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | 技術仕様書 |
| 版数 | v2.0 |
| 作成日 | 2025年7月22日 |
| 更新日 | 2025年8月5日 |
| 作成者 | 学習者 |
| 承認者 | - |

---

## 🏗️ システムアーキテクチャ

### 全体構成
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │     バックエンド   │    │     データベース   │
│                 │    │                 │    │                 │
│  Vue.js/React   │◄──►│    FastAPI      │◄──►│    SQLite       │
│  + Tailwind CSS │    │   + SQLAlchemy  │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │   CI/CD Pipeline│    │   Backup System │
│                 │    │                 │    │                 │
│   Python CLI    │    │ GitHub Actions  │    │   Auto Backup   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### レイヤー構成
1. **プレゼンテーション層**: Web UI、CLI
2. **アプリケーション層**: FastAPI、ビジネスロジック
3. **データアクセス層**: SQLAlchemy、データベース
4. **インフラ層**: Docker、CI/CD、監視

---

## 🛠️ 技術スタック詳細

### バックエンド技術

#### 言語・フレームワーク
- **言語**: Python 3.11+
- **Webフレームワーク**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **データベース**: SQLite 3.x（初期）→ PostgreSQL 15+（将来）

#### 主要ライブラリ
```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pytest==7.4.3
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
```

#### 開発ツール
- **コードフォーマッター**: Black
- **リンター**: Flake8
- **テストフレームワーク**: pytest
- **型チェック**: mypy（将来）

### フロントエンド技術

#### フレームワーク・ライブラリ
- **フレームワーク**: Vue.js 3.x / React 18.x
- **UIライブラリ**: Tailwind CSS 3.x
- **グラフライブラリ**: Chart.js 4.x
- **ビルドツール**: Vite 5.x

#### 主要パッケージ
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "tailwindcss": "^3.3.0",
    "chart.js": "^4.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^4.5.0"
  }
}
```

### インフラ・運用技術

#### コンテナ・オーケストレーション
- **コンテナ**: Docker 24.x
- **オーケストレーション**: Docker Compose（開発）
- **本番環境**: Kubernetes（将来）

#### CI/CD・デプロイ
- **CI/CD**: GitHub Actions
- **ホスティング**: GitHub Pages / Vercel（フロントエンド）
- **APIホスティング**: Railway / Render（バックエンド）

#### 監視・ログ
- **監視**: Prometheus + Grafana（将来）
- **ログ**: 構造化ログ（JSON形式）
- **エラー追跡**: Sentry（将来）

---

## 📊 データベース設計

### ER図
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   study_records │    │  study_goals    │    │   categories    │
│                 │    │                 │    │                 │
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ title           │    │ title           │    │ name            │
│ content         │    │ description     │    │ description     │
│ study_time      │    │ target_date     │    │ color           │
│ category_id (FK)│◄──►│ progress        │    │ created_at      │
│ difficulty      │    │ status          │    │ updated_at      │
│ created_at      │    │ created_at      │    └─────────────────┘
│ updated_at      │    │ updated_at      │
└─────────────────┘    └─────────────────┘
```

### テーブル定義

#### study_records（学習記録）
```sql
CREATE TABLE study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    study_time INTEGER NOT NULL DEFAULT 0,
    category_id INTEGER,
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### study_goals（学習目標）
```sql
CREATE TABLE study_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE,
    progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### categories（カテゴリ）
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### インデックス設計
```sql
-- 学習記録の検索用インデックス
CREATE INDEX idx_study_records_category ON study_records(category_id);
CREATE INDEX idx_study_records_created_at ON study_records(created_at);
CREATE INDEX idx_study_records_difficulty ON study_records(difficulty);

-- 学習目標の検索用インデックス
CREATE INDEX idx_study_goals_status ON study_goals(status);
CREATE INDEX idx_study_goals_target_date ON study_goals(target_date);

-- カテゴリの検索用インデックス
CREATE INDEX idx_categories_name ON categories(name);
```

---

## 🔌 API設計

### RESTful API設計原則
- **リソース指向**: 学習記録、目標、カテゴリをリソースとして扱う
- **HTTPメソッド**: GET、POST、PUT、DELETEの適切な使用
- **ステータスコード**: 適切なHTTPステータスコードの使用
- **エラーハンドリング**: 統一されたエラーレスポンス形式

### APIエンドポイント

#### 学習記録API
```
GET    /api/study-records          # 学習記録一覧取得
POST   /api/study-records          # 学習記録作成
GET    /api/study-records/{id}     # 学習記録詳細取得
PUT    /api/study-records/{id}     # 学習記録更新
DELETE /api/study-records/{id}     # 学習記録削除
GET    /api/study-records/search   # 学習記録検索
```

#### 学習目標API
```
GET    /api/study-goals            # 学習目標一覧取得
POST   /api/study-goals            # 学習目標作成
GET    /api/study-goals/{id}       # 学習目標詳細取得
PUT    /api/study-goals/{id}       # 学習目標更新
DELETE /api/study-goals/{id}       # 学習目標削除
```

#### カテゴリAPI
```
GET    /api/categories             # カテゴリ一覧取得
POST   /api/categories             # カテゴリ作成
GET    /api/categories/{id}        # カテゴリ詳細取得
PUT    /api/categories/{id}        # カテゴリ更新
DELETE /api/categories/{id}        # カテゴリ削除
```

#### 統計API
```
GET    /api/statistics/overview    # 統計概要
GET    /api/statistics/time-series # 時間系列データ
GET    /api/statistics/categories  # カテゴリ別統計
```

### データモデル（Pydantic）

#### StudyRecord
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StudyRecordBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    study_time: int = Field(..., ge=0)
    category_id: Optional[int] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)

class StudyRecordCreate(StudyRecordBase):
    pass

class StudyRecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    study_time: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)

class StudyRecord(StudyRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### エラーレスポンス形式
```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

---

## 🎨 フロントエンド設計

### コンポーネント構成

#### ページコンポーネント
```
src/
├── pages/
│   ├── Dashboard.vue          # ダッシュボード
│   ├── StudyRecords.vue       # 学習記録一覧
│   ├── StudyRecordDetail.vue  # 学習記録詳細
│   ├── StudyGoals.vue         # 学習目標
│   ├── Statistics.vue         # 統計・分析
│   └── Settings.vue           # 設定
```

#### 共通コンポーネント
```
src/
├── components/
│   ├── common/
│   │   ├── Header.vue         # ヘッダー
│   │   ├── Sidebar.vue        # サイドバー
│   │   ├── Footer.vue         # フッター
│   │   └── Loading.vue        # ローディング
│   ├── forms/
│   │   ├── StudyRecordForm.vue # 学習記録フォーム
│   │   └── StudyGoalForm.vue   # 学習目標フォーム
│   └── charts/
│       ├── TimeSeriesChart.vue # 時間系列グラフ
│       └── CategoryChart.vue   # カテゴリ別グラフ
```

### 状態管理
```javascript
// Pinia（Vue.js）またはRedux（React）
const useStudyStore = defineStore('study', {
  state: () => ({
    studyRecords: [],
    studyGoals: [],
    categories: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchStudyRecords() { /* ... */ },
    async createStudyRecord(record) { /* ... */ },
    async updateStudyRecord(id, record) { /* ... */ },
    async deleteStudyRecord(id) { /* ... */ }
  }
});
```

### ルーティング
```javascript
// Vue Router
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/study-records',
    name: 'StudyRecords',
    component: StudyRecords
  },
  {
    path: '/study-records/:id',
    name: 'StudyRecordDetail',
    component: StudyRecordDetail
  },
  {
    path: '/study-goals',
    name: 'StudyGoals',
    component: StudyGoals
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
];
```

---

## 🧪 テスト戦略

### テストピラミッド
```
        E2E Tests (少数)
           ▲
    Integration Tests (中程度)
           ▲
    Unit Tests (多数)
```

### テスト種別

#### ユニットテスト
- **対象**: 個別の関数・クラス・コンポーネント
- **ツール**: pytest（バックエンド）、Vitest（フロントエンド）
- **カバレッジ目標**: 80%以上

#### 統合テスト
- **対象**: APIエンドポイント、データベース操作
- **ツール**: pytest + FastAPI TestClient
- **カバレッジ目標**: 主要機能の100%

#### E2Eテスト
- **対象**: ユーザー操作フロー
- **ツール**: Playwright / Cypress
- **カバレッジ目標**: 重要なユーザーフロー

### テストデータ管理
```python
# フィクスチャ
@pytest.fixture
def sample_study_record():
    return {
        "title": "Python基礎学習",
        "content": "変数、関数、クラスの学習",
        "study_time": 60,
        "category_id": 1,
        "difficulty": 3
    }

@pytest.fixture
def sample_category():
    return {
        "name": "Python",
        "description": "Pythonプログラミング",
        "color": "#3776AB"
    }
```

---

## 🔒 セキュリティ設計

### 認証・認可
- **認証方式**: JWT（将来）
- **認可**: ロールベースアクセス制御（将来）
- **セッション管理**: セキュアなセッション管理

### データ保護
- **暗号化**: 機密データの暗号化
- **バックアップ**: 定期的なバックアップ
- **データ削除**: 適切なデータ削除処理

### 入力検証
- **バリデーション**: Pydanticによる入力検証
- **サニタイゼーション**: XSS対策
- **SQLインジェクション対策**: ORMの使用

---

## 📈 パフォーマンス設計

### データベース最適化
- **インデックス**: 適切なインデックス設計
- **クエリ最適化**: 効率的なクエリ設計
- **接続プール**: データベース接続の効率化

### キャッシュ戦略
- **アプリケーションキャッシュ**: Redis（将来）
- **ブラウザキャッシュ**: 適切なキャッシュヘッダー
- **CDN**: 静的ファイルの配信最適化

### フロントエンド最適化
- **コード分割**: 遅延読み込み
- **バンドル最適化**: Tree shaking
- **画像最適化**: WebP形式の使用

---

## 🔄 CI/CD設計

### GitHub Actionsワークフロー

#### CI（継続的インテグレーション）
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=src
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

#### CD（継続的デプロイ）
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: echo "Deploy to production"
```

### 環境管理
- **開発環境**: ローカル開発環境
- **ステージング環境**: テスト用環境（将来）
- **本番環境**: クラウド環境（将来）

---

## 📊 監視・ログ設計

### ログ設計
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event_type, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))
```

### メトリクス設計
- **アプリケーションメトリクス**: レスポンス時間、エラー率
- **ビジネスメトリクス**: 学習記録数、ユーザーアクティビティ
- **インフラメトリクス**: CPU使用率、メモリ使用率

---

## 📋 デプロイメント設計

### Docker設計
```dockerfile
# バックエンド
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# フロントエンド
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./study_tracker.db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

---

## 🔒 セキュリティ技術仕様（Phase 1完了）

### セキュリティアーキテクチャ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │   セキュリティ層   │    │     バックエンド   │
│                 │    │                 │    │                 │
│  Vue.js/React   │◄──►│   CORS制限      │◄──►│    FastAPI      │
│  + Tailwind CSS │    │   セキュリティヘッダー │    │   + 入力値検証   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XSS対策       │    │   エラーハンドリング │    │   データベース   │
│   HTMLエスケープ │    │   情報漏洩防止   │    │   DynamoDB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### セキュリティ実装詳細

#### 1. 入力値検証・サニタイズ
```python
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """入力値のサニタイズ（XSS対策）"""
    if not isinstance(text, str):
        return ""
    
    # 長さ制限
    if len(text) > max_length:
        text = text[:max_length]
    
    # HTMLエスケープ
    text = html.escape(text)
    
    # 危険な文字列の除去
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe.*?</iframe>',
        r'<object.*?</object>',
        r'<embed.*?</embed>'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()
```

#### 2. セキュリティヘッダー設定
```python
def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """セキュリティ強化レスポンス作成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'https://learninggarden.studio',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        },
        'body': json.dumps(body, default=str)
    }
```

#### 3. エラーハンドリング
```python
def handler(event, context):
    try:
        # メイン処理
        pass
    except Exception as e:
        # エラーメッセージの情報漏洩を防ぐ
        return create_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })
```

### セキュリティテスト仕様

#### テストカバレッジ
- **XSS攻撃テスト**: 14種類の危険な入力パターン
- **入力値検証テスト**: 全フィールドの境界値テスト
- **エラーハンドリングテスト**: 情報漏洩防止テスト
- **セキュリティヘッダーテスト**: 全ヘッダーの存在確認

#### テスト実行
```bash
# セキュリティテスト実行
python -m pytest tests/test_security.py -v

# テスト結果
# 14 passed in 0.24s
```

### セキュリティ監視・ログ

#### セキュリティログ
```python
def log_security_event(event_type: str, details: Dict[str, Any]):
    """セキュリティイベントのログ記録"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "security",
        "security_event": event_type,
        "details": details,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
    logger.warning(json.dumps(log_entry))
```

#### 監視項目
- **不正アクセス試行**: 認証失敗、権限エラー
- **XSS攻撃試行**: 危険な入力パターンの検出
- **大量リクエスト**: DoS攻撃の検出
- **異常なアクセスパターン**: 不正なAPI呼び出し

### 次のセキュリティ実装予定

#### Phase 2: 認証・認可 ✅ **実装完了**
```python
# JWT認証実装完了
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # JWTトークンの検証
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": payload.get("sub")}
```

#### Phase 3: 高度セキュリティ（3ヶ月後）
- **WAF**: AWS WAFによるWebアプリケーションファイアウォール
- **GuardDuty**: 脅威検出・監視
- **CloudTrail**: API呼び出しの監査ログ

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年7月22日 | - |
| 技術責任者 | AIアシスタント | 2025年7月22日 | - |
| セキュリティ責任者 | AIアシスタント | 2025年8月5日 | - |

---

**文書バージョン**: v2.0  
**最終更新日**: 2025年8月7日 