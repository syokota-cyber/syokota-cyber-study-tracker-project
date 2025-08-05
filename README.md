# StudyTracker Project

## 📚 プロジェクト概要

**StudyTracker**は、個人の学習進捗・目標管理・知識蓄積を統合的に管理するWebアプリケーションです。

### 🎯 プロジェクトの目的
- 個人開発者のGit/GitHub学習を中心とした実践的な開発経験の獲得
- 段階的な機能追加を通じた技術スキルの向上
- ポートフォリオとして活用できる実用的なアプリケーションの構築

---

## 🚀 クイックスタート

### 開発環境のセットアップ
```bash
# リポジトリをクローン
git clone https://github.com/syokota-cyber/syokota-cyber-study-tracker-project.git
cd study-tracker-project

# 仮想環境を作成・アクティベート
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### FastAPIサーバーの起動
```bash
# 開発サーバーを起動
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### アクセス方法
- **APIドキュメント**: http://localhost:8000/docs
- **APIエンドポイント**: http://localhost:8000/api/v1/
- **ヘルスチェック**: http://localhost:8000/health

### CLIツールの使用
```bash
# 学習記録を追加
python -m src.cli.main add "FastAPI学習" --content "Swagger UIの使い方" --time 60 --category "バックエンド" --difficulty 2

# 学習記録一覧を表示
python -m src.cli.main list

# 統計情報を表示
python -m src.cli.main stats --category

# データをエクスポート
python -m src.cli.main export csv --all-fields
```

---

## 📁 プロジェクト構造

```
study-tracker-project/
├── README.md                    # プロジェクト概要（このファイル）
├── requirements/                # 要件定義・仕様書
│   ├── requirements.md         # 要件定義書
│   ├── specification.md        # 技術仕様書
│   └── api-specification.md    # API仕様書
├── docs/                       # ドキュメント
│   ├── setup.md               # セットアップガイド
│   ├── development.md         # 開発ガイド
│   └── deployment.md          # デプロイガイド
├── rules/                      # ルール・ガイドライン
│   ├── git-workflow.md        # Gitワークフロー
│   ├── coding-standards.md    # コーディング規約
│   └── review-guidelines.md   # レビューガイドライン
├── plans/                      # 学習計画・スケジュール
│   ├── phase1-plan.md         # Phase 1詳細計画
│   ├── learning-schedule.md   # 学習スケジュール
│   └── milestones.md          # マイルストーン
├── src/                        # ソースコード
│   ├── models/                # データモデル
│   ├── database/              # データベース関連
│   ├── cli/                   # CLIインターフェース
│   └── api/                   # FastAPI関連
│       ├── main.py            # FastAPIアプリケーション
│       └── routes.py          # APIルート定義
├── tests/                      # テストファイル
└── logs/                       # 学習ログ・進捗記録
    ├── daily-logs/            # 日次学習ログ
    ├── weekly-reviews/        # 週次振り返り
    └── progress-tracker.md    # 進捗追跡
```

---

## 🚀 開発フェーズ

### Phase 1: 基礎構築（2週間）
- **期間**: 2025年7月24日〜8月6日（準備日: 今日、開始日: 明日）
- **目標**: 基本機能の実装とGit Flow習得
- **成果物**: CLI、Web API、基本UI、CI/CD

### Phase 2: 機能拡張（3-4ヶ月）
- **目標**: 高度な機能とAPI開発
- **成果物**: 検索・フィルタリング、統計・可視化

### Phase 3: 高度化（2-3ヶ月）
- **目標**: データベース移行とAI機能
- **成果物**: PostgreSQL、自動化・通知、AI機能

### Phase 4: 運用・改善（継続）
- **目標**: クラウドデプロイとモバイル対応
- **成果物**: クラウド展開、モバイルアプリ

---

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **データベース**: SQLite → PostgreSQL
- **ORM**: SQLAlchemy
- **テスト**: pytest
- **API開発**: FastAPI + Swagger UI

### フロントエンド
- **言語**: JavaScript/TypeScript
- **フレームワーク**: Vue.js 3 / React 18
- **UIライブラリ**: Tailwind CSS
- **グラフ**: Chart.js
- **ビルドツール**: Vite

### インフラ・運用
- **コンテナ**: Docker
- **CI/CD**: GitHub Actions
- **クラウド**: AWS/GCP
- **監視**: Prometheus + Grafana

---

## 📋 主要機能

### 基本機能
- ✅ 学習記録のCRUD操作
- ✅ 学習目標の設定・管理
- ✅ カテゴリ別分類
- ✅ 学習時間の記録

### 高度な機能
- ✅ 検索・フィルタリング
- ✅ 統計・可視化
- 🔄 リマインダー・通知
- ✅ データエクスポート

---

## 🔧 FastAPI + Swagger活用方法

### API開発フロー
1. **FastAPIでエンドポイントを定義**
   ```python
   @app.post("/api/v1/study-records/")
   async def create_study_record(record: StudyRecordCreate):
       """学習記録を作成"""
       return created_record
   ```

2. **Swagger UIで自動ドキュメント生成**
   - http://localhost:8000/docs でAPI仕様書を確認
   - インタラクティブなテスト環境を活用
   - チーム内でAPI仕様を共有

3. **フロントエンド開発との連携**
   - Swagger UIをフロントエンド開発者と共有
   - API仕様書として活用
   - リアルタイムでAPIテストを実行

### 開発環境での運用
```bash
# 開発サーバー起動
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# アクセスURL
# APIドキュメント: http://localhost:8000/docs
# APIエンドポイント: http://localhost:8000/api/v1/
# ヘルスチェック: http://localhost:8000/health
```

### 本番環境での運用
```bash
# 本番サーバー起動
uvicorn src.api.main:app --host 0.0.0.0 --port 80

# Docker化
docker build -t study-tracker-api .
docker run -p 80:80 study-tracker-api
```

### APIエンドポイント
- **GET /api/v1/study-records** - 学習記録一覧取得
- **POST /api/v1/study-records** - 学習記録作成
- **GET /api/v1/study-records/{id}** - 学習記録詳細取得
- **PUT /api/v1/study-records/{id}** - 学習記録更新
- **DELETE /api/v1/study-records/{id}** - 学習記録削除
- **GET /api/v1/study-records/stats/summary** - 統計情報取得

---

## 🧪 テスト

### テストの実行
```bash
# 全テストを実行
python -m pytest

# CLIテストのみ実行
python -m pytest tests/test_cli.py

# カバレッジ付きでテスト
python -m pytest --cov=src --cov-report=html
```

### テストカバレッジ
- **目標**: 80%以上
- **現在**: 52%（CLI機能）
- **次回目標**: FastAPI機能のテスト追加

---

## 📊 現在の進捗

### Phase 1 Day 3 完了（2025年7月26日）
- ✅ **CLI機能**: 完全実装（7コマンド、14テスト）
- ✅ **検索・フィルタリング**: 6種類のフィルタリング機能
- ✅ **データエクスポート**: CSV、JSON、TXT形式対応
- ✅ **FastAPI**: 基本実装完了
- ✅ **Swagger UI**: APIドキュメント自動生成
- ✅ **テスト**: 14個のテストケース（すべて成功）

### 次のステップ
- **Day 4**: FastAPI基本機能の拡張
- **Day 5**: APIエンドポイントの実装
- **Day 6**: APIテストの実装

---

## 🤝 開発者向け情報

### 開発ルール
1. **Git Flowワークフロー**: feature/bugfix/hotfix/releaseブランチを使用
2. **コミットメッセージ**: Conventional Commits形式（feat:, fix:, docs:, etc.）
3. **テスト駆動開発**: 新機能実装前にテストを作成
4. **コード品質**: Black（フォーマット）、Flake8（リンター）を使用
5. **ドキュメント**: 重要な変更はドキュメントを更新
6. **API開発**: FastAPI + Swagger UIで自動ドキュメント生成

### 品質基準
- テストカバレッジ: 80%以上
- コードフォーマット: Black準拠
- リンター: Flake8合格
- ドキュメント: 適切な更新
- コミット: 意味のあるメッセージ
- API仕様: Swagger UIで自動生成・最新維持

---

## 📝 ライセンス

このプロジェクトは学習目的で作成されています。

---

## 📞 サポート

質問や問題がある場合は、GitHubのIssuesで報告してください。

---

## 📚 ドキュメント

### 基本ドキュメント
- [セットアップガイド](docs/setup.md)
- [プロジェクト仕様書](requirements/specification.md)
- [要件定義書](requirements/requirements.md)

### AWS移行関連ドキュメント
- [AWS移行要件定義書](requirements/migration-requirements.md)
- [AWS移行技術仕様書](requirements/migration-specification.md)
- [AWS移行手順書](docs/migration-procedure.md)
- [AWS移行計画・運用コスト分析](docs/aws-migration-plan.md)
- [AWS資産管理・コスト監視インベントリ](docs/aws-assets-inventory.md)
- [AWS Lambda デプロイメントガイド](docs/aws-deployment.md)

## 🔗 リポジトリ情報

- **GitHubリポジトリ**: https://github.com/syokota-cyber/syokota-cyber-study-tracker-project
- **学習ログ**: [logs/daily-logs/](logs/daily-logs/)
- **進捗追跡**: [logs/progress-tracker.md](logs/progress-tracker.md)
- **APIドキュメント**: http://localhost:8000/docs（開発サーバー起動時） 