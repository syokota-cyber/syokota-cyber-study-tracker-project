# StudyTracker AWS移行技術仕様書

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | AWS移行技術仕様書 |
| 版数 | v1.0 |
| 作成日 | 2025年8月3日 |
| 作成者 | AIアシスタント |
| 承認者 | - |

---

## 🏗️ システムアーキテクチャ

### 移行後のアーキテクチャ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │   CloudFront    │    │   S3 Static     │
│                 │    │                 │    │   Hosting       │
│  Vue.js/React   │◄──►│   + Route 53    │◄──►│   + Vue/React   │
│  + Tailwind CSS │    │   learninggarden│    │   Build Files   │
└─────────────────┘    │   .studio       │    └─────────────────┘
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   API Gateway   │
                       │   HTTP API      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   AWS Lambda    │    │   DynamoDB      │
                       │                 │    │                 │
                       │  FastAPI +      │◄──►│  study-records  │
                       │  Mangum         │    │  (On-Demand)    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   CloudWatch    │
                       │   + Logs        │
                       └─────────────────┘
```

### 既存リソースの活用

#### Route53設定
```yaml
Domain: learninggarden.studio
HostedZoneId: Z101042423Z2DRKY6F711
CurrentRecords:
  - Type: A
    Name: learninggarden.studio
    Target: d198uibra12k42.cloudfront.net
  - Type: NS
    Name: learninggarden.studio
    Values: [ns-540.awsdns-03.net, ns-488.awsdns-61.com, ...]
```

#### CloudFront設定
```yaml
DistributionId: E3RTAE75MJ0MSH
DomainName: dq90z1ht2u7q4.cloudfront.net
Aliases: [learninggarden.studio]
SSL: ACM Certificate (arn:aws:acm:us-east-1:572163715344:certificate/ad191ceb-ce49-45d8-9e0e-b1b2010267dc)
Status: Deployed (Enabled: false)
```

---

## 🛠️ 技術スタック

### バックエンド
- **ランタイム**: Python 3.11
- **フレームワーク**: FastAPI
- **AWS Lambda**: サーバーレス実行環境
- **Mangum**: FastAPI to Lambda アダプター
- **データベース**: DynamoDB (On-Demand)
- **API Gateway**: HTTP API

### フロントエンド
- **フレームワーク**: Vue.js 3.x / React 18.x
- **スタイリング**: Tailwind CSS
- **ビルドツール**: Vite / Webpack
- **ホスティング**: S3 Static Website Hosting
- **CDN**: CloudFront

### インフラ・運用
- **DNS**: Route 53
- **SSL**: AWS Certificate Manager
- **CI/CD**: GitHub Actions
- **モニタリング**: CloudWatch
- **ログ**: CloudWatch Logs

---

## 📊 データベース設計

### DynamoDBスキーマ

#### study-records テーブル
```yaml
TableName: study-records
BillingMode: PAY_PER_REQUEST
AttributeDefinitions:
  - AttributeName: id
    AttributeType: S
  - AttributeName: user_id
    AttributeType: S
  - AttributeName: created_at
    AttributeType: S
KeySchema:
  - AttributeName: id
    KeyType: HASH
GlobalSecondaryIndexes:
  - IndexName: UserIdCreatedAtIndex
    KeySchema:
      - AttributeName: user_id
        KeyType: HASH
      - AttributeName: created_at
        KeyType: RANGE
    Projection:
      ProjectionType: ALL
```

#### データモデル
```python
class StudyRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    content: str
    category: str
    study_time: int  # minutes
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = []
    goals: List[str] = []
```

---

## 🔧 設定ファイル

### Serverless Framework設定
```yaml
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

resources:
  Resources:
    StudyTrackerRecordsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: study-records
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
          - AttributeName: user_id
            AttributeType: S
          - AttributeName: created_at
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        GlobalSecondaryIndexes:
          - IndexName: UserIdCreatedAtIndex
            KeySchema:
              - AttributeName: user_id
                KeyType: HASH
              - AttributeName: created_at
                KeyType: RANGE
            Projection:
              ProjectionType: ALL
```

### CloudFront設定更新
```yaml
DistributionConfig:
  Origins:
    Items:
      - Id: study-tracker-api
        DomainName: ${API_GATEWAY_URL}
        CustomOriginConfig:
          HTTPPort: 443
          HTTPSPort: 443
          OriginProtocolPolicy: https-only
      - Id: study-tracker-frontend
        DomainName: ${S3_BUCKET}.s3.ap-northeast-1.amazonaws.com
        S3OriginConfig:
          OriginAccessIdentity: ""
  CacheBehaviors:
    Items:
      - PathPattern: /api/*
        TargetOriginId: study-tracker-api
        ViewerProtocolPolicy: redirect-to-https
        AllowedMethods:
          Items: [GET, POST, PUT, DELETE, OPTIONS]
        CachedMethods:
          Items: [GET, HEAD]
        DefaultTTL: 0
        MinTTL: 0
        MaxTTL: 0
      - PathPattern: /*
        TargetOriginId: study-tracker-frontend
        ViewerProtocolPolicy: redirect-to-https
        AllowedMethods:
          Items: [GET, HEAD]
        CachedMethods:
          Items: [GET, HEAD]
        DefaultTTL: 86400  # 24時間
```

---

## 🔒 セキュリティ設計

### IAMロール設定
```yaml
LambdaExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: study-tracker-lambda-role
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: DynamoDBAccess
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:DeleteItem
                - dynamodb:Query
                - dynamodb:Scan
              Resource: 
                - !GetAtt StudyTrackerRecordsTable.Arn
                - !Sub "${StudyTrackerRecordsTable.Arn}/index/*"
```

### CORS設定
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://learninggarden.studio"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 パフォーマンス設計

### Lambda最適化
- **メモリ**: 256MB（コスト最適化）
- **タイムアウト**: 15秒
- **同時実行数**: 1000（デフォルト）
- **プロビジョニング**: 必要に応じて

### DynamoDB最適化
- **オンデマンドモード**: 使用量に応じた課金
- **パーティションキー**: id（UUID）
- **GSI**: user_id + created_at
- **TTL**: 不要（学習データは永続保存）

### CloudFront最適化
- **キャッシュ**: API（0秒）、フロントエンド（24時間）
- **圧縮**: 有効
- **HTTP/2**: 有効
- **エッジロケーション**: 自動選択

---

## 🔄 CI/CDパイプライン

### GitHub Actions設定
```yaml
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
```

---

## 📊 モニタリング・ログ

### CloudWatch設定
```yaml
LogGroups:
  - LogGroupName: /aws/lambda/study-tracker-api
    RetentionInDays: 30
    MetricFilters:
      - FilterName: ErrorCount
        FilterPattern: "[timestamp, request_id, level=ERROR, ...]"
        MetricTransformations:
          - MetricName: ErrorCount
            MetricNamespace: StudyTracker
            MetricValue: "1"

Alarms:
  - AlarmName: study-tracker-api-errors
    MetricName: ErrorCount
    Namespace: StudyTracker
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
```

### カスタムメトリクス
```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='StudyTracker',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.now()
            }
        ]
    )
```

---

## 💰 コスト最適化

### 月間コスト予測（最適化後）
| サービス | 開発環境 | 本番環境 | 合計 |
|----------|----------|----------|------|
| Lambda | $0.25 | $1.00 | $1.25 |
| API Gateway | $0.025 | $0.10 | $0.125 |
| DynamoDB | $1.50 | $2.50 | $4.00 |
| S3 | $0.25 | $0.50 | $0.75 |
| CloudWatch | $0.25 | $0.50 | $0.75 |
| Route 53 | $0.00 | $0.50 | $0.50 |
| **合計** | **$2.28** | **$5.10** | **$7.38** |

### コスト削減戦略
1. **Lambda最適化**: メモリ256MB、タイムアウト15秒
2. **DynamoDB On-Demand**: 使用量に応じた課金
3. **CloudFrontキャッシュ**: 転送量削減
4. **S3 Intelligent Tiering**: 自動ストレージ最適化

---

## 🔧 移行手順

### Phase 1: 基盤準備
1. 既存リソースの詳細調査
2. Lambda関数の最適化
3. DynamoDBスキーマ設計
4. 基本的なAPIテスト

### Phase 2: アプリケーション移行
1. フロントエンドのS3移行
2. CloudFront設定更新
3. API Gateway設定
4. エンドツーエンドテスト

### Phase 3: 本番化
1. CI/CDパイプライン構築
2. モニタリング設定
3. セキュリティ強化
4. 本番リリース

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年8月3日 | - |
| 技術責任者 | AIアシスタント | 2025年8月3日 | - |

---

**文書バージョン**: v1.0  
**最終更新日**: 2025年8月3日 