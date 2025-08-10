import json
import boto3
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64
import hmac
import hashlib
import json
from datetime import datetime, timezone, timedelta
import os

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('study-records')

# JWT認証設定
SECRET_KEY = "your-secret-key-for-development-only-change-in-production"
ALGORITHM = "HS256"

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

def validate_study_record(data: Dict[str, Any]) -> List[str]:
    """学習記録データの検証"""
    errors = []
    
    # タイトルの検証
    title = data.get('title', '').strip()
    if not title:
        errors.append('title is required')
    elif len(title) > 200:
        errors.append('title must be 200 characters or less')
    else:
        data['title'] = sanitize_input(title, 200)
    
    # コンテンツの検証
    content = data.get('content', '')
    if content and len(content) > 1000:
        errors.append('content must be 1000 characters or less')
    else:
        data['content'] = sanitize_input(content, 1000)
    
    # 学習時間の検証
    study_time = data.get('study_time', 0)
    try:
        study_time = int(study_time)
        if study_time < 0 or study_time > 1440:  # 24時間以内
            errors.append('study_time must be between 0 and 1440 minutes')
        data['study_time'] = study_time
    except (ValueError, TypeError):
        errors.append('study_time must be a valid integer')
    
    # カテゴリの検証
    category = data.get('category', '')
    if category and len(category) > 50:
        errors.append('category must be 50 characters or less')
    else:
        data['category'] = sanitize_input(category, 50)
    
    # 難易度の検証
    difficulty = data.get('difficulty', 1)
    try:
        difficulty = int(difficulty)
        if difficulty < 1 or difficulty > 5:
            errors.append('difficulty must be between 1 and 5')
        data['difficulty'] = difficulty
    except (ValueError, TypeError):
        errors.append('difficulty must be a valid integer between 1 and 5')
    
    return errors

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWTトークンを検証（標準ライブラリベース）
    
    Args:
        token: 検証するJWTトークン
    
    Returns:
        検証成功時はペイロード、失敗時はNone
    """
    try:
        # JWTトークンの構造: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # ペイロードのデコード
        payload_padding = payload_b64 + '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_padding)
        payload = json.loads(payload_json)
        
        # 有効期限チェック
        exp = payload.get('exp')
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None
        
        # 署名検証（簡易版 - 実際の運用ではより厳密に）
        expected_signature = hmac.new(
            SECRET_KEY.encode('utf-8'),
            f"{header_b64}.{payload_b64}".encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode('utf-8').rstrip('=')
        
        if signature_b64 != expected_signature_b64:
            return None
        
        return payload
    except Exception:
        return None

def get_current_user_from_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    イベントからJWTトークンを取得し、ユーザー情報を返す
    
    Args:
        event: Lambda イベント
    
    Returns:
        ユーザー情報（成功時）、None（失敗時）
    """
    # Authorizationヘッダーからトークンを取得
    headers = event.get('headers', {})
    authorization = headers.get('Authorization') or headers.get('authorization')
    
    if not authorization:
        return None
    
    # "Bearer <token>" 形式からトークンを抽出
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    token = parts[1]
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return {"user_id": user_id}

def create_access_token(data: dict) -> str:
    """
    JWTアクセストークンを生成（標準ライブラリベース）
    
    Args:
        data: トークンに含めるデータ（通常はユーザーID）
    
    Returns:
        生成されたJWTトークン
    """
    # ヘッダー
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # ペイロード
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire.timestamp()})
    
    # Base64エンコード
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).decode('utf-8').rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode('utf-8')).decode('utf-8').rstrip('=')
    
    # 署名生成
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    # JWTトークン生成
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def create_test_login_token() -> Dict[str, Any]:
    """
    テスト用のログイントークンを生成
    """
    # テスト用ユーザーID（実際は認証フローで取得）
    test_user_id = "test-user-12345"
    
    access_token = create_access_token(data={"sub": test_user_id})
    
    return create_response(200, {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": test_user_id,
        "message": "Test login successful"
    })

def handler(event, context):
    """Lambda関数のメインハンドラー（セキュリティ強化版）"""
    try:
        # HTTPメソッドの取得
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        
        # デバッグ用ログ出力
        print(f"DEBUG: HTTP Method = {http_method}")
        print(f"DEBUG: Path = {path}")
        
        # OPTIONSリクエストの処理（CORSプリフライト）
        if http_method == 'OPTIONS':
            return create_response(200, {})
        
        # パスの解析（CloudFrontのOriginPath /dev を考慮）
        path_parts = path.strip('/').split('/')
        print(f"DEBUG: Path parts = {path_parts}")
        
        # /dev/api/v1/... の形式に対応
        if len(path_parts) >= 4 and path_parts[0] == 'dev' and path_parts[1] == 'api' and path_parts[2] == 'v1':
            # /dev を除去して /api/v1/... の形式に変換
            path_parts = path_parts[1:]  # dev を除去
        elif len(path_parts) >= 3 and path_parts[0] == 'api' and path_parts[1] == 'v1':
            # 直接 /api/v1/... の形式
            pass
        else:
            return create_response(404, {'error': 'API version not found'})
        
        print(f"DEBUG: Adjusted path parts = {path_parts}")
        
        # APIバージョンチェック
        if len(path_parts) < 3 or path_parts[0] != 'api' or path_parts[1] != 'v1':
            return create_response(404, {'error': 'API version not found'})
        
        # エンドポイントの判定
        endpoint = path_parts[2] if len(path_parts) > 2 else ''
        print(f"DEBUG: Endpoint = {endpoint}")
        
        # 学習記録関連のエンドポイント
        if endpoint == 'study-records':
            # 🔐 認証チェック（学習記録は認証が必要）
            current_user = get_current_user_from_event(event)
            if not current_user:
                return create_response(401, {
                    'error': 'Unauthorized', 
                    'message': 'Authentication required to access study records'
                })
            
            user_id = current_user['user_id']
            print(f"DEBUG: Authenticated user_id = {user_id}")
            
            # 個別レコードのID取得
            record_id = path_parts[3] if len(path_parts) > 3 else None
            
            if http_method == 'GET':
                if record_id:
                    return get_study_record(record_id, user_id)
                else:
                    # クエリパラメータでページネーション判定
                    query_params = event.get('queryStringParameters', {}) or {}
                    if 'page' in query_params or 'limit' in query_params:
                        return get_paginated_study_records(event, user_id)
                    else:
                        return get_study_records(user_id)
            
            elif http_method == 'POST':
                return create_study_record(event, user_id)
            
            elif http_method == 'PUT':
                if record_id:
                    return update_study_record(record_id, event, user_id)
                else:
                    return create_response(400, {'error': 'Record ID required for update'})
            
            elif http_method == 'DELETE':
                if record_id:
                    return delete_study_record(record_id, user_id)
                else:
                    return create_response(400, {'error': 'Record ID required for deletion'})
            
            else:
                return create_response(405, {'error': 'Method not allowed'})
        
        # 統計関連のエンドポイント
        elif endpoint == 'stats':
            # 🔐 認証チェック（統計情報も認証が必要）
            current_user = get_current_user_from_event(event)
            if not current_user:
                return create_response(401, {
                    'error': 'Unauthorized', 
                    'message': 'Authentication required to access statistics'
                })
            
            user_id = current_user['user_id']
            
            if len(path_parts) < 4:
                return create_response(404, {'error': 'Stats endpoint not found'})
            
            stats_type = path_parts[3]
            
            if http_method == 'GET':
                if stats_type == 'summary':
                    return get_study_stats_summary(user_id)
                elif stats_type == 'category':
                    return get_category_stats(user_id)
                elif stats_type == 'difficulty':
                    return get_difficulty_stats(user_id)
                else:
                    return create_response(404, {'error': 'Stats type not found'})
            else:
                return create_response(405, {'error': 'Method not allowed'})
        
        # 認証関連のエンドポイント（テスト用簡易実装）
        elif endpoint == 'auth':
            if len(path_parts) < 4:
                return create_response(404, {'error': 'Auth endpoint not found'})
            
            auth_action = path_parts[3]
            
            if auth_action == 'test-login' and http_method == 'POST':
                # テスト用の簡易ログイン（実際はユーザー認証システムと統合）
                return create_test_login_token()
            else:
                return create_response(404, {'error': 'Auth action not found'})
        
        # ヘルスチェックエンドポイント
        elif endpoint == 'health':
            if http_method == 'GET':
                return create_response(200, {
                    'status': 'healthy',
                    'service': 'StudyTracker API',
                    'message': 'セキュリティ強化版（Phase 1）',
                    'database': 'DynamoDB (study-records)',
                    'version': '2.1.0',
                    'security': 'enhanced'
                })
            else:
                return create_response(405, {'error': 'Method not allowed'})
        
        # ドキュメントエンドポイント
        elif endpoint == 'docs':
            if http_method == 'GET':
                return create_response(200, {
                    'message': 'API Documentation',
                    'endpoints': {
                        'health': 'GET /api/v1/health',
                        'records': 'GET /api/v1/study-records',
                        'create': 'POST /api/v1/study-records',
                        'update': 'PUT /api/v1/study-records/{id}',
                        'delete': 'DELETE /api/v1/study-records/{id}',
                        'stats': 'GET /api/v1/stats/summary'
                    }
                })
            else:
                return create_response(405, {'error': 'Method not allowed'})
        
        else:
            return create_response(404, {'error': 'Endpoint not found'})
    
    except Exception as e:
        # エラーログの出力（本番環境では詳細情報を隠す）
        print(f"Error in handler: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """セキュリティ強化レスポンス作成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'https://learninggarden.studio',  # 特定ドメインのみ
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        },
        'body': json.dumps(body, default=str)
    }

def get_paginated_study_records(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """ページネーション付き学習記録一覧取得（セキュリティ強化版）"""
    try:
        # クエリパラメータの取得と検証
        query_params = event.get('queryStringParameters', {}) or {}
        
        # ページ番号の検証
        try:
            page = int(query_params.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # 制限数の検証
        try:
            limit = int(query_params.get('limit', 10))
            if limit < 1 or limit > 50:  # 最大50件に制限
                limit = 10
        except (ValueError, TypeError):
            limit = 10
        
        # DynamoDBからユーザー別レコード取得
        response = table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        all_records = response.get('Items', [])
        
        # 日付順でソート
        all_records.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # ページネーション処理
        total_items = len(all_records)
        total_pages = (total_items + limit - 1) // limit
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        paginated_records = all_records[start_index:end_index]
        
        return create_response(200, {
            'items': paginated_records,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to get records'})

def get_study_records(user_id: str) -> Dict[str, Any]:
    """学習記録一覧取得（セキュリティ強化版）"""
    try:
        response = table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        records = response.get('Items', [])
        
        # 日付順でソート
        records.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return create_response(200, {
            'records': records,
            'count': len(records)
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to get records'})

def create_study_record(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """学習記録作成（セキュリティ強化版）"""
    try:
        # JSON解析のエラーハンドリング
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return create_response(400, {'error': 'Invalid JSON format'})
        
        # 入力値検証
        validation_errors = validate_study_record(body)
        if validation_errors:
            return create_response(400, {
                'error': 'Validation failed',
                'details': validation_errors
            })
        
        # レコード作成（user_idを追加）
        record = {
            'id': str(datetime.now().timestamp()),
            'user_id': user_id,  # ユーザーIDを追加
            'title': body['title'],
            'content': body.get('content', ''),
            'study_time': body.get('study_time', 0),
            'category': body.get('category', ''),
            'difficulty': body.get('difficulty', 1),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        table.put_item(Item=record)
        
        return create_response(201, {
            'message': 'Study record created successfully',
            'record': record
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to create record'})

def get_study_record(record_id: str, user_id: str) -> Dict[str, Any]:
    """学習記録取得（個別・セキュリティ強化版）"""
    try:
        # IDの検証
        if not record_id or not isinstance(record_id, str):
            return create_response(400, {'error': 'Invalid record ID'})
        
        response = table.get_item(Key={'id': record_id})
        record = response.get('Item')
        
        if not record:
            return create_response(404, {'error': 'Record not found'})
        
        # ユーザー権限チェック
        if record.get('user_id') != user_id:
            return create_response(403, {'error': 'Access denied: You can only access your own records'})
        
        return create_response(200, {'record': record})
    except Exception as e:
        return create_response(500, {'error': 'Failed to get record'})

def update_study_record(record_id: str, event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """学習記録更新（セキュリティ強化版）"""
    try:
        # IDの検証
        if not record_id or not isinstance(record_id, str):
            return create_response(400, {'error': 'Invalid record ID'})
        
        # JSON解析のエラーハンドリング
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return create_response(400, {'error': 'Invalid JSON format'})
        
        # 入力値検証
        validation_errors = validate_study_record(body)
        if validation_errors:
            return create_response(400, {
                'error': 'Validation failed',
                'details': validation_errors
            })
        
        # 更新可能なフィールド
        update_fields = ['title', 'content', 'study_time', 'category', 'difficulty']
        update_expression = []
        expression_values = {}
        
        for field in update_fields:
            if field in body:
                update_expression.append(f'#{field} = :{field}')
                expression_values[f':{field}'] = body[field]
        
        if not update_expression:
            return create_response(400, {'error': 'No fields to update'})
        
        # 権限チェック用に現在のレコードを取得
        existing_response = table.get_item(Key={'id': record_id})
        existing_record = existing_response.get('Item')
        
        if not existing_record:
            return create_response(404, {'error': 'Record not found'})
        
        if existing_record.get('user_id') != user_id:
            return create_response(403, {'error': 'Access denied: You can only update your own records'})
        
        # 更新実行
        response = table.update_item(
            Key={'id': record_id},
            UpdateExpression='SET ' + ', '.join(update_expression) + ', updated_at = :updated_at',
            ExpressionAttributeNames={f'#{field}': field for field in update_fields if field in body},
            ExpressionAttributeValues={**expression_values, ':updated_at': datetime.now().isoformat()},
            ReturnValues='ALL_NEW'
        )
        
        return create_response(200, {
            'message': 'Study record updated successfully',
            'record': response.get('Attributes', {})
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to update record'})

def delete_study_record(record_id: str, user_id: str) -> Dict[str, Any]:
    """学習記録削除（セキュリティ強化版）"""
    try:
        # IDの検証
        if not record_id or not isinstance(record_id, str):
            return create_response(400, {'error': 'Invalid record ID'})
        
        # 権限チェック用に現在のレコードを取得
        existing_response = table.get_item(Key={'id': record_id})
        existing_record = existing_response.get('Item')
        
        if not existing_record:
            return create_response(404, {'error': 'Record not found'})
        
        if existing_record.get('user_id') != user_id:
            return create_response(403, {'error': 'Access denied: You can only delete your own records'})
        
        table.delete_item(Key={'id': record_id})
        
        return create_response(200, {
            'message': 'Study record deleted successfully',
            'record_id': record_id
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to delete record'})

def get_study_stats_summary(user_id: str) -> Dict[str, Any]:
    """統計情報サマリー取得（セキュリティ強化版）"""
    try:
        response = table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        records = response.get('Items', [])
        
        if not records:
            return create_response(200, {
                'total_records': 0,
                'total_study_time': 0,
                'average_difficulty': 0,
                'categories': {},
                'difficulties': {}
            })
        
        # 統計計算
        total_records = len(records)
        total_study_time = sum(int(record.get('study_time', 0)) for record in records)
        total_difficulty = sum(int(record.get('difficulty', 1)) for record in records)
        average_difficulty = total_difficulty / total_records if total_records > 0 else 0
        
        # カテゴリ別統計
        categories = {}
        for record in records:
            category = record.get('category', '未分類')
            categories[category] = categories.get(category, 0) + 1
        
        # 難易度別統計
        difficulties = {}
        for record in records:
            difficulty = str(record.get('difficulty', 1))
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        return create_response(200, {
            'total_records': total_records,
            'total_study_time': total_study_time,
            'average_difficulty': round(average_difficulty, 2),
            'categories': categories,
            'difficulties': difficulties
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to get stats'})

def get_category_stats(user_id: str) -> Dict[str, Any]:
    """カテゴリ別統計取得（セキュリティ強化版）"""
    try:
        response = table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        records = response.get('Items', [])
        
        # カテゴリ別統計
        category_stats = {}
        for record in records:
            category = record.get('category', '未分類')
            study_time = int(record.get('study_time', 0))
            difficulty = int(record.get('difficulty', 1))
            
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_time': 0,
                    'total_difficulty': 0
                }
            
            category_stats[category]['count'] += 1
            category_stats[category]['total_time'] += study_time
            category_stats[category]['total_difficulty'] += difficulty
        
        # 平均値計算
        result = []
        for category, stats in category_stats.items():
            avg_difficulty = stats['total_difficulty'] / stats['count'] if stats['count'] > 0 else 0
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            
            result.append({
                'category': category,
                'count': stats['count'],
                'total_time': stats['total_time'],
                'total_hours': round(stats['total_time'] / 60, 2),
                'average_difficulty': round(avg_difficulty, 2),
                'average_time': round(avg_time, 2)
            })
        
        return create_response(200, result)
    except Exception as e:
        return create_response(500, {'error': 'Failed to get category stats'})

def get_difficulty_stats(user_id: str) -> Dict[str, Any]:
    """難易度別統計取得（セキュリティ強化版）"""
    try:
        response = table.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        records = response.get('Items', [])
        
        # 難易度別統計
        difficulty_stats = {}
        for record in records:
            difficulty = int(record.get('difficulty', 1))
            study_time = int(record.get('study_time', 0))
            
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {
                    'count': 0,
                    'total_time': 0
                }
            
            difficulty_stats[difficulty]['count'] += 1
            difficulty_stats[difficulty]['total_time'] += study_time
        
        # 結果フォーマット
        result = []
        for difficulty, stats in difficulty_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            
            result.append({
                'difficulty': difficulty,
                'count': stats['count'],
                'total_time': stats['total_time'],
                'total_hours': round(stats['total_time'] / 60, 2),
                'average_time': round(avg_time, 2)
            })
        
        # 難易度順でソート
        result.sort(key=lambda x: x['difficulty'])
        
        return create_response(200, result)
    except Exception as e:
        return create_response(500, {'error': 'Failed to get difficulty stats'}) 