"""
CLI機能のテスト
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime, timedelta

# CLIモジュールをインポート
from src.cli.main import (
    main,
    handle_add,
    handle_list,
    handle_show,
    handle_update,
    handle_delete,
    handle_stats,
    handle_search,
    handle_export,
    filter_records,
    export_to_csv,
    export_to_json,
    export_to_txt,
)
from src.models.study_record import StudyRecord
from src.database.connection import DatabaseManager


class TestCLICommands:
    """CLIコマンドのテスト"""

    @pytest.fixture
    def mock_db(self):
        """モックデータベース"""
        db = MagicMock(spec=DatabaseManager)
        return db

    @pytest.fixture
    def sample_records(self):
        """サンプル学習記録"""
        records = [
            StudyRecord(
                id=1,
                title="Python学習",
                content="FastAPIの基礎",
                study_time=60,
                category="プログラミング",
                difficulty=3,
            ),
            StudyRecord(
                id=2,
                title="Git学習",
                content="Git Flow",
                study_time=90,
                category="バックエンド",
                difficulty=2,
            ),
        ]
        # 手動で日時を設定
        records[0].created_at = datetime.now() - timedelta(days=1)
        records[0].updated_at = datetime.now()
        records[1].created_at = datetime.now()
        records[1].updated_at = datetime.now()
        return records

    def test_handle_add(self, mock_db):
        """学習記録追加のテスト"""
        # モック引数
        args = MagicMock()
        args.title = "テスト学習"
        args.content = "テスト内容"
        args.time = 45
        args.category = "テスト"
        args.difficulty = 4

        # モックデータベースの設定
        mock_db.add_study_record.return_value = 1

        # 標準出力をキャプチャ
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_add(mock_db, args)
            output = mock_stdout.getvalue()

        # 検証
        assert "✅ 学習記録を追加しました" in output
        assert "ID: 1" in output
        assert "タイトル: テスト学習" in output
        mock_db.add_study_record.assert_called_once()

    def test_handle_list_empty(self, mock_db):
        """空の学習記録一覧のテスト"""
        mock_db.get_all_study_records.return_value = []

        args = MagicMock()
        args.limit = 10

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_list(mock_db, args)
            output = mock_stdout.getvalue()

        assert "📝 学習記録がありません" in output

    def test_handle_list_with_records(self, mock_db, sample_records):
        """学習記録一覧のテスト"""
        mock_db.get_all_study_records.return_value = sample_records

        args = MagicMock()
        args.limit = 10
        args.category = None
        args.difficulty = None
        args.min_time = None
        args.max_time = None
        args.search = None
        args.days = None

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_list(mock_db, args)
            output = mock_stdout.getvalue()

        assert "📚 学習記録一覧" in output
        assert "Python学習" in output
        assert "Git学習" in output

    def test_handle_show_found(self, mock_db, sample_records):
        """学習記録詳細表示のテスト（存在する場合）"""
        mock_db.get_study_record.return_value = sample_records[0]

        args = MagicMock()
        args.id = 1

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_show(mock_db, args)
            output = mock_stdout.getvalue()

        assert "📖 学習記録詳細" in output
        assert "Python学習" in output
        assert "60分" in output

    def test_handle_show_not_found(self, mock_db):
        """学習記録詳細表示のテスト（存在しない場合）"""
        mock_db.get_study_record.return_value = None

        args = MagicMock()
        args.id = 999

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_show(mock_db, args)
            output = mock_stdout.getvalue()

        assert "❌ ID 999 の学習記録が見つかりません" in output

    def test_handle_update_success(self, mock_db):
        """学習記録更新のテスト（成功）"""
        mock_db.update_study_record.return_value = True

        args = MagicMock()
        args.id = 1
        args.title = "更新されたタイトル"
        args.content = None
        args.time = None
        args.category = None
        args.difficulty = None

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_update(mock_db, args)
            output = mock_stdout.getvalue()

        assert "✅ 学習記録 (ID: 1) を更新しました" in output
        mock_db.update_study_record.assert_called_once_with(
            1, title="更新されたタイトル"
        )

    def test_handle_update_no_fields(self, mock_db):
        """学習記録更新のテスト（フィールド未指定）"""
        args = MagicMock()
        args.id = 1
        args.title = None
        args.content = None
        args.time = None
        args.category = None
        args.difficulty = None

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_update(mock_db, args)
            output = mock_stdout.getvalue()

        assert "❌ 更新するフィールドが指定されていません" in output

    def test_handle_delete_success(self, mock_db):
        """学習記録削除のテスト（成功）"""
        mock_db.delete_study_record.return_value = True

        args = MagicMock()
        args.id = 1

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_delete(mock_db, args)
            output = mock_stdout.getvalue()

        assert "✅ 学習記録 (ID: 1) を削除しました" in output

    def test_handle_delete_failure(self, mock_db):
        """学習記録削除のテスト（失敗）"""
        mock_db.delete_study_record.return_value = False

        args = MagicMock()
        args.id = 999

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_delete(mock_db, args)
            output = mock_stdout.getvalue()

        assert "❌ 学習記録 (ID: 999) の削除に失敗しました" in output

    def test_handle_stats_empty(self, mock_db):
        """統計情報のテスト（空の場合）"""
        mock_db.get_all_study_records.return_value = []

        args = MagicMock()
        args.category = False
        args.difficulty = False
        args.period = "all"

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_stats(mock_db, args)
            output = mock_stdout.getvalue()

        assert "📊 学習統計" in output
        assert "学習記録がありません" in output

    def test_handle_stats_with_records(self, mock_db, sample_records):
        """統計情報のテスト（記録がある場合）"""
        mock_db.get_all_study_records.return_value = sample_records

        args = MagicMock()
        args.category = False
        args.difficulty = False
        args.period = "all"

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_stats(mock_db, args)
            output = mock_stdout.getvalue()

        assert "📊 学習統計サマリー" in output
        assert "総学習記録数: 2件" in output
        assert "総学習時間: 150分" in output

    def test_handle_search_found(self, mock_db, sample_records):
        """検索のテスト（結果あり）"""
        mock_db.get_all_study_records.return_value = sample_records

        args = MagicMock()
        args.keyword = "Python"
        args.title_only = False
        args.content_only = False
        args.case_sensitive = False
        args.limit = 10

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_search(mock_db, args)
            output = mock_stdout.getvalue()

        assert "🔍 検索結果: 'Python'" in output
        assert "Python学習" in output

    def test_handle_search_not_found(self, mock_db, sample_records):
        """検索のテスト（結果なし）"""
        mock_db.get_all_study_records.return_value = sample_records

        args = MagicMock()
        args.keyword = "存在しないキーワード"
        args.title_only = False
        args.content_only = False
        args.case_sensitive = False
        args.limit = 10

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            handle_search(mock_db, args)
            output = mock_stdout.getvalue()

        assert (
            "🔍 キーワード '存在しないキーワード' に一致する学習記録がありません"
            in output
        )


class TestFilterRecords:
    """フィルタリング機能のテスト"""

    @pytest.fixture
    def sample_records(self):
        """サンプル学習記録"""
        records = [
            StudyRecord(
                id=1,
                title="Python学習",
                content="FastAPIの基礎",
                study_time=60,
                category="プログラミング",
                difficulty=3,
            ),
            StudyRecord(
                id=2,
                title="Git学習",
                content="Git Flow",
                study_time=90,
                category="バックエンド",
                difficulty=2,
            ),
        ]
        # 手動で日時を設定
        records[0].created_at = datetime.now()
        records[0].updated_at = datetime.now()
        records[1].created_at = datetime.now()
        records[1].updated_at = datetime.now()
        return records

    def test_filter_by_category(self, sample_records):
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
        assert filtered[0].category == "プログラミング"

    def test_filter_by_difficulty(self, sample_records):
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
        assert filtered[0].difficulty == 2

    def test_filter_by_time_range(self, sample_records):
        """時間範囲フィルタリングのテスト"""
        args = MagicMock()
        args.category = None
        args.difficulty = None
        args.min_time = 70
        args.max_time = 100
        args.search = None
        args.days = None

        filtered = filter_records(sample_records, args)
        assert len(filtered) == 1
        assert filtered[0].study_time == 90

    def test_filter_by_search(self, sample_records):
        """検索フィルタリングのテスト"""
        args = MagicMock()
        args.category = None
        args.difficulty = None
        args.min_time = None
        args.max_time = None
        args.search = "Python"
        args.days = None

        filtered = filter_records(sample_records, args)
        assert len(filtered) == 1
        assert "Python" in filtered[0].title


class TestExportFunctions:
    """エクスポート機能のテスト"""

    @pytest.fixture
    def sample_records(self):
        """サンプル学習記録"""
        record = StudyRecord(
            id=1,
            title="テスト学習",
            content="テスト内容",
            study_time=60,
            category="テスト",
            difficulty=3,
        )
        # 手動で日時を設定
        record.created_at = datetime.now()
        record.updated_at = datetime.now()
        return [record]

    def test_export_to_csv(self, sample_records, tmp_path):
        """CSVエクスポートのテスト"""
        filename = tmp_path / "test.csv"
        export_to_csv(sample_records, str(filename), all_fields=False)

        assert filename.exists()
        content = filename.read_text(encoding="utf-8")
        assert "ID,タイトル,学習時間(分),カテゴリ,難易度,作成日" in content
        assert "テスト学習" in content

    def test_export_to_json(self, sample_records, tmp_path):
        """JSONエクスポートのテスト"""
        filename = tmp_path / "test.json"
        export_to_json(sample_records, str(filename), all_fields=False)

        assert filename.exists()
        content = filename.read_text(encoding="utf-8")
        assert '"title": "テスト学習"' in content
        assert '"study_time_minutes": 60' in content

    def test_export_to_txt(self, sample_records, tmp_path):
        """テキストエクスポートのテスト"""
        filename = tmp_path / "test.txt"
        export_to_txt(sample_records, str(filename), all_fields=False)

        assert filename.exists()
        content = filename.read_text(encoding="utf-8")
        assert "StudyTracker - 学習記録エクスポート" in content
        assert "テスト学習" in content


class TestMainFunction:
    """メイン関数のテスト"""

    @patch("src.cli.main.DatabaseManager")
    def test_main_with_add_command(self, mock_db_class):
        """addコマンドのテスト"""
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.add_study_record.return_value = 1

        # コマンドライン引数をモック
        with patch("sys.argv", ["study-tracker", "add", "テスト学習", "--time", "60"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()

        assert "✅ 学習記録を追加しました" in output

    @patch("src.cli.main.DatabaseManager")
    def test_main_with_list_command(self, mock_db_class):
        """listコマンドのテスト"""
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.get_all_study_records.return_value = []

        # コマンドライン引数をモック
        with patch("sys.argv", ["study-tracker", "list"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()

        assert "📝 学習記録がありません" in output

    @patch("src.cli.main.DatabaseManager")
    def test_main_with_invalid_command(self, mock_db_class):
        """無効なコマンドのテスト"""
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db

        # 存在しないコマンド
        with patch("sys.argv", ["study-tracker", "invalid"]):
            with patch("sys.stderr", new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit):
                    main()
                output = mock_stderr.getvalue()

        # エラーメッセージが表示されることを確認
        assert "usage:" in output
        assert "study-tracker" in output
        assert "invalid choice" in output

    def test_main_help(self):
        """ヘルプ表示のテスト"""
        with patch("sys.argv", ["study-tracker"]):
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                main()
                output = mock_stdout.getvalue()

        assert "usage:" in output
        assert "study-tracker" in output
