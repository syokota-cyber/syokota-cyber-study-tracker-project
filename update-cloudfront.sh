#!/bin/bash

# StudyTracker CloudFront設定更新スクリプト
# 作成日: 2025年8月6日

set -e

echo "🚀 StudyTracker CloudFront設定更新を開始します..."

# 変数設定
DISTRIBUTION_ID="E3RTAE75MJ0MSH"
CONFIG_FILE="cloudfront-update-simple.json"
BACKUP_FILE="cloudfront-config-backup-$(date +%Y%m%d-%H%M%S).json"

echo "📋 設定情報:"
echo "  - ディストリビューションID: $DISTRIBUTION_ID"
echo "  - 設定ファイル: $CONFIG_FILE"
echo "  - バックアップファイル: $BACKUP_FILE"

# 1. 現在の設定をバックアップ
echo "💾 現在の設定をバックアップ中..."
aws cloudfront get-distribution-config --id $DISTRIBUTION_ID > $BACKUP_FILE
echo "✅ バックアップ完了: $BACKUP_FILE"

# 2. ETagを取得
echo "🔍 ETagを取得中..."
ETAG=$(aws cloudfront get-distribution-config --id $DISTRIBUTION_ID --query 'ETag' --output text)
echo "✅ ETag取得完了: $ETAG"

# 3. 設定ファイルの存在確認
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 設定ファイルが見つかりません: $CONFIG_FILE"
    exit 1
fi

echo "📄 設定ファイル確認完了: $CONFIG_FILE"

# 4. CloudFront設定を更新
echo "🔄 CloudFront設定を更新中..."
aws cloudfront update-distribution \
    --id $DISTRIBUTION_ID \
    --distribution-config file://$CONFIG_FILE \
    --if-match $ETAG

echo "✅ CloudFront設定更新完了！"

# 5. 更新状況を確認
echo "🔍 更新状況を確認中..."
aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.Status' --output text

echo "🎉 CloudFront設定更新が完了しました！"
echo ""
echo "📊 更新内容:"
echo "  - フロントエンド: study-tracker-2025-1754182796.s3.ap-northeast-1.amazonaws.com"
echo "  - API: o1kb9ujxjf.execute-api.ap-northeast-1.amazonaws.com/dev"
echo "  - ドメイン: learninggarden.studio"
echo "  - APIパス: /api/*"
echo ""
echo "🌐 アクセスURL:"
echo "  - フロントエンド: https://learninggarden.studio"
echo "  - API: https://learninggarden.studio/api/v1/study-records"
echo "  - ヘルスチェック: https://learninggarden.studio/api/health"
echo ""
echo "⚠️  注意: 設定の反映には数分かかる場合があります。" 