# AWS資産管理・コスト監視インベントリ

## 📋 文書情報

| 項目 | 内容 |
|------|------|
| プロジェクト名 | StudyTracker |
| 文書名 | AWS資産管理・コスト監視インベントリ |
| 版数 | v1.0 |
| 作成日 | 2025年8月3日 |
| 作成者 | AIアシスタント |
| 承認者 | - |

---

## 🏷️ リソースタグ戦略

### 必須タグ
```json
{
  "Project": "study-tracker",
  "Environment": "dev|staging|prod",
  "Owner": "study-tracker-team",
  "CostCenter": "study-tracker-api",
  "ManagedBy": "terraform|serverless"
}
```

### 推奨タグ
```json
{
  "Application": "study-tracker-api",
  "Component": "lambda|database|storage|network",
  "Version": "1.0.0",
  "Backup": "daily|weekly|none",
  "Security": "public|private|restricted"
}
```

---

## 📊 AWSリソースインベントリ

### 1. コンピューティングリソース

#### Lambda関数
| リソース名 | 環境 | ランタイム | メモリ | タイムアウト | 予想コスト/月 |
|------------|------|------------|--------|--------------|---------------|
| study-tracker-api-dev | dev | python3.11 | 512MB | 30s | $2.00 |
| study-tracker-api-prod | prod | python3.11 | 1024MB | 60s | $20.00 |

#### Lambda Layer
| リソース名 | 環境 | サイズ | 内容 | 予想コスト/月 |
|------------|------|--------|------|---------------|
| python-deps-dev | dev | 50MB | FastAPI, SQLAlchemy | $0.10 |
| python-deps-prod | prod | 50MB | FastAPI, SQLAlchemy | $0.10 |

### 2. ストレージリソース

#### S3バケット
| バケット名 | 環境 | 用途 | クラス | 予想サイズ | 予想コスト/月 |
|------------|------|------|--------|-------------|---------------|
| study-tracker-static-dev | dev | 静的ファイル | Standard | 20GB | $0.50 |
| study-tracker-static-prod | prod | 静的ファイル | Standard | 50GB | $1.00 |
| study-tracker-logs-dev | dev | ログ保存 | Standard-IA | 10GB | $0.25 |
| study-tracker-logs-prod | prod | ログ保存 | Standard-IA | 100GB | $2.50 |

#### DynamoDBテーブル
| テーブル名 | 環境 | モード | 用途 | 予想コスト/月 |
|------------|------|--------|------|---------------|
| study-tracker-records-dev | dev | On-Demand | 学習記録 | $1.50 |
| study-tracker-records-prod | prod | Provisioned | 学習記録 | $3.00 |

### 3. ネットワークリソース

#### API Gateway
| API名 | 環境 | タイプ | エンドポイント数 | 予想コスト/月 |
|-------|------|--------|------------------|---------------|
| study-tracker-api-dev | dev | HTTP API | 10 | $0.10 |
| study-tracker-api-prod | prod | HTTP API | 10 | $1.00 |

#### CloudFront
| ディストリビューション名 | 環境 | オリジン | 予想コスト/月 |
|-------------------------|------|----------|---------------|
| study-tracker-cdn-dev | dev | S3 | $0.00 | 初期段階では不使用 |
| study-tracker-cdn-prod | prod | S3 | $0.00 | 初期段階では不使用 |

#### Route 53
| ホストゾーン名 | 環境 | レコード数 | 予想コスト/月 |
|----------------|------|------------|---------------|
| study-tracker.com | prod | 5 | $0.50 |

### 4. セキュリティリソース

#### IAMロール
| ロール名 | 環境 | 用途 | 権限 |
|----------|------|------|------|
| study-tracker-lambda-role-dev | dev | Lambda実行 | CloudWatch Logs, S3 Read |
| study-tracker-lambda-role-prod | prod | Lambda実行 | CloudWatch Logs, S3 Read, RDS |
| study-tracker-rds-role-dev | dev | RDSアクセス | Secrets Manager |
| study-tracker-rds-role-prod | prod | RDSアクセス | Secrets Manager |

#### Secrets Manager
| シークレット名 | 環境 | 用途 | 予想コスト/月 |
|----------------|------|------|---------------|
| study-tracker/app/dev | dev | アプリ認証情報 | $0.00 | 初期段階では不使用 |
| study-tracker/app/prod | prod | アプリ認証情報 | $0.40 |

### 5. 監視・ログリソース

#### CloudWatch
| リソース名 | 環境 | 用途 | 予想コスト/月 |
|------------|------|------|---------------|
| study-tracker-logs-dev | dev | ログ保存 | $0.50 |
| study-tracker-logs-prod | prod | ログ保存 | $2.00 |
| study-tracker-metrics-dev | dev | メトリクス | $0.10 |
| study-tracker-metrics-prod | prod | メトリクス | $0.50 |

#### X-Ray
| サービス名 | 環境 | 用途 | 予想コスト/月 |
|------------|------|------|---------------|
| study-tracker-tracing-dev | dev | 分散トレーシング | $0.00 | 初期段階では不使用 |
| study-tracker-tracing-prod | prod | 分散トレーシング | $1.00 |

---

## 💰 コスト監視・分析

### 月間コスト予測（詳細）

#### 開発環境
| カテゴリ | サービス | 月間コスト | 年間コスト | 備考 |
|----------|----------|------------|------------|------|
| コンピューティング | Lambda | $0.50 | $6.00 | 2.5万リクエスト/月 |
| コンピューティング | Lambda Layer | $0.10 | $1.20 | 依存関係管理 |
| ストレージ | S3 Standard | $0.25 | $3.00 | 10GB使用 |
| ストレージ | S3 Standard-IA | $0.25 | $3.00 | 10GBログ |
| データベース | DynamoDB | $1.50 | $18.00 | On-Demand |
| ネットワーク | API Gateway | $0.025 | $0.30 | 2.5万呼び出し |
| 監視 | CloudWatch | $0.25 | $3.00 | 基本監視 |
| **合計** | | **$2.88** | **$34.50** | **開発環境** |

#### 本番環境
| カテゴリ | サービス | 月間コスト | 年間コスト | 備考 |
|----------|----------|------------|------------|------|
| コンピューティング | Lambda | $2.00 | $24.00 | 10万リクエスト/月 |
| コンピューティング | Lambda Layer | $0.10 | $1.20 | 依存関係管理 |
| ストレージ | S3 Standard | $0.50 | $6.00 | 20GB使用 |
| ストレージ | S3 Standard-IA | $0.50 | $6.00 | 20GBログ |
| データベース | DynamoDB | $3.00 | $36.00 | Provisioned |
| ネットワーク | API Gateway | $0.10 | $1.20 | 10万呼び出し |
| ネットワーク | Route 53 | $0.50 | $6.00 | DNS管理 |
| セキュリティ | Secrets Manager | $0.40 | $4.80 | アプリ認証情報 |
| 監視 | CloudWatch | $0.50 | $6.00 | 基本監視 |
| トレーシング | X-Ray | $1.00 | $12.00 | 分散トレーシング |
| **合計** | | **$8.60** | **$103.20** | **本番環境** |

### コスト最適化の機会

#### 1. DynamoDB最適化
| サービス | 現在のコスト | 最適化後コスト | 節約額 | 節約率 |
|----------|--------------|----------------|--------|--------|
| DynamoDB Provisioned | $3.00/月 | $2.50/月 | $0.50/月 | 17% |
| DynamoDB Auto Scaling | $3.00/月 | $2.00/月 | $1.00/月 | 33% |

#### 2. S3 Intelligent Tiering
| バケット | 現在のクラス | 最適化後 | 節約額/月 |
|----------|--------------|----------|-----------|
| study-tracker-logs-dev | Standard-IA | Intelligent Tiering | $0.05 |
| study-tracker-logs-prod | Standard-IA | Intelligent Tiering | $0.25 |

#### 3. Lambda最適化
| 最適化項目 | 現在 | 最適化後 | 節約額/月 |
|------------|------|----------|-----------|
| メモリ設定 | 512MB | 256MB | $1.00 |
| 実行時間 | 30秒 | 15秒 | $0.50 |

---

## 📈 コスト監視ダッシュボード

### CloudWatch Dashboard設定
```json
{
  "dashboardName": "StudyTracker-Cost-Monitoring",
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "study-tracker-api-prod"],
          ["AWS/Lambda", "Invocations", "FunctionName", "study-tracker-api-prod"],
          ["AWS/Lambda", "Errors", "FunctionName", "study-tracker-api-prod"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "ap-northeast-1"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "study-tracker-db-prod"],
          ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "study-tracker-db-prod"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "ap-northeast-1"
      }
    }
  ]
}
```

### コストアラート設定
```json
{
  "alarmName": "StudyTracker-Monthly-Cost-Alert",
  "alarmDescription": "月間コストが予算を超過した場合のアラート",
  "metricName": "EstimatedCharges",
  "namespace": "AWS/Billing",
  "dimensions": [
    {
      "Name": "Currency",
      "Value": "USD"
    }
  ],
  "threshold": 100,
  "comparisonOperator": "GreaterThanThreshold",
  "evaluationPeriods": 1,
  "period": 86400
}
```

---

## 🔄 リソースライフサイクル管理

### 開発環境
| リソース | 作成タイミング | 削除タイミング | 保持期間 |
|----------|----------------|----------------|----------|
| Lambda関数 | 開発開始時 | 開発終了時 | プロジェクト期間 |
| S3バケット | 開発開始時 | 開発終了時 | プロジェクト期間 |
| RDSインスタンス | 開発開始時 | 開発終了時 | プロジェクト期間 |
| CloudWatch Logs | 自動作成 | 30日後自動削除 | 30日 |

### 本番環境
| リソース | 作成タイミング | 削除タイミング | 保持期間 |
|----------|----------------|----------------|----------|
| Lambda関数 | 本番デプロイ時 | サービス終了時 | サービス期間 |
| S3バケット | 本番デプロイ時 | サービス終了時 | サービス期間 |
| RDSインスタンス | 本番デプロイ時 | サービス終了時 | サービス期間 |
| CloudWatch Logs | 自動作成 | 90日後自動削除 | 90日 |

---

## 📋 定期レビュー項目

### 月次レビュー
- [ ] コスト予測 vs 実際のコスト
- [ ] 未使用リソースの特定
- [ ] パフォーマンスメトリクスの確認
- [ ] セキュリティ設定の確認

### 四半期レビュー
- [ ] リザーブドインスタンスの見直し
- [ ] ストレージクラスの最適化
- [ ] アーキテクチャの見直し
- [ ] コスト最適化の機会調査

### 年次レビュー
- [ ] 長期的なコスト予測
- [ ] 技術スタックの見直し
- [ ] セキュリティ監査
- [ ] 災害復旧計画の更新

---

## 📚 参考資料

### AWS公式ドキュメント
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)
- [AWS Resource Groups](https://docs.aws.amazon.com/ARG/latest/userguide/)
- [AWS Tagging Strategies](https://aws.amazon.com/answers/account-management/aws-tagging-strategies/)

### コスト最適化ツール
- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)
- [AWS Trusted Advisor](https://aws.amazon.com/premiumsupport/technology/trusted-advisor/)
- [AWS Pricing Calculator](https://calculator.aws/)

---

## ✅ 承認

| 役割 | 名前 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | 学習者 | 2025年8月3日 | - |
| インフラ責任者 | AIアシスタント | 2025年8月3日 | - |
| 財務責任者 | AIアシスタント | 2025年8月3日 | - |

---

**文書バージョン**: v1.0  
**最終更新日**: 2025年8月3日  
**次回レビュー**: 2025年8月10日 