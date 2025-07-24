"""
StudyRecordモデルのテスト

データモデルの動作を検証するテストスイートです。
"""

import pytest
from datetime import datetime

from src.models.study_record import StudyRecord


class TestStudyRecord:
    """StudyRecordクラスのテストクラス"""
    
    def test_study_record_creation(self):
        """学習記録の作成テスト"""
        record = StudyRecord(
            title="Python学習",
            content="FastAPIの基礎を学んだ",
            study_time=60,
            category="プログラミング",
            difficulty=3
        )
        
        assert record.title == "Python学習"
        assert record.content == "FastAPIの基礎を学んだ"
        assert record.study_time == 60
        assert record.category == "プログラミング"
        assert record.difficulty == 3
        assert record.id is None  # 新規作成時はIDなし
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)
    
    def test_study_record_minimal_creation(self):
        """最小限の情報での学習記録作成テスト"""
        record = StudyRecord(title="テスト学習")
        
        assert record.title == "テスト学習"
        assert record.content is None
        assert record.study_time == 0
        assert record.category is None
        assert record.difficulty == 1  # デフォルト値
    
    def test_difficulty_range_validation(self):
        """難易度の範囲検証テスト"""
        # 最小値（1）のテスト
        record1 = StudyRecord(title="テスト", difficulty=1)
        assert record1.difficulty == 1
        
        # 最大値（5）のテスト
        record5 = StudyRecord(title="テスト", difficulty=5)
        assert record5.difficulty == 5
        
        # 範囲外の値は自動調整される
        record0 = StudyRecord(title="テスト", difficulty=0)
        assert record0.difficulty == 1  # 最小値に調整
        
        record6 = StudyRecord(title="テスト", difficulty=6)
        assert record6.difficulty == 5  # 最大値に調整
    
    def test_get_study_hours(self):
        """学習時間の時間単位変換テスト"""
        # 60分 = 1時間
        record1 = StudyRecord(title="テスト", study_time=60)
        assert record1.get_study_hours() == 1.0
        
        # 30分 = 0.5時間
        record2 = StudyRecord(title="テスト", study_time=30)
        assert record2.get_study_hours() == 0.5
        
        # 90分 = 1.5時間
        record3 = StudyRecord(title="テスト", study_time=90)
        assert record3.get_study_hours() == 1.5
        
        # 0分 = 0時間
        record4 = StudyRecord(title="テスト", study_time=0)
        assert record4.get_study_hours() == 0.0
    
    def test_update_method(self):
        """更新メソッドのテスト"""
        record = StudyRecord(
            title="元のタイトル",
            content="元の内容",
            study_time=30,
            category="元のカテゴリ",
            difficulty=2
        )
        
        original_updated_at = record.updated_at
        
        # 更新を実行
        record.update(
            title="新しいタイトル",
            study_time=60,
            difficulty=4
        )
        
        # 更新されたフィールドの確認
        assert record.title == "新しいタイトル"
        assert record.content == "元の内容"  # 変更されていない
        assert record.study_time == 60
        assert record.category == "元のカテゴリ"  # 変更されていない
        assert record.difficulty == 4
        
        # updated_atが更新されていることを確認
        assert record.updated_at > original_updated_at
    
    def test_update_with_invalid_field(self):
        """無効なフィールドでの更新テスト"""
        record = StudyRecord(title="テスト")
        original_title = record.title
        
        # 存在しないフィールドで更新を試行
        record.update(invalid_field="無効な値")
        
        # 元の値が保持されていることを確認
        assert record.title == original_title
        assert not hasattr(record, 'invalid_field')
    
    def test_string_representation(self):
        """文字列表現のテスト"""
        record = StudyRecord(
            title="テスト学習",
            study_time=45,
            id=1
        )
        
        expected_str = "StudyRecord(id=1, title='テスト学習', time=45分)"
        assert str(record) == expected_str
        assert repr(record) == expected_str
    
    def test_record_with_id(self):
        """ID付きレコードの作成テスト"""
        record = StudyRecord(
            title="テスト",
            id=123
        )
        
        assert record.id == 123
        assert str(record) == "StudyRecord(id=123, title='テスト', time=0分)"


class TestStudyRecordEdgeCases:
    """StudyRecordのエッジケーステスト"""
    
    def test_empty_title(self):
        """空のタイトルでの作成テスト"""
        record = StudyRecord(title="")
        assert record.title == ""
    
    def test_very_long_title(self):
        """非常に長いタイトルでの作成テスト"""
        long_title = "a" * 1000
        record = StudyRecord(title=long_title)
        assert record.title == long_title
    
    def test_negative_study_time(self):
        """負の学習時間での作成テスト"""
        record = StudyRecord(title="テスト", study_time=-10)
        assert record.study_time == -10  # 負の値も許可
    
    def test_very_large_study_time(self):
        """非常に大きな学習時間での作成テスト"""
        record = StudyRecord(title="テスト", study_time=999999)
        assert record.study_time == 999999
        assert record.get_study_hours() == 16666.65  # 約16666時間