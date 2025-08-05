# AWSリソース クリーンアップチェックリスト

## 📋 現在の状況（2025年8月3日時点）

### 発見されたStudyTracker関連リソース

#### 1. Lambda関数
- **関数名**: `study-tracker-api`
- **ARN**: `arn:aws:lambda:ap-northeast-1:572163715344:function:study-tracker-api`
- **最終更新**: 2025-08-03T01:33:27.647+0000
- **状態**: アクティブ（料金発生中）

#### 2. DynamoDBテーブル
- **テーブル名**: `study-records`
- **状態**: アクティブ（料金発生中）

#### 3. S3バケット
- **バケット名**: `study-tracker-2025-1754182796`
- **作成日**: 2025-08-03 10:15:53
- **状態**: アクティブ（料金発生中）

#### 4. IAMロール
- **ロール名**: `study-tracker-lambda-role`
- **状態**: アクティブ

#### 5. CloudWatch Logs
- **ロググループ**: なし（Lambda関数削除時に自動削除される）

---

## 🗑️ クリーンアップ手順

### 1. Lambda関数の削除
```bash
# Lambda関数を削除
aws lambda delete-function \
  --function-name study-tracker-api \
  --region ap-northeast-1
```

### 2. DynamoDBテーブルの削除
```bash
# DynamoDBテーブルを削除
aws dynamodb delete-table \
  --table-name study-records \
  --region ap-northeast-1
```

### 3. S3バケットの削除
```bash
# S3バケット内のオブジェクトを削除
aws s3 rm s3://study-tracker-2025-1754182796 --recursive

# S3バケットを削除
aws s3 rb s3://study-tracker-2025-1754182796 --force
```

### 4. IAMロールの削除
```bash
# IAMロールを削除（ポリシーがアタッチされている場合は先にデタッチ）
aws iam detach-role-policy \
  --role-name study-tracker-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# IAMロールを削除
aws iam delete-role \
  --role-name study-tracker-lambda-role
```

---

## ⚠️ 注意事項

### 料金発生の可能性
- **Lambda関数**: 実行時間に応じて料金発生
- **DynamoDB**: 読み書き容量ユニットに応じて料金発生
- **S3**: ストレージ容量と転送量に応じて料金発生
- **CloudWatch Logs**: ログ保存量に応じて料金発生

### 削除前の確認事項
1. **データのバックアップ**: 重要なデータがある場合は事前にバックアップ
2. **依存関係の確認**: 他のサービスから参照されていないか確認
3. **権限の確認**: 削除権限があるか確認

---

## 🔍 削除後の確認

### 1. Lambda関数の確認
```bash
aws lambda list-functions \
  --region ap-northeast-1 \
  --query 'Functions[?contains(FunctionName, `study-tracker`)].FunctionName'
```

### 2. DynamoDBテーブルの確認
```bash
aws dynamodb list-tables \
  --region ap-northeast-1 \
  --query 'TableNames[?contains(@, `study`)]'
```

### 3. S3バケットの確認
```bash
aws s3 ls | grep study-tracker
```

### 4. IAMロールの確認
```bash
aws iam list-roles \
  --query 'Roles[?contains(RoleName, `study-tracker`)].RoleName'
```

---

## 📊 料金影響

### 削除前の月間料金（推定）
- **Lambda**: $2.00（10万リクエスト/月）
- **DynamoDB**: $3.00（読み書き容量ユニット）
- **S3**: $0.50（20GB使用）
- **CloudWatch**: $0.50（ログ保存）
- **合計**: $6.00/月

### 削除後の料金
- **料金**: $0.00/月
- **節約額**: $6.00/月

---

## 🚀 今後の移行計画

### 移行を再開する際の手順
1. **ローカル環境での完全テスト**
2. **コスト最適化された構成の確認**
3. **段階的なデプロイ**
4. **料金監視の設定**

### 推奨される移行タイミング
- ローカル開発が完了してから
- コスト最適化が完了してから
- 本番運用の準備が整ってから

---

## 📝 記録

| 日時 | 作業内容 | 実行者 | 備考 |
|------|----------|--------|------|
| 2025-08-03 | リソース状況確認 | AIアシスタント | 料金発生リソースを発見 |
| 2025-08-03 | クリーンアップ計画作成 | AIアシスタント | このドキュメント作成 |

---

**作成日**: 2025年8月3日  
**更新日**: 2025年8月3日  
**次回確認**: 移行再開時 