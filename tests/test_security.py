"""
Phase 1 セキュリティ機能のテスト

入力値検証、XSS対策、エラーハンドリング、CORS設定のテスト
"""

import json
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Lambda関数のパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'package'))

from lambda_handler_secure import (
    sanitize_input,
    validate_study_record,
    create_response,
    handler
)

class TestSecurityPhase1:
    """Phase 1 セキュリティ機能のテストクラス"""
    
    def test_sanitize_input_xss_prevention(self):
        """XSS攻撃の防止テスト"""
        # 危険なHTMLタグの除去
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>",
            "<object data='javascript:alert(1)'>",
            "<embed src='javascript:alert(1)'>",
            "javascript:alert('XSS')",
            "onclick=alert('XSS')",
            "onload=alert('XSS')"
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_input(dangerous_input)
            assert "<script>" not in sanitized.lower()
            assert "javascript:" not in sanitized.lower()
            assert "onclick" not in sanitized.lower()
            assert "onload" not in sanitized.lower()
            assert "onerror" not in sanitized.lower()
    
    def test_sanitize_input_length_limit(self):
        """入力値の長さ制限テスト"""
        # 長すぎる文字列の切り詰め
        long_input = "A" * 2000
        sanitized = sanitize_input(long_input, max_length=1000)
        assert len(sanitized) <= 1000
        
        # 正常な長さの文字列
        normal_input = "正常な入力値"
        sanitized = sanitize_input(normal_input, max_length=1000)
        assert sanitized == normal_input
    
    def test_sanitize_input_html_escape(self):
        """HTMLエスケープのテスト"""
        # HTML特殊文字のエスケープ
        test_cases = [
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&#x27;")
        ]
        
        for input_char, expected_escape in test_cases:
            sanitized = sanitize_input(input_char)
            assert expected_escape in sanitized
    
    def test_validate_study_record_title_validation(self):
        """タイトルの検証テスト"""
        # 必須フィールドテスト
        data = {}
        errors = validate_study_record(data)
        assert "title is required" in errors
        
        # 長さ制限テスト
        data = {"title": "A" * 201}
        errors = validate_study_record(data)
        assert "title must be 200 characters or less" in errors
        
        # 正常なタイトル
        data = {"title": "正常なタイトル"}
        errors = validate_study_record(data)
        assert "title is required" not in errors
        assert "title must be 200 characters or less" not in errors
    
    def test_validate_study_record_content_validation(self):
        """コンテンツの検証テスト"""
        # 長さ制限テスト
        data = {"title": "テスト", "content": "A" * 1001}
        errors = validate_study_record(data)
        assert "content must be 1000 characters or less" in errors
        
        # 正常なコンテンツ
        data = {"title": "テスト", "content": "正常なコンテンツ"}
        errors = validate_study_record(data)
        assert "content must be 1000 characters or less" not in errors
    
    def test_validate_study_record_study_time_validation(self):
        """学習時間の検証テスト"""
        # 範囲外の値
        data = {"title": "テスト", "study_time": -1}
        errors = validate_study_record(data)
        assert "study_time must be between 0 and 1440 minutes" in errors
        
        data = {"title": "テスト", "study_time": 1441}
        errors = validate_study_record(data)
        assert "study_time must be between 0 and 1440 minutes" in errors
        
        # 無効な型
        data = {"title": "テスト", "study_time": "invalid"}
        errors = validate_study_record(data)
        assert "study_time must be a valid integer" in errors
        
        # 正常な値
        data = {"title": "テスト", "study_time": 60}
        errors = validate_study_record(data)
        assert "study_time must be between 0 and 1440 minutes" not in errors
        assert "study_time must be a valid integer" not in errors
    
    def test_validate_study_record_difficulty_validation(self):
        """難易度の検証テスト"""
        # 範囲外の値
        data = {"title": "テスト", "difficulty": 0}
        errors = validate_study_record(data)
        assert "difficulty must be between 1 and 5" in errors
        
        data = {"title": "テスト", "difficulty": 6}
        errors = validate_study_record(data)
        assert "difficulty must be between 1 and 5" in errors
        
        # 無効な型
        data = {"title": "テスト", "difficulty": "invalid"}
        errors = validate_study_record(data)
        assert "difficulty must be a valid integer between 1 and 5" in errors
        
        # 正常な値
        data = {"title": "テスト", "difficulty": 3}
        errors = validate_study_record(data)
        assert "difficulty must be between 1 and 5" not in errors
        assert "difficulty must be a valid integer between 1 and 5" not in errors
    
    def test_validate_study_record_category_validation(self):
        """カテゴリの検証テスト"""
        # 長さ制限テスト
        data = {"title": "テスト", "category": "A" * 51}
        errors = validate_study_record(data)
        assert "category must be 50 characters or less" in errors
        
        # 正常なカテゴリ
        data = {"title": "テスト", "category": "プログラミング"}
        errors = validate_study_record(data)
        assert "category must be 50 characters or less" not in errors
    
    def test_create_response_security_headers(self):
        """セキュリティヘッダーのテスト"""
        response = create_response(200, {"message": "test"})
        headers = response['headers']
        
        # セキュリティヘッダーの確認
        assert headers['X-Content-Type-Options'] == 'nosniff'
        assert headers['X-Frame-Options'] == 'DENY'
        assert headers['X-XSS-Protection'] == '1; mode=block'
        assert headers['Strict-Transport-Security'] == 'max-age=31536000; includeSubDomains'
        
        # CORS設定の確認
        assert headers['Access-Control-Allow-Origin'] == 'https://learninggarden.studio'
        assert '*' not in headers['Access-Control-Allow-Origin']
    
    def test_handler_error_information_leak_prevention(self):
        """エラー情報漏洩防止のテスト"""
        # 例外が発生した場合のエラーメッセージ
        with patch('lambda_handler_secure.table') as mock_table:
            mock_table.scan.side_effect = Exception("Internal database error")
            
            event = {
                'path': '/api/v1/study-records',
                'httpMethod': 'GET'
            }
            
            response = handler(event, {})
            body = json.loads(response['body'])
            
            # 内部エラー情報が漏洩していないことを確認
            assert "Internal database error" not in body['error']
            # エラーメッセージが安全であることを確認
            assert body['error'] in ['Failed to get records', 'Internal server error']
            # messageフィールドは存在しない場合がある
            if 'message' in body:
                assert "Internal database error" not in body['message']
    
    def test_handler_json_decode_error_handling(self):
        """JSON解析エラーの処理テスト"""
        event = {
            'path': '/api/v1/study-records',
            'httpMethod': 'POST',
            'body': 'invalid json'
        }
        
        response = handler(event, {})
        body = json.loads(response['body'])
        
        assert response['statusCode'] == 400
        assert body['error'] == 'Invalid JSON format'
    
    def test_handler_validation_error_handling(self):
        """入力値検証エラーの処理テスト"""
        event = {
            'path': '/api/v1/study-records',
            'httpMethod': 'POST',
            'body': json.dumps({
                'title': '',  # 空のタイトル
                'study_time': 'invalid'  # 無効な学習時間
            })
        }
        
        response = handler(event, {})
        body = json.loads(response['body'])
        
        assert response['statusCode'] == 400
        assert body['error'] == 'Validation failed'
        assert 'title is required' in body['details']
        assert 'study_time must be a valid integer' in body['details']
    
    def test_handler_xss_prevention_in_data(self):
        """データ保存時のXSS防止テスト"""
        event = {
            'path': '/api/v1/study-records',
            'httpMethod': 'POST',
            'body': json.dumps({
                'title': '<script>alert("XSS")</script>',
                'content': '<img src=x onerror=alert("XSS")>',
                'category': 'javascript:alert("XSS")'
            })
        }
        
        with patch('lambda_handler_secure.table') as mock_table:
            response = handler(event, {})
            body = json.loads(response['body'])
            
            # 成功レスポンスを確認
            assert response['statusCode'] == 201
            
            # 保存されたデータがサニタイズされていることを確認
            saved_record = body['record']
            assert '<script>' not in saved_record['title']
            assert 'javascript:' not in saved_record['category']
            assert 'onerror' not in saved_record['content']
    
    def test_handler_query_parameter_validation(self):
        """クエリパラメータの検証テスト"""
        # 無効なページ番号
        event = {
            'path': '/api/v1/study-records/paginated',
            'httpMethod': 'GET',
            'queryStringParameters': {
                'page': 'invalid',
                'limit': 'invalid'
            }
        }
        
        with patch('lambda_handler_secure.table') as mock_table:
            mock_table.scan.return_value = {'Items': []}
            response = handler(event, {})
            body = json.loads(response['body'])
            
            # デフォルト値が使用されることを確認
            pagination = body['pagination']
            assert pagination['page'] == 1
            assert pagination['limit'] == 10
        
        # 範囲外の制限数
        event = {
            'path': '/api/v1/study-records/paginated',
            'httpMethod': 'GET',
            'queryStringParameters': {
                'limit': '1000'  # 最大50件を超える
            }
        }
        
        with patch('lambda_handler_secure.table') as mock_table:
            mock_table.scan.return_value = {'Items': []}
            response = handler(event, {})
            body = json.loads(response['body'])
            
            # 最大値に制限されることを確認
            pagination = body['pagination']
            assert pagination['limit'] <= 50  # 50以下であることを確認

if __name__ == "__main__":
    pytest.main([__file__]) 