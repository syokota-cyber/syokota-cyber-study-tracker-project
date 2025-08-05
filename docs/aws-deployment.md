# AWS Lambda デプロイメントガイド

## 概要

StudyTracker APIをAWS Lambdaにデプロイするための手順を説明します。

## 前提条件

### 1. AWS CLI の設定
```bash
# AWS CLI のインストール
pip install awscli

# AWS認証情報の設定
aws configure
```

### 2. Serverless Framework のインストール
```bash
# グローバルインストール
npm install -g serverless

# プロジェクト依存関係のインストール
npm install
```

### 3. Python 依存関係のインストール
```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## ローカル開発環境

### 1. ローカルでのLambda関数テスト
```bash
# ローカルでのLambda関数実行
serverless invoke local -f api --path test-event.json

# オフライン開発サーバーの起動
serverless offline start
```

### 2. ローカルでのFastAPI開発サーバー
```bash
# 開発サーバーの起動
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# APIドキュメントの確認
# http://localhost:8000/docs
```

## デプロイメント

### 1. 開発環境へのデプロイ
```bash
# 開発環境へのデプロイ
serverless deploy --stage dev

# 環境変数の設定
export DATABASE_URL="your-dev-database-url"
```

### 2. 本番環境へのデプロイ
```bash
# 本番環境へのデプロイ
serverless deploy --stage prod

# 環境変数の設定
export DATABASE_URL="your-prod-database-url"
```

### 3. CI/CD パイプラインでのデプロイ
GitHub Actions を使用した自動デプロイメントが設定されています。

**必要なGitHub Secrets:**
- `AWS_ACCESS_KEY_ID`: AWSアクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWSシークレットアクセスキー
- `DATABASE_URL`: 本番データベースURL
- `DATABASE_URL_DEV`: 開発データベースURL

## 設定ファイル

### serverless.yml
```yaml
service: study-tracker-api
provider:
  name: aws
  runtime: python3.11
  region: ap-northeast-1
  memorySize: 512
  timeout: 30
```

### package.json
```json
{
  "scripts": {
    "deploy": "serverless deploy",
    "deploy:prod": "serverless deploy --stage prod",
    "offline": "serverless offline start"
  }
}
```

## 環境変数

### 開発環境
```bash
STAGE=dev
DATABASE_URL=sqlite:///./study_tracker.db
```

### 本番環境
```bash
STAGE=prod
DATABASE_URL=postgresql://user:password@host:port/database
```

## モニタリング・ログ

### CloudWatch Logs の確認
```bash
# ログの確認
serverless logs -f api

# リアルタイムログ
serverless logs -f api --tail
```

### メトリクスの確認
- AWS Lambda コンソールでメトリクスを確認
- CloudWatch でカスタムメトリクスを設定

## トラブルシューティング

### よくある問題

#### 1. 依存関係エラー
```bash
# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall

# Lambda Layer の再作成
serverless deploy --force
```

#### 2. タイムアウトエラー
```yaml
# serverless.yml でタイムアウトを調整
provider:
  timeout: 60  # 秒単位
```

#### 3. メモリ不足エラー
```yaml
# serverless.yml でメモリを調整
provider:
  memorySize: 1024  # MB単位
```

#### 4. 環境変数エラー
```bash
# 環境変数の確認
serverless print

# 環境変数の設定
serverless deploy --env production
```

## セキュリティ

### IAM ロール
- 最小権限の原則に従ったIAMロール設定
- CloudWatch Logs への書き込み権限のみ付与

### 環境変数の暗号化
```bash
# AWS Systems Manager Parameter Store を使用
aws ssm put-parameter \
  --name "/study-tracker/prod/database-url" \
  --value "your-database-url" \
  --type "SecureString"
```

## パフォーマンス最適化

### 1. コールドスタートの最小化
- Lambda Layer の活用
- 依存関係の最適化
- 初期化コードの効率化

### 2. メモリ・タイムアウトの最適化
```yaml
provider:
  memorySize: 512    # 適切なメモリ設定
  timeout: 30        # 適切なタイムアウト設定
```

### 3. データベース接続プール
- 接続プールの設定
- 接続の再利用
- 効率的なクエリ実行

## ロールバック

### 1. 手動ロールバック
```bash
# 前のバージョンにロールバック
serverless rollback --timestamp 2023-08-03T10:00:00.000Z
```

### 2. 自動ロールバック
- CloudWatch アラームの設定
- 自動ロールバックのトリガー設定

## 参考資料

- [Serverless Framework Documentation](https://www.serverless.com/framework/docs/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Mangum Documentation](https://mangum.io/)
- [FastAPI on AWS Lambda](https://fastapi.tiangolo.com/deployment/serverless/)

---

**最終更新**: 2025年8月3日
**バージョン**: 1.0.0 