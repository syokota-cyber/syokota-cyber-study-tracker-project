import json
import boto3
from datetime import datetime
from typing import Dict, Any, List, Optional

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('study-records')

def handler(event, context):
    """StudyTracker API - DynamoDB対応版"""
    try:
        # パスパラメータの取得
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'GET')
        
        # ヘルスチェックエンドポイント
        if path == '/health' or path.endswith('/health'):
            return create_response(200, {
                'status': 'healthy',
                'service': 'StudyTracker API',
                'message': 'DynamoDB対応版',
                'database': 'DynamoDB (study-records)'
            })
        
        # 学習記録一覧取得
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
                'version': '1.0.0',
                'status': 'ready',
                'database': 'DynamoDB',
                'endpoints': {
                    'health': '/health',
                    'study_records': '/api/v1/study-records',
                    'api': '/api/v1'
                }
            })
        
        # その他のエンドポイント
        else:
            return create_response(404, {
                'error': 'Not Found',
                'message': f'Endpoint {path} not found',
                'available_endpoints': [
                    '/health', 
                    '/api/v1/study-records',
                    '/api/v1'
                ]
            })
            
    except Exception as e:
        return create_response(500, {
            'error': str(e),
            'message': 'Internal server error'
        })

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """標準レスポンス作成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }

def get_study_records() -> Dict[str, Any]:
    """学習記録一覧取得"""
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
        return create_response(500, {'error': f'Failed to get records: {str(e)}'})

def create_study_record(event: Dict[str, Any]) -> Dict[str, Any]:
    """学習記録作成"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # 必須フィールドの確認
        if 'title' not in body:
            return create_response(400, {'error': 'title is required'})
        
        # レコード作成
        record = {
            'id': str(datetime.now().timestamp()),  # 簡易ID生成
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
        return create_response(500, {'error': f'Failed to create record: {str(e)}'})

def get_study_record(record_id: str) -> Dict[str, Any]:
    """学習記録取得（個別）"""
    try:
        response = table.get_item(Key={'id': record_id})
        record = response.get('Item')
        
        if not record:
            return create_response(404, {'error': 'Record not found'})
        
        return create_response(200, {'record': record})
    except Exception as e:
        return create_response(500, {'error': f'Failed to get record: {str(e)}'})

def update_study_record(record_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """学習記録更新"""
    try:
        body = json.loads(event.get('body', '{}'))
        
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
        return create_response(500, {'error': f'Failed to update record: {str(e)}'})

def delete_study_record(record_id: str) -> Dict[str, Any]:
    """学習記録削除"""
    try:
        table.delete_item(Key={'id': record_id})
        
        return create_response(200, {
            'message': 'Study record deleted successfully',
            'record_id': record_id
        })
    except Exception as e:
        return create_response(500, {'error': f'Failed to delete record: {str(e)}'})
