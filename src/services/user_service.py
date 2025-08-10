"""
ユーザーサービス層
DynamoDBを使用したユーザー管理機能を提供
"""

import boto3
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..models.user import UserCreate, UserUpdate, User, UserResponse
from ..auth.jwt_handler import get_password_hash, verify_password

class UserService:
    """ユーザー管理サービス"""
    
    def __init__(self, endpoint_url: Optional[str] = None):
        """
        ユーザーサービスの初期化
        
        Args:
            endpoint_url: DynamoDBのエンドポイントURL（ローカル開発用）
        """
        if endpoint_url:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        else:
            self.dynamodb = boto3.resource('dynamodb')
        
        self.table = self.dynamodb.Table('users')
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        ユーザーを作成
        
        Args:
            user_data: ユーザー作成データ
            
        Returns:
            作成されたユーザー情報
            
        Raises:
            ValueError: メールアドレスが既に存在する場合
        """
        # メールアドレスの重複チェック
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # ユーザーIDの生成
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # パスワードのハッシュ化
        hashed_password = get_password_hash(user_data.password)
        
        # 現在時刻
        now = datetime.now().isoformat()
        
        # ユーザーデータの作成
        user_item = {
            'id': user_id,
            'email': user_data.email,
            'username': user_data.username,
            'hashed_password': hashed_password,
            'role': user_data.role.value,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        
        # DynamoDBに保存
        self.table.put_item(Item=user_item)
        
        # レスポンス用のユーザーオブジェクトを作成
        return User(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now)
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        IDでユーザーを取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            ユーザー情報（存在しない場合はNone）
        """
        try:
            response = self.table.get_item(Key={'id': user_id})
            item = response.get('Item')
            
            if not item:
                return None
            
            return self._item_to_user(item)
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        メールアドレスでユーザーを取得
        
        Args:
            email: メールアドレス
            
        Returns:
            ユーザー情報（存在しない場合はNone）
        """
        try:
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            items = response.get('Items', [])
            if not items:
                return None
            
            return self._item_to_user(items[0])
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        ユーザー認証
        
        Args:
            email: メールアドレス
            password: パスワード
            
        Returns:
            認証成功時のユーザー情報（失敗時はNone）
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        ユーザー情報を更新
        
        Args:
            user_id: ユーザーID
            user_data: 更新データ
            
        Returns:
            更新されたユーザー情報（失敗時はNone）
        """
        try:
            # 更新可能なフィールド
            update_fields = []
            expression_values = {}
            expression_names = {}
            
            if user_data.username is not None:
                update_fields.append('#username = :username')
                expression_values[':username'] = user_data.username
                expression_names['#username'] = 'username'
            
            if user_data.email is not None:
                # メールアドレスの重複チェック
                existing_user = self.get_user_by_email(user_data.email)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("Email already exists")
                
                update_fields.append('#email = :email')
                expression_values[':email'] = user_data.email
                expression_names['#email'] = 'email'
            
            if user_data.password is not None:
                hashed_password = get_password_hash(user_data.password)
                update_fields.append('#hashed_password = :hashed_password')
                expression_values[':hashed_password'] = hashed_password
                expression_names['#hashed_password'] = 'hashed_password'
            
            if not update_fields:
                return self.get_user_by_id(user_id)
            
            # updated_atフィールドを追加
            now = datetime.now().isoformat()
            update_fields.append('#updated_at = :updated_at')
            expression_values[':updated_at'] = now
            expression_names['#updated_at'] = 'updated_at'
            
            # 更新実行
            response = self.table.update_item(
                Key={'id': user_id},
                UpdateExpression='SET ' + ', '.join(update_fields),
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return self._item_to_user(response['Attributes'])
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """
        ユーザーを削除
        
        Args:
            user_id: ユーザーID
            
        Returns:
            削除成功時はTrue
        """
        try:
            self.table.delete_item(Key={'id': user_id})
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def list_users(self, limit: int = 10, last_key: Optional[str] = None) -> Dict[str, Any]:
        """
        ユーザー一覧を取得
        
        Args:
            limit: 取得件数
            last_key: ページネーション用のキー
            
        Returns:
            ユーザー一覧とページネーション情報
        """
        try:
            scan_kwargs = {
                'Limit': limit
            }
            
            if last_key:
                scan_kwargs['ExclusiveStartKey'] = {'id': last_key}
            
            response = self.table.scan(**scan_kwargs)
            
            users = [self._item_to_user(item) for item in response.get('Items', [])]
            
            return {
                'users': users,
                'count': len(users),
                'last_evaluated_key': response.get('LastEvaluatedKey'),
                'scanned_count': response.get('ScannedCount', 0)
            }
        except Exception as e:
            print(f"Error listing users: {e}")
            return {'users': [], 'count': 0, 'last_evaluated_key': None, 'scanned_count': 0}
    
    def _item_to_user(self, item: Dict[str, Any]) -> User:
        """
        DynamoDBアイテムをUserオブジェクトに変換
        
        Args:
            item: DynamoDBアイテム
            
        Returns:
            Userオブジェクト
        """
        from ..models.user import UserRole
        
        return User(
            id=item['id'],
            email=item['email'],
            username=item['username'],
            hashed_password=item['hashed_password'],
            role=UserRole(item['role']),
            is_active=item['is_active'],
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

