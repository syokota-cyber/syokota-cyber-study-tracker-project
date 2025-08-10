# StudyTracker Phase 2: 認証・セキュリティ強化 - 詳細計画

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | Phase 2詳細計画 |
| 版数 | v1.0 |
| 作成日 | 2025年8月7日 |
| 作成者 | 学習者 |
| 承認者 | - |

---

## 🎯 Phase 2 概要

### 期間
**2025年8月7日〜2025年8月14日**（8日間）
**開始日**: 2025年8月7日（今日）
**完了予定日**: 2025年8月14日

### 学習時間
**毎日90-120分**（合計約12時間）

### 目標
- JWT認証システムの完全実装
- ユーザー管理機能の実装
- フロントエンド認証UIの実装
- ローカル環境での完全動作確認

### 成果物
- JWT認証システム
- ユーザー管理API
- フロントエンド認証UI
- 統合テストスイート
- ローカル開発環境

---

## 📅 詳細スケジュール

### Day 1 (8/7): JWT認証基盤構築 ✅ **完了**

#### 成果物
- ✅ JWT認証ライブラリの追加
- ✅ 認証ディレクトリ構造の作成
- ✅ JWTハンドラーの実装
- ✅ 認証依存関係の実装
- ✅ ユーザーモデルの作成
- ✅ 包括的なテストの実装

#### 技術的成果
- **JWT認証**: トークン生成・検証機能
- **パスワードセキュリティ**: bcryptハッシュ化
- **FastAPI統合**: OAuth2PasswordBearer
- **テスト品質**: 9個のテストケース、100%成功

---

### Day 2 (8/8): ローカルDynamoDB環境構築

#### 目標
- Docker環境でのローカルDynamoDB設定
- ユーザーテーブルの設計・作成
- 基本的なCRUD操作の実装

#### 詳細作業
**90分: Docker環境の準備**
```bash
# Docker Desktopの起動確認
docker --version
docker ps

# ローカルDynamoDBコンテナの起動
docker run -p 8000:8000 amazon/dynamodb-local

# 接続テスト
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

**90分: ユーザーテーブルの作成**
```bash
# ユーザーテーブルの作成
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
    AttributeName=email,AttributeType=S \
  --key-schema \
    AttributeName=id,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=email-index,KeySchema=[{AttributeName=email,KeyType=HASH}],Projection={ProjectionType=ALL} \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --endpoint-url http://localhost:8000
```

#### 成果物
- ローカルDynamoDB環境
- ユーザーテーブル設計
- 基本的なCRUD操作

---

### Day 3 (8/9): ユーザー管理API実装

#### 目標
- ユーザー登録・ログインAPIの実装
- JWT認証との統合
- エラーハンドリングの実装

#### 詳細作業
**60分: ユーザーサービス層の実装**
```python
# src/services/user_service.py
class UserService:
    def create_user(self, user_data: UserCreate) -> User
    def get_user_by_email(self, email: str) -> Optional[User]
    def get_user_by_id(self, user_id: str) -> Optional[User]
    def update_user(self, user_id: str, user_data: UserUpdate) -> User
    def authenticate_user(self, email: str, password: str) -> Optional[User]
```

**60分: 認証APIエンドポイントの実装**
```python
# src/api/auth_routes.py
@router.post("/register")
async def register(user: UserCreate)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends())

@router.get("/users/me")
async def get_current_user_info(current_user = Depends(get_current_user))
```

#### 成果物
- ユーザーサービス層
- 認証APIエンドポイント
- 統合テスト

---

### Day 4 (8/10): 認証フローの統合

#### 目標
- 既存APIと認証の統合
- 認証が必要なエンドポイントの保護
- エラーハンドリングの強化

#### 詳細作業
**60分: 既存APIの認証統合**
```python
# 学習記録APIに認証を追加
@router.post("/study-records/")
async def create_study_record(
    record: StudyRecordCreate,
    current_user = Depends(get_current_user)
)

@router.get("/study-records/")
async def get_study_records(
    current_user = Depends(get_current_user)
)
```

**60分: エラーハンドリングの強化**
```python
# 認証エラーの統一
class AuthException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )
```

#### 成果物
- 認証統合されたAPI
- 強化されたエラーハンドリング
- セキュリティテスト

---

### Day 5 (8/11): フロントエンド認証UI実装

#### 目標
- ログイン・登録画面の実装
- 認証状態管理の実装
- ルートガードの実装

#### 詳細作業
**60分: 認証ストアの実装**
```typescript
// src/stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isAuthenticated = ref(false)

  const login = async (email: string, password: string)
  const register = async (userData: any)
  const logout = () => void
})
```

**60分: 認証コンポーネントの実装**
```vue
<!-- src/components/LoginForm.vue -->
<template>
  <form @submit.prevent="handleLogin">
    <input v-model="email" type="email" required>
    <input v-model="password" type="password" required>
    <button type="submit">ログイン</button>
  </form>
</template>
```

#### 成果物
- 認証ストア
- ログイン・登録コンポーネント
- ルートガード

---

### Day 6 (8/12): フロントエンド統合

#### 目標
- 認証UIとAPIの統合
- 認証状態の永続化
- ユーザー体験の最適化

#### 詳細作業
**60分: API統合**
```typescript
// src/services/auth.ts
export const authService = {
  async login(email: string, password: string): Promise<Token>
  async register(userData: UserCreate): Promise<UserResponse>
  async getCurrentUser(): Promise<UserResponse>
}
```

**60分: 認証状態の永続化**
```typescript
// ローカルストレージでのトークン保存
const saveToken = (token: string) => {
  localStorage.setItem('auth_token', token)
}

const getToken = (): string | null => {
  return localStorage.getItem('auth_token')
}
```

#### 成果物
- API統合された認証UI
- 認証状態の永続化
- ユーザー体験の改善

---

### Day 7 (8/13): 統合テスト・最適化

#### 目標
- エンドツーエンドテストの実装
- パフォーマンス最適化
- セキュリティテスト

#### 詳細作業
**60分: 統合テストの実装**
```python
# tests/test_auth_integration.py
class TestAuthIntegration:
    def test_user_registration_flow(self)
    def test_user_login_flow(self)
    def test_protected_endpoints(self)
    def test_token_expiration(self)
```

**60分: パフォーマンス最適化**
- データベースクエリの最適化
- キャッシュ戦略の実装
- レスポンス時間の改善

#### 成果物
- 統合テストスイート
- パフォーマンス最適化
- セキュリティ監査

---

### Day 8 (8/14): ドキュメント・最終確認

#### 目標
- APIドキュメントの更新
- 運用マニュアルの作成
- 最終動作確認

#### 詳細作業
**60分: ドキュメント更新**
- Swagger UIの更新
- API仕様書の作成
- 運用マニュアルの作成

**60分: 最終動作確認**
- 全機能の動作確認
- エラーケースの確認
- パフォーマンステスト

#### 成果物
- 更新されたAPIドキュメント
- 運用マニュアル
- 最終テストレポート

---

## 🛠️ 技術スタック

### バックエンド
- **JWT認証**: python-jose[cryptography]
- **パスワードハッシュ**: passlib[bcrypt]
- **フォーム処理**: python-multipart
- **データベース**: DynamoDB（ローカル）
- **API**: FastAPI

### フロントエンド
- **状態管理**: Pinia
- **認証**: js-cookie
- **UI**: Vue.js 3 + Tailwind CSS
- **HTTP通信**: Axios

### 開発環境
- **ローカルDB**: Docker + DynamoDB Local
- **テスト**: pytest
- **型チェック**: mypy
- **リンター**: flake8

---

## 🔒 セキュリティ設計

### 認証・認可
- **JWT認証**: 30分有効期限のアクセストークン
- **パスワードセキュリティ**: bcryptハッシュ化
- **トークン管理**: 安全な秘密鍵管理

### データ保護
- **入力検証**: Pydanticによる厳密なバリデーション
- **SQLインジェクション対策**: DynamoDBの使用
- **XSS対策**: 既存のセキュリティヘッダー

### 監査・ログ
- **アクセスログ**: 認証イベントの記録
- **エラーログ**: セキュリティ関連エラーの記録
- **監査証跡**: ユーザー操作の追跡

---

## 📊 成功指標

### 技術指標
- **テストカバレッジ**: 90%以上
- **API応答時間**: 200ms以下
- **エラー率**: 1%以下
- **セキュリティ**: セキュリティテスト100%通過

### 機能指標
- **ユーザー登録**: 正常にユーザーが作成される
- **ユーザーログイン**: 正常にログインできる
- **認証保護**: 認証が必要なエンドポイントが保護される
- **セッション管理**: トークンの有効期限が適切に管理される

### ユーザビリティ指標
- **UI/UX**: 直感的な認証フロー
- **エラーメッセージ**: 分かりやすいエラー表示
- **レスポンシブ**: モバイル対応
- **アクセシビリティ**: アクセシビリティガイドライン準拠

---

## 🚨 リスク管理

### 技術リスク
- **Docker環境**: ローカル環境の構築失敗
- **DynamoDB**: テーブル設計の不備
- **JWT実装**: セキュリティ脆弱性

### 対策
- **事前準備**: Docker環境の事前確認
- **段階的実装**: 小さな単位での実装・テスト
- **セキュリティレビュー**: 定期的なセキュリティチェック

---

## 📈 期待される効果

### 技術的効果
- **セキュリティ向上**: 本格的な認証システム
- **スケーラビリティ**: ユーザー管理機能の実装
- **保守性**: モジュール化された認証システム

### 学習効果
- **JWT認証**: 現代的な認証システムの習得
- **DynamoDB**: NoSQLデータベースの実践
- **セキュリティ**: セキュリティベストプラクティス

### ビジネス効果
- **ユーザー管理**: 個人・チームでの利用が可能
- **セキュリティ**: 本格的なWebアプリケーション
- **拡張性**: 将来の機能拡張が容易

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年8月7日 | - |
| 技術責任者 | AIアシスタント | 2025年8月7日 | - |
| セキュリティ責任者 | AIアシスタント | 2025年8月7日 | - |

---

**文書バージョン**: v1.0  
**最終更新日**: 2025年8月7日

