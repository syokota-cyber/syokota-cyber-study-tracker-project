# StudyTracker AWS移行手順書

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | AWS移行手順書 |
| 版数 | v1.0 |
| 作成日 | 2025年8月3日 |
| 作成者 | AIアシスタント |
| 承認者 | - |

---

## 🎯 移行概要

### 移行対象
- **アプリケーション**: StudyTracker（学習管理アプリ）
- **現在環境**: ローカル開発環境（SQLite + FastAPI）
- **移行先**: AWSサーバーレス環境
- **既存リソース活用**: Route53（learninggarden.studio）、CloudFront（E3RTAE75MJ0MSH）

### 移行目標
- 月間$5.50以内での運用コスト実現
- 既存ドメインでの継続サービス提供
- サーバーレスアーキテクチャによるスケーラビリティ確保

---

## 📋 事前準備チェックリスト

### 既存リソース確認
- [ ] Route53ドメイン（learninggarden.studio）の確認
- [ ] CloudFrontディストリビューション（E3RTAE75MJ0MSH）の確認
- [ ] Lambda関数（study-tracker-api）の確認
- [ ] DynamoDBテーブル（study-records）の確認
- [ ] S3バケット（study-tracker-2025-1754182796）の確認

### 開発環境準備
- [ ] AWS CLIの設定
- [ ] Serverless Frameworkのインストール
- [ ] Node.js環境の準備
- [ ] Python環境の準備
- [ ] GitHub Actionsの設定

### 認証情報準備
- [ ] AWS Access Key ID
- [ ] AWS Secret Access Key
- [ ] GitHub Secrets設定

---

## 🔄 Phase 1: 基盤構築（Week 1）

### Day 1: 既存リソースの詳細調査

#### 1.1 Route53設定確認
```bash
# ホストゾーンの詳細確認
aws route53 get-hosted-zone --id Z101042423Z2DRKY6F711

# レコードセットの確認
aws route53 list-resource-record-sets --hosted-zone-id Z101042423Z2DRKY6F711
```

#### 1.2 CloudFront設定確認
```bash
# ディストリビューションの詳細確認
aws cloudfront get-distribution --id E3RTAE75MJ0MSH

# 設定の取得
aws cloudfront get-distribution-config --id E3RTAE75MJ0MSH
```

#### 1.3 既存Lambda関数確認
```bash
# Lambda関数の詳細確認
aws lambda get-function --function-name study-tracker-api

# 関数設定の確認
aws lambda get-function-configuration --function-name study-tracker-api
```

#### 1.4 DynamoDBテーブル確認
```bash
# テーブルの詳細確認
aws dynamodb describe-table --table-name study-records

# テーブル項目の確認
aws dynamodb scan --table-name study-records --limit 10
```

### Day 2: Lambda関数の最適化

#### 2.1 Serverless Framework設定更新
```bash
# serverless.ymlの更新
cat > serverless.yml << 'EOF'
service: study-tracker-api

provider:
  name: aws
  runtime: python3.11
  region: ap-northeast-1
  stage: ${opt:stage, 'dev'}
  memorySize: 256  # コスト最適化
  timeout: 15      # コスト最適化
  environment:
    STAGE: ${self:provider.stage}
    DYNAMODB_TABLE: study-records
    CORS_ORIGIN: https://learninggarden.studio
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: "arn:aws:logs:*:*:*"
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Query
            - dynamodb:Scan
          Resource: "arn:aws:dynamodb:${self:provider.region}:*:table/study-records"

functions:
  api:
    handler: package.lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    environment:
      PYTHONPATH: /var/task
    layers:
      - Ref: PythonRequirementsLambdaLayer

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: non-linux
    layer:
      name: python-deps
      description: Python dependencies for study-tracker-api
    noDeploy:
      - coverage
      - pytest
      - black
      - flake8
      - isort
      - bandit
      - safety
      - mkdocs
      - mkdocs-material

package:
  patterns:
    - '!node_modules/**'
    - '!tests/**'
    - '!docs/**'
    - '!logs/**'
    - '!venv/**'
    - '!.git/**'
EOF
```

#### 2.2 依存関係の更新
```bash
# requirements.txtの更新
cat >> requirements.txt << 'EOF'

# AWS Lambda Support
mangum>=0.17.0
boto3>=1.34.0

# Database
dynamodb-encryption-sdk>=4.0.0
EOF
```

#### 2.3 Lambda Handlerの確認
```bash
# lambda_handler.pyの確認
cat package/lambda_handler.py
```

### Day 3: DynamoDBスキーマ設計

#### 3.1 既存データの分析
```bash
# 既存データの構造確認
aws dynamodb scan --table-name study-records --limit 5
```

#### 3.2 スキーマ最適化
```bash
# 新しいテーブル構造の作成（必要に応じて）
aws dynamodb create-table \
  --table-name study-records-optimized \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    IndexName=UserIdCreatedAtIndex,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL}
```

### Day 4-5: 基本的なAPIテスト

#### 4.1 ローカルテスト
```bash
# ローカルでのテスト実行
serverless offline start

# 別ターミナルでテスト
curl -X GET http://localhost:3000/health
curl -X GET http://localhost:3000/api/v1/study-records/
```

#### 4.2 デプロイテスト
```bash
# 開発環境へのデプロイ
serverless deploy --stage dev

# デプロイ後のテスト
curl -X GET https://[API_GATEWAY_URL]/health
```

---

## 🔄 Phase 2: アプリケーション移行（Week 2）

### Day 6-7: フロントエンドのS3移行

#### 6.1 S3バケットの準備
```bash
# フロントエンド用バケットの作成
aws s3 mb s3://study-tracker-frontend

# 静的ウェブサイトホスティングの設定
aws s3 website s3://study-tracker-frontend --index-document index.html --error-document index.html

# バケットポリシーの設定
cat > bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::study-tracker-frontend/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket study-tracker-frontend --policy file://bucket-policy.json
```

#### 6.2 フロントエンドのビルド
```bash
# フロントエンドディレクトリに移動
cd study-tracker-frontend

# 依存関係のインストール
npm install

# 本番ビルド
npm run build

# S3へのアップロード
aws s3 sync dist/ s3://study-tracker-frontend --delete
```

### Day 8-9: CloudFront設定更新

#### 8.1 現在の設定をバックアップ
```bash
# 現在の設定を取得
aws cloudfront get-distribution-config --id E3RTAE75MJ0MSH > cloudfront-config-backup.json
```

#### 8.2 新しい設定の作成
```bash
# 新しい設定ファイルの作成
cat > cloudfront-update.json << 'EOF'
{
  "DistributionConfig": {
    "Origins": {
      "Quantity": 2,
      "Items": [
        {
          "Id": "study-tracker-api",
          "DomainName": "[API_GATEWAY_URL]",
          "CustomOriginConfig": {
            "HTTPPort": 443,
            "HTTPSPort": 443,
            "OriginProtocolPolicy": "https-only"
          }
        },
        {
          "Id": "study-tracker-frontend",
          "DomainName": "study-tracker-frontend.s3.ap-northeast-1.amazonaws.com",
          "S3OriginConfig": {
            "OriginAccessIdentity": ""
          }
        }
      ]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "study-tracker-frontend",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Quantity": 2,
        "Items": ["HEAD", "GET"],
        "CachedMethods": {
          "Quantity": 2,
          "Items": ["HEAD", "GET"]
        }
      },
      "DefaultTTL": 86400,
      "MinTTL": 0,
      "MaxTTL": 31536000
    },
    "CacheBehaviors": {
      "Quantity": 1,
      "Items": [
        {
          "PathPattern": "/api/*",
          "TargetOriginId": "study-tracker-api",
          "ViewerProtocolPolicy": "redirect-to-https",
          "AllowedMethods": {
            "Quantity": 5,
            "Items": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "CachedMethods": {
              "Quantity": 2,
              "Items": ["GET", "HEAD"]
            }
          },
          "DefaultTTL": 0,
          "MinTTL": 0,
          "MaxTTL": 0
        }
      ]
    },
    "Aliases": {
      "Quantity": 1,
      "Items": ["learninggarden.studio"]
    },
    "Enabled": true
  }
}
EOF
```

#### 8.3 CloudFront設定の更新
```bash
# ETagの取得
ETAG=$(aws cloudfront get-distribution-config --id E3RTAE75MJ0MSH --query 'ETag' --output text)

# 設定の更新
aws cloudfront update-distribution \
  --id E3RTAE75MJ0MSH \
  --distribution-config file://cloudfront-update.json \
  --if-match $ETAG
```

### Day 10: API Gateway設定

#### 10.1 API Gatewayの確認
```bash
# API Gatewayの詳細確認
aws apigatewayv2 get-apis

# 特定のAPIの詳細
aws apigatewayv2 get-api --api-id [API_ID]
```

#### 10.2 CORS設定の更新
```bash
# CORS設定の更新
aws apigatewayv2 update-api \
  --api-id [API_ID] \
  --cors-configuration AllowOrigins="https://learninggarden.studio"
```

### Day 11-12: エンドツーエンドテスト

#### 11.1 統合テスト
```bash
# フロントエンドアクセステスト
curl -I https://learninggarden.studio

# APIアクセステスト
curl -X GET https://learninggarden.studio/api/v1/health

# 学習記録APIテスト
curl -X POST https://learninggarden.studio/api/v1/study-records/ \
  -H "Content-Type: application/json" \
  -d '{"title":"テスト学習","content":"テスト内容","category":"テスト","study_time":60}'
```

#### 11.2 パフォーマンステスト
```bash
# レスポンス時間の測定
time curl -X GET https://learninggarden.studio/api/v1/health

# 負荷テスト（簡易版）
for i in {1..10}; do
  curl -X GET https://learninggarden.studio/api/v1/health &
done
wait
```

---

## 🔄 Phase 3: 本番化（Week 3）

### Day 13-14: CI/CDパイプライン構築

#### 13.1 GitHub Actions設定
```bash
# .github/workflows/deploy.ymlの作成
mkdir -p .github/workflows

cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to AWS

on:
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Serverless Framework
        run: |
          npm install -g serverless
          npm install
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
      
      - name: Deploy API
        run: serverless deploy --stage prod
      
      - name: Build Frontend
        run: |
          cd study-tracker-frontend
          npm install
          npm run build
      
      - name: Deploy Frontend
        run: |
          aws s3 sync study-tracker-frontend/dist/ s3://study-tracker-frontend --delete
          aws cloudfront create-invalidation --distribution-id E3RTAE75MJ0MSH --paths "/*"
EOF
```

#### 13.2 GitHub Secrets設定
```bash
# GitHub Secretsの設定（手動）
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# DATABASE_URL
```

### Day 15: モニタリング設定

#### 15.1 CloudWatchアラーム設定
```bash
# エラー率アラームの作成
aws cloudwatch put-metric-alarm \
  --alarm-name study-tracker-api-errors \
  --alarm-description "StudyTracker API Error Rate" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=FunctionName,Value=study-tracker-api

# レスポンス時間アラームの作成
aws cloudwatch put-metric-alarm \
  --alarm-name study-tracker-api-duration \
  --alarm-description "StudyTracker API Duration" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=FunctionName,Value=study-tracker-api
```

#### 15.2 ログ設定
```bash
# ログ保持期間の設定
aws logs put-retention-policy \
  --log-group-name /aws/lambda/study-tracker-api \
  --retention-in-days 30
```

### Day 16: セキュリティ強化

#### 16.1 IAMロールの最適化
```bash
# 最小権限の原則に基づく権限設定
# serverless.ymlで既に設定済み
```

#### 16.2 WAF設定（オプション）
```bash
# Web Application Firewallの設定（必要に応じて）
aws wafv2 create-web-acl \
  --name study-tracker-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --description "StudyTracker WAF"
```

### Day 17-18: 本番リリース

#### 17.1 最終テスト
```bash
# 本番環境での包括的テスト
curl -X GET https://learninggarden.studio/api/v1/health
curl -X GET https://learninggarden.studio/api/v1/study-records/
curl -X POST https://learninggarden.studio/api/v1/study-records/ \
  -H "Content-Type: application/json" \
  -d '{"title":"本番テスト","content":"本番環境でのテスト","category":"テスト","study_time":30}'
```

#### 17.2 パフォーマンス監視
```bash
# CloudWatchメトリクスの確認
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=study-tracker-api \
  --start-time $(date -d '1 hour ago' --iso-8601=seconds) \
  --end-time $(date --iso-8601=seconds) \
  --period 300 \
  --statistics Average
```

#### 17.3 コスト監視
```bash
# コスト使用量の確認
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. Lambda関数のタイムアウト
```bash
# タイムアウト設定の確認
aws lambda get-function-configuration --function-name study-tracker-api --query 'Timeout'

# タイムアウト設定の更新
aws lambda update-function-configuration \
  --function-name study-tracker-api \
  --timeout 15
```

#### 2. CORSエラー
```bash
# CORS設定の確認
aws apigatewayv2 get-api --api-id [API_ID] --query 'CorsConfiguration'

# CORS設定の更新
aws apigatewayv2 update-api \
  --api-id [API_ID] \
  --cors-configuration AllowOrigins="https://learninggarden.studio",AllowMethods="GET,POST,PUT,DELETE,OPTIONS"
```

#### 3. DynamoDB接続エラー
```bash
# テーブル存在確認
aws dynamodb describe-table --table-name study-records

# IAM権限確認
aws iam get-role-policy --role-name study-tracker-lambda-role --policy-name DynamoDBAccess
```

#### 4. CloudFrontキャッシュ問題
```bash
# キャッシュ無効化
aws cloudfront create-invalidation \
  --distribution-id E3RTAE75MJ0MSH \
  --paths "/*"
```

---

## 📊 移行完了チェックリスト

### 機能確認
- [ ] フロントエンドが正常に表示される
- [ ] APIエンドポイントが正常に動作する
- [ ] データベース操作が正常に動作する
- [ ] 認証・認可が正常に動作する

### パフォーマンス確認
- [ ] ページ読み込み時間が3秒以下
- [ ] API応答時間が200ms以下
- [ ] エラー率が1%以下
- [ ] 可用性が99.9%以上

### セキュリティ確認
- [ ] HTTPS通信が正常に動作する
- [ ] CORS設定が適切
- [ ] IAM権限が最小限
- [ ] ログが適切に記録される

### コスト確認
- [ ] 月間コストが$5.50以下
- [ ] 予想コストと実際のコストが一致
- [ ] コスト監視が設定されている
- [ ] アラートが設定されている

---

## 📈 移行後の運用

### 日常監視
- CloudWatchダッシュボードの確認
- エラーログの確認
- パフォーマンスメトリクスの確認
- コスト使用量の確認

### 定期メンテナンス
- 月次セキュリティパッチの適用
- 依存関係の更新
- バックアップの確認
- パフォーマンス最適化

### 拡張計画
- 新機能の追加
- トラフィック増加への対応
- セキュリティ強化
- コスト最適化

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年8月3日 | - |
| 技術責任者 | AIアシスタント | 2025年8月3日 | - |

---

**文書バージョン**: v1.0  
**最終更新日**: 2025年8月3日 