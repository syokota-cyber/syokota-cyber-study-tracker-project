"""
CLI機能のテスト

コマンドラインインターフェースの各機能をテストします。
"""

import pytest
import tempfile
import os
import json
import csv
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.cli.main import (
    handle_add, handle_list, handle_show, handle_update, 
    handle_delete, handle_stats, handle_search, handle_export,
    filter_records
)
from src.database.connection import DatabaseManager
from src.models.study_record import StudyRecord


class TestCLI:
    """CLI機能のテストクラス"""
    
    @pytest.fixture
    def db_manager(self):
        """テスト用データベースマネージャー"""
        # 一時的なSQLiteファイルを使用
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = DatabaseManager(db_path)
        db.init_database()
        yield db
        
        # テスト後にファイルを削除
        os.unlink(db_path)
    
    @pytest.fixture
    def sample_records(self):
        """テスト用サンプルデータ"""
        return [
            StudyRecord(
                title="Python基礎",
                content="変数と関数の学習",
                study_time=60,
                category="プログラミング",
                difficulty=1
            ),
            StudyRecord(
                title="Vue.js学習",
                content="コンポーネントの作成",
                study_time=90,
                category="フロントエンド",
                difficulty=2
            ),
            StudyRecord(
                title="Git基礎",
                content="コミットとブランチ",
                study_time=45,
                category="ツール",
                difficulty=1
            )
        ]
    
    def test_handle_add(self, db_manager):
        """学習記録追加のテスト"""
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.title = "テスト学習"
        args.content = "テスト内容"
        args.time = 30
        args.category = "テスト"
        args.difficulty = 2
        
        # 実行
        handle_add(db_manager, args)
        
        # 検証
        records = db_manager.get_all_study_records()
        assert len(records) == 1
        assert records[0].title == "テスト学習"
        assert records[0].study_time == 30
    
    def test_handle_list(self, db_manager, sample_records):
        """学習記録一覧表示のテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.limit = 10
        args.category = None
        args.difficulty = None
        args.min_time = None
        args.max_time = None
        args.search = None
        args.days = None
        
        # 実行
        handle_list(db_manager, args)
        
        # 検証（出力は標準出力に表示されるため、例外が発生しないことを確認）
        records = db_manager.get_all_study_records()
        assert len(records) == 3
    
    def test_handle_show(self, db_manager, sample_records):
        """学習記録詳細表示のテスト"""
        # テストデータを追加
        record_id = db_manager.add_study_record(sample_records[0])
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.id = record_id
        
        # 実行
        handle_show(db_manager, args)
        
        # 検証（例外が発生しないことを確認）
        record = db_manager.get_study_record(record_id)
        assert record is not None
    
    def test_handle_update(self, db_manager, sample_records):
        """学習記録更新のテスト"""
        # テストデータを追加
        record_id = db_manager.add_study_record(sample_records[0])
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.id = record_id
        args.title = "更新されたタイトル"
        args.content = None
        args.time = 120
        args.category = None
        args.difficulty = None
        
        # 実行
        handle_update(db_manager, args)
        
        # 検証
        record = db_manager.get_study_record(record_id)
        assert record.title == "更新されたタイトル"
        assert record.study_time == 120
    
    def test_handle_delete(self, db_manager, sample_records):
        """学習記録削除のテスト"""
        # テストデータを追加
        record_id = db_manager.add_study_record(sample_records[0])
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.id = record_id
        
        # 実行
        handle_delete(db_manager, args)
        
        # 検証
        record = db_manager.get_study_record(record_id)
        assert record is None
    
    def test_handle_stats(self, db_manager, sample_records):
        """統計情報表示のテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.category = False
        args.difficulty = False
        args.period = 'all'
        
        # 実行
        handle_stats(db_manager, args)
        
        # 検証（例外が発生しないことを確認）
        records = db_manager.get_all_study_records()
        assert len(records) == 3
    
    def test_handle_search(self, db_manager, sample_records):
        """検索機能のテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # モックのargsオブジェクトを作成
        args = MagicMock()
        args.keyword = "Python"
        args.title_only = False
        args.content_only = False
        args.case_sensitive = False
        args.limit = 10
        
        # 実行
        handle_search(db_manager, args)
        
        # 検証（例外が発生しないことを確認）
        records = db_manager.get_all_study_records()
        assert len(records) == 3
    
    def test_filter_records_category(self, sample_records):
        """カテゴリフィルタリングのテスト"""
        args = MagicMock()
        args.category = "プログラミング"
        args.difficulty = None
        args.min_time = None
        args.max_time = None
        args.search = None
        args.days = None
        
        filtered = filter_records(sample_records, args)
        assert len(filtered) == 1
        assert filtered[0].title == "Python基礎"
    
    def test_filter_records_difficulty(self, sample_records):
        """難易度フィルタリングのテスト"""
        args = MagicMock()
        args.category = None
        args.difficulty = 2
        args.min_time = None
        args.max_time = None
        args.search = None
        args.days = None
        
        filtered = filter_records(sample_records, args)
        assert len(filtered) == 1
        assert filtered[0].title == "Vue.js学習"
    
    def test_filter_records_time(self, sample_records):
        """学習時間フィルタリングのテスト"""
        args = MagicMock()
        args.category = None
        args.difficulty = None
        args.min_time = 60
        args.max_time = None
        args.search = None
        args.days = None
        
        filtered = filter_records(sample_records, args)
        assert len(filtered) == 2  # 60分以上は2件
    
    def test_filter_records_days(self, sample_records):
        """期間フィルタリングのテスト"""
        # 古いレコードを作成
        old_record = StudyRecord(
            title="古い学習",
            study_time=30,
            category="テスト"
        )
        old_record.created_at = datetime.now() - timedelta(days=10)
        
        all_records = sample_records + [old_record]
        
        args = MagicMock()
        args.category = None
        args.difficulty = None
        args.min_time = None
        args.max_time = None
        args.search = None
        args.days = 7
        
        filtered = filter_records(all_records, args)
        assert len(filtered) == 3  # 過去7日間は3件
    
    def test_handle_export_csv(self, db_manager, sample_records):
        """CSVエクスポートのテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            filename = tmp.name
        
        try:
            # モックのargsオブジェクトを作成
            args = MagicMock()
            args.format = 'csv'
            args.output = filename
            args.all_fields = False
            args.category = None
            args.difficulty = None
            args.min_time = None
            args.max_time = None
            args.search = None
            args.days = None
            
            # 実行
            handle_export(db_manager, args)
            
            # 検証
            assert os.path.exists(filename)
            
            # CSVファイルの内容を確認
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 3
                assert rows[0]['タイトル'] == "Python基礎"
        
        finally:
            # 一時ファイルを削除
            os.unlink(filename)
    
    def test_handle_export_json(self, db_manager, sample_records):
        """JSONエクスポートのテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            filename = tmp.name
        
        try:
            # モックのargsオブジェクトを作成
            args = MagicMock()
            args.format = 'json'
            args.output = filename
            args.all_fields = True
            args.category = None
            args.difficulty = None
            args.min_time = None
            args.max_time = None
            args.search = None
            args.days = None
            
            # 実行
            handle_export(db_manager, args)
            
            # 検証
            assert os.path.exists(filename)
            
            # JSONファイルの内容を確認
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert len(data) == 3
                assert data[0]['title'] == "Python基礎"
                assert 'content' in data[0]  # all_fields=Trueの場合
        
        finally:
            # 一時ファイルを削除
            os.unlink(filename)
    
    def test_handle_export_txt(self, db_manager, sample_records):
        """テキストエクスポートのテスト"""
        # テストデータを追加
        for record in sample_records:
            db_manager.add_study_record(record)
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            filename = tmp.name
        
        try:
            # モックのargsオブジェクトを作成
            args = MagicMock()
            args.format = 'txt'
            args.output = filename
            args.all_fields = False
            args.category = None
            args.difficulty = None
            args.min_time = None
            args.max_time = None
            args.search = None
            args.days = None
            
            # 実行
            handle_export(db_manager, args)
            
            # 検証
            assert os.path.exists(filename)
            
            # テキストファイルの内容を確認
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "StudyTracker" in content
                assert "Python基礎" in content
        
        finally:
            # 一時ファイルを削除
            os.unlink(filename)


if __name__ == "__main__":
    pytest.main([__file__]) 