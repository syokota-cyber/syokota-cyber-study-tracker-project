import json
import boto3
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('study-records')

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

def handler(event, context):
    """StudyTracker API - セキュリティ強化版（Phase 1）"""
    try:
        # パスパラメータの取得
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'GET')
        
        # ヘルスチェックエンドポイント
        if path == '/health' or path.endswith('/health'):
            return create_response(200, {
                'status': 'healthy',
                'service': 'StudyTracker API',
                'message': 'セキュリティ強化版（Phase 1）',
                'database': 'DynamoDB (study-records)',
                'version': '2.1.0',
                'security': 'enhanced'
            })
        
        # 統計情報エンドポイント（個別レコード取得より前に配置）
        elif path == '/api/v1/study-records/stats/summary' and http_method == 'GET':
            return get_study_stats_summary()
        
        elif path == '/api/v1/study-records/stats/category' and http_method == 'GET':
            return get_category_stats()
        
        elif path == '/api/v1/study-records/stats/difficulty' and http_method == 'GET':
            return get_difficulty_stats()
        
        # ページネーション付き学習記録一覧取得
        elif path == '/api/v1/study-records/paginated' and http_method == 'GET':
            return get_paginated_study_records(event)
        
        # 学習記録一覧取得（従来版）
        elif path == '/api/v1/study-records' and http_method == 'GET':
            return get_study_records()
        
        # 学習記録作成
        elif path == '/api/v1/study-records' and http_method == 'POST':
            return create_study_record(event)
        
        # 学習記録取得（個別）
        elif path.startswith('/api/v1/study-records/') and http_method == 'GET':
            record_id = path.split('/')[-1]
            return get_study_record(record_id)
        
        # 学習記録更新
        elif path.startswith('/api/v1/study-records/') and http_method == 'PUT':
            record_id = path.split('/')[-1]
            return update_study_record(record_id, event)
        
        # 学習記録削除
        elif path.startswith('/api/v1/study-records/') and http_method == 'DELETE':
            record_id = path.split('/')[-1]
            return delete_study_record(record_id)
        
        # ルートエンドポイント
        elif path == '/' or path == '/api/v1':
            return create_response(200, {
                'message': 'StudyTracker API',
                'version': '2.1.0',
                'status': 'ready',
                'database': 'DynamoDB',
                'security': 'enhanced',
                'endpoints': {
                    'health': '/health',
                    'study_records': '/api/v1/study-records',
                    'study_records_paginated': '/api/v1/study-records/paginated',
                    'study_stats_summary': '/api/v1/study-records/stats/summary',
                    'study_stats_category': '/api/v1/study-records/stats/category',
                    'study_stats_difficulty': '/api/v1/study-records/stats/difficulty',
                    'api': '/api/v1'
                }
            })
        
        # その他のエンドポイント
        else:
            return create_response(404, {
                'error': 'Not Found',
                'message': 'Endpoint not found'
            })
            
    except Exception as e:
        # エラーメッセージの情報漏洩を防ぐ
        return create_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })

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

def get_paginated_study_records(event: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # DynamoDBから全レコード取得
        response = table.scan()
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

def get_study_records() -> Dict[str, Any]:
    """学習記録一覧取得（セキュリティ強化版）"""
    try:
        response = table.scan()
        records = response.get('Items', [])
        
        # 日付順でソート
        records.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return create_response(200, {
            'records': records,
            'count': len(records)
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to get records'})

def create_study_record(event: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # レコード作成
        record = {
            'id': str(datetime.now().timestamp()),
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

def get_study_record(record_id: str) -> Dict[str, Any]:
    """学習記録取得（個別・セキュリティ強化版）"""
    try:
        # IDの検証
        if not record_id or not isinstance(record_id, str):
            return create_response(400, {'error': 'Invalid record ID'})
        
        response = table.get_item(Key={'id': record_id})
        record = response.get('Item')
        
        if not record:
            return create_response(404, {'error': 'Record not found'})
        
        return create_response(200, {'record': record})
    except Exception as e:
        return create_response(500, {'error': 'Failed to get record'})

def update_study_record(record_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
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

def delete_study_record(record_id: str) -> Dict[str, Any]:
    """学習記録削除（セキュリティ強化版）"""
    try:
        # IDの検証
        if not record_id or not isinstance(record_id, str):
            return create_response(400, {'error': 'Invalid record ID'})
        
        table.delete_item(Key={'id': record_id})
        
        return create_response(200, {
            'message': 'Study record deleted successfully',
            'record_id': record_id
        })
    except Exception as e:
        return create_response(500, {'error': 'Failed to delete record'})

def get_study_stats_summary() -> Dict[str, Any]:
    """統計情報サマリー取得（セキュリティ強化版）"""
    try:
        response = table.scan()
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

def get_category_stats() -> Dict[str, Any]:
    """カテゴリ別統計取得（セキュリティ強化版）"""
    try:
        response = table.scan()
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

def get_difficulty_stats() -> Dict[str, Any]:
    """難易度別統計取得（セキュリティ強化版）"""
    try:
        response = table.scan()
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