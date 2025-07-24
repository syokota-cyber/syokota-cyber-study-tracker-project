"""
学習記録データモデル

学習の進捗、内容、時間などを管理するためのデータモデルです。
"""

from datetime import datetime
from typing import Optional


class StudyRecord:
    """
    学習記録クラス
    
    学習のタイトル、内容、時間、カテゴリ、難易度などを管理します。
    """
    
    def __init__(
        self,
        title: str,
        content: Optional[str] = None,
        study_time: int = 0,
        category: Optional[str] = None,
        difficulty: int = 1,
        id: Optional[int] = None
    ):
        """
        学習記録を初期化
        
        Args:
            title: 学習タイトル
            content: 学習内容（オプション）
            study_time: 学習時間（分）
            category: カテゴリ（オプション）
            difficulty: 難易度（1-5）
            id: レコードID（オプション）
        """
        self.id = id
        self.title = title
        self.content = content
        self.study_time = study_time
        self.category = category
        self.difficulty = max(1, min(5, difficulty))  # 1-5の範囲に制限
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_study_hours(self) -> float:
        """学習時間を時間単位で取得"""
        return self.study_time / 60
    
    def update(self, **kwargs):
        """学習記録を更新"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"StudyRecord(id={self.id}, title='{self.title}', time={self.study_time}分)"
    
    def __repr__(self) -> str:
        return self.__str__()