# FormDataとJSON対応認証機能

## 概要

Lambda関数の`login_user`と`register_user`関数を修正し、FormDataとJSONの両方の形式でリクエストを受け取れるようにしました。

## 対応形式

### 1. JSON形式（デフォルト）
```json
{
  "username": "test@example.com",
  "password": "password123"
}
```

### 2. FormData形式（application/x-www-form-urlencoded）
```
username=test%40example.com&password=password123
```

### 3. Multipart形式（multipart/form-data）
```
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="username"

test@example.com
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="password"

password123
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

## 実装詳細

### Content-Type判定
- `application/x-www-form-urlencoded`: URLエンコードされたフォームデータとして解析
- `multipart/form-data`: Multipart形式として解析
- その他（デフォルト）: JSONとして解析

### エラーハンドリング
- 無効なJSON形式: 400エラー
- 無効なフォームデータ形式: 400エラー
- 必須フィールド不足: 400エラー

## テスト方法

### 1. テストスクリプトの実行
```bash
python test_formdata_login.py
```

### 2. Lambda関数でのテスト
AWS Lambdaコンソールで以下のテストイベントを使用：

#### FormDataログインテスト
```json
{
  "httpMethod": "POST",
  "path": "/dev/api/v1/auth/login",
  "headers": {
    "Content-Type": "application/x-www-form-urlencoded"
  },
  "body": "username=test%40example.com&password=password123"
}
```

#### JSONログインテスト
```json
{
  "httpMethod": "POST",
  "path": "/dev/api/v1/auth/login",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"username\": \"test@example.com\", \"password\": \"password123\"}"
}
```

## フロントエンドでの使用例

### JavaScript（FormData）
```javascript
const formData = new FormData();
formData.append('username', 'test@example.com');
formData.append('password', 'password123');

fetch('/api/v1/auth/login', {
  method: 'POST',
  body: formData
});
```

### JavaScript（JSON）
```javascript
fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'test@example.com',
    password: 'password123'
  })
});
```

## セキュリティ考慮事項

1. **入力値検証**: すべての入力値に対してサニタイズ処理を実施
2. **Content-Type検証**: 適切なContent-Typeヘッダーの確認
3. **エラーメッセージ**: 詳細なエラー情報を返さないよう配慮
4. **パスワード処理**: 実際の運用ではbcrypt等の適切なハッシュ化を使用

## 今後の改善点

1. **より厳密なMultipart解析**: 現在は簡易的な実装のため、より厳密な解析が必要
2. **ファイルアップロード対応**: 必要に応じてファイルアップロード機能を追加
3. **バリデーション強化**: より詳細な入力値検証の実装
4. **ログ機能**: セキュリティログの実装

## 変更履歴

- 2025-01-XX: FormDataとJSONの両方に対応した認証機能を実装
- `login_user`関数の修正
- `register_user`関数の修正
- テストスクリプトとテストイベントの追加
