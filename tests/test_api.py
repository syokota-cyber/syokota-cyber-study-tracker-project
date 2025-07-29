import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.connection import DatabaseManager
from datetime import datetime

# テストクライアントの作成
client = TestClient(app)

# テスト用データベースマネージャー
db = DatabaseManager()


@pytest.fixture
def sample_study_record():
    """テスト用の学習記録データ"""
    return {
        "title": "pytest学習",
        "content": "FastAPIのテスト実装を学習",
        "study_time": 90,
        "category": "テスト",
        "difficulty": 3,
    }


@pytest.fixture
def sample_study_record_2():
    """テスト用の学習記録データ（2件目）"""
    return {
        "title": "APIテスト実装",
        "content": "pytestによるAPIテストの実装",
        "study_time": 120,
        "category": "テスト",
        "difficulty": 4,
    }


class TestStudyRecordsAPI:
    """学習記録APIのテストクラス"""

    def test_create_study_record(self, sample_study_record):
        """学習記録作成のテスト"""
        response = client.post("/api/v1/study-records/", json=sample_study_record)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_study_record["title"]
        assert data["content"] == sample_study_record["content"]
        assert data["study_time"] == sample_study_record["study_time"]
        assert data["category"] == sample_study_record["category"]
        assert data["difficulty"] == sample_study_record["difficulty"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_study_records(self):
        """学習記録一覧取得のテスト"""
        response = client.get("/api/v1/study-records/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "title" in data[0]
            assert "content" in data[0]
            assert "study_time" in data[0]
            assert "category" in data[0]
            assert "difficulty" in data[0]
            assert "created_at" in data[0]
            assert "updated_at" in data[0]

    def test_get_study_record_by_id(self):
        """学習記録詳細取得のテスト"""
        # まず学習記録を作成
        sample_record = {
            "title": "テスト用記録",
            "content": "テスト用の学習記録",
            "study_time": 60,
            "category": "テスト",
            "difficulty": 2,
        }
        create_response = client.post("/api/v1/study-records/", json=sample_record)
        assert create_response.status_code == 200
        record_id = create_response.json()["id"]

        # 作成した記録を取得
        response = client.get(f"/api/v1/study-records/{record_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == record_id
        assert data["title"] == sample_record["title"]

    def test_get_study_record_by_id_not_found(self):
        """存在しないIDでの学習記録取得テスト"""
        response = client.get("/api/v1/study-records/99999")
        assert response.status_code == 404

    def test_update_study_record(self):
        """学習記録更新のテスト"""
        # まず学習記録を作成
        sample_record = {
            "title": "更新前のタイトル",
            "content": "更新前の内容",
            "study_time": 60,
            "category": "テスト",
            "difficulty": 2,
        }
        create_response = client.post("/api/v1/study-records/", json=sample_record)
        assert create_response.status_code == 200
        record_id = create_response.json()["id"]

        # 更新データ
        update_data = {
            "title": "更新後のタイトル",
            "content": "更新後の内容",
            "study_time": 90,
            "category": "更新テスト",
            "difficulty": 3,
        }

        # 更新実行
        response = client.put(f"/api/v1/study-records/{record_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["study_time"] == update_data["study_time"]
        assert data["category"] == update_data["category"]
        assert data["difficulty"] == update_data["difficulty"]

    def test_delete_study_record(self):
        """学習記録削除のテスト"""
        # まず学習記録を作成
        sample_record = {
            "title": "削除用記録",
            "content": "削除される学習記録",
            "study_time": 60,
            "category": "テスト",
            "difficulty": 2,
        }
        create_response = client.post("/api/v1/study-records/", json=sample_record)
        assert create_response.status_code == 200
        record_id = create_response.json()["id"]

        # 削除実行
        response = client.delete(f"/api/v1/study-records/{record_id}")
        assert response.status_code == 200

        # 削除確認
        get_response = client.get(f"/api/v1/study-records/{record_id}")
        assert get_response.status_code == 404


class TestPaginationAPI:
    """ページネーションAPIのテストクラス"""

    def test_get_study_records_paginated(self):
        """ページネーション機能のテスト"""
        response = client.get("/api/v1/study-records/paginated?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()

        # レスポンス構造の確認
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)

        # ページネーション情報の確認
        pagination = data["pagination"]
        assert "page" in pagination
        assert "limit" in pagination
        assert "total_items" in pagination
        assert "total_pages" in pagination
        assert "has_next" in pagination
        assert "has_prev" in pagination

        # 値の妥当性確認
        assert pagination["page"] >= 1
        assert pagination["limit"] >= 1
        assert pagination["total_items"] >= 0
        assert pagination["total_pages"] >= 0

    def test_get_study_records_paginated_with_offset(self):
        """オフセット付きページネーションのテスト"""
        response = client.get("/api/v1/study-records/paginated?page=1&limit=3&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "pagination" in data


class TestStatisticsAPI:
    """統計APIのテストクラス"""

    def test_get_category_stats(self):
        """カテゴリ別統計のテスト"""
        response = client.get("/api/v1/study-records/stats/category")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            item = data[0]
            assert "category" in item
            assert "count" in item
            assert "total_time" in item
            assert "total_hours" in item
            assert "average_difficulty" in item
            assert "average_time" in item

    def test_get_difficulty_stats(self):
        """難易度別統計のテスト"""
        response = client.get("/api/v1/study-records/stats/difficulty")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            item = data[0]
            assert "difficulty" in item
            assert "count" in item
            assert "total_time" in item
            assert "total_hours" in item
            assert "average_time" in item

    def test_get_time_distribution_stats(self):
        """時間分布統計のテスト"""
        response = client.get("/api/v1/study-records/stats/time-distribution")
        assert response.status_code == 200
        data = response.json()

        assert "short_time" in data
        assert "medium_time" in data
        assert "long_time" in data
        assert "total_records" in data

        # 値の妥当性確認
        assert data["short_time"] >= 0
        assert data["medium_time"] >= 0
        assert data["long_time"] >= 0
        assert data["total_records"] >= 0

    def test_get_timeline_stats(self):
        """時系列統計のテスト"""
        response = client.get("/api/v1/study-records/stats/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            item = data[0]
            assert "date" in item
            assert "total_time" in item
            assert "total_hours" in item
            assert "count" in item


class TestErrorHandling:
    """エラーハンドリングのテストクラス"""

    def test_invalid_study_record_data(self):
        """無効なデータでの学習記録作成テスト"""
        invalid_data = {
            "title": "",  # 空のタイトル
            "study_time": -1,  # 負の値
            "difficulty": 6,  # 範囲外の値
        }
        response = client.post("/api/v1/study-records/", json=invalid_data)
        # FastAPIのバリデーションエラーは422を返す
        assert response.status_code == 422

    def test_invalid_pagination_parameters(self):
        """無効なページネーションパラメータのテスト"""
        response = client.get("/api/v1/study-records/paginated?page=0&limit=0")
        # バリデーションエラー
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
