"""
FastAPIルート定義

Web APIのエンドポイントを定義します。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..models.study_record import StudyRecord
from ..database.connection import DatabaseManager

router = APIRouter(tags=["study-records"])


# Pydanticモデル（APIのリクエスト・レスポンス用）
class StudyRecordCreate(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=200, description="学習記録のタイトル"
    )
    content: Optional[str] = Field(None, max_length=1000, description="学習内容の詳細")
    study_time: int = Field(0, ge=0, le=1440, description="学習時間（分、0-1440分）")
    category: Optional[str] = Field(None, max_length=50, description="学習カテゴリ")
    difficulty: int = Field(1, ge=1, le=5, description="難易度（1-5）")


class StudyRecordUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="学習記録のタイトル"
    )
    content: Optional[str] = Field(None, max_length=1000, description="学習内容の詳細")
    study_time: Optional[int] = Field(
        None, ge=0, le=1440, description="学習時間（分、0-1440分）"
    )
    category: Optional[str] = Field(None, max_length=50, description="学習カテゴリ")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="難易度（1-5）")


class StudyRecordResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    study_time: int
    category: Optional[str]
    difficulty: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ページネーション用モデル
class PaginationInfo(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedStudyRecords(BaseModel):
    items: List[StudyRecordResponse]
    pagination: PaginationInfo


# 詳細統計情報用モデル
class CategoryStats(BaseModel):
    category: str
    count: int
    total_time: int
    total_hours: float
    average_difficulty: float
    average_time: float


class DifficultyStats(BaseModel):
    difficulty: int
    count: int
    total_time: int
    total_hours: float
    average_time: float


class TimeDistributionStats(BaseModel):
    short_time: int  # 30分未満
    medium_time: int  # 30分-2時間
    long_time: int  # 2時間以上
    total_records: int


class TimelineStats(BaseModel):
    date: str
    total_time: int
    total_hours: float
    count: int


# データベースマネージャーのインスタンス
db = DatabaseManager()


@router.get("/study-records", response_model=List[StudyRecordResponse])
async def get_study_records():
    """学習記録一覧を取得（非推奨: ページネーション機能付きのエンドポイントを使用してください）"""
    records = db.get_all_study_records()
    return records


@router.get("/study-records/paginated", response_model=PaginatedStudyRecords)
async def get_study_records_paginated(
    page: int = Query(1, ge=1, description="ページ番号（1から開始）"),
    limit: int = Query(10, ge=1, le=100, description="1ページあたりの件数（1-100）"),
    offset: int = Query(0, ge=0, description="スキップする件数"),
):
    """ページネーション機能付きで学習記録一覧を取得"""
    # オフセットの計算
    actual_offset = (page - 1) * limit + offset

    # 全件数を取得
    all_records = db.get_all_study_records()
    total_items = len(all_records)

    # ページネーション計算
    total_pages = (total_items + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1

    # 指定された範囲のレコードを取得
    start_index = actual_offset
    end_index = start_index + limit
    paginated_records = all_records[start_index:end_index]

    # ページネーション情報を作成
    pagination_info = PaginationInfo(
        page=page,
        limit=limit,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return PaginatedStudyRecords(items=paginated_records, pagination=pagination_info)


@router.get("/study-records/{record_id}", response_model=StudyRecordResponse)
async def get_study_record(record_id: int):
    """学習記録の詳細を取得"""
    record = db.get_study_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="学習記録が見つかりません")
    return record


@router.post("/study-records", response_model=StudyRecordResponse)
async def create_study_record(record_data: StudyRecordCreate):
    """学習記録を作成"""
    record = StudyRecord(
        title=record_data.title,
        content=record_data.content,
        study_time=record_data.study_time,
        category=record_data.category,
        difficulty=record_data.difficulty,
    )

    record_id = db.add_study_record(record)
    created_record = db.get_study_record(record_id)
    return created_record


@router.put("/study-records/{record_id}", response_model=StudyRecordResponse)
async def update_study_record(record_id: int, record_data: StudyRecordUpdate):
    """学習記録を更新"""
    # 更新データをフィルタリング
    update_data = {}
    for field, value in record_data.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value

    if not update_data:
        raise HTTPException(
            status_code=400, detail="更新するデータが指定されていません"
        )

    success = db.update_study_record(record_id, **update_data)
    if not success:
        raise HTTPException(status_code=404, detail="学習記録が見つかりません")

    updated_record = db.get_study_record(record_id)
    return updated_record


@router.delete("/study-records/{record_id}")
async def delete_study_record(record_id: int):
    """学習記録を削除"""
    success = db.delete_study_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="学習記録が見つかりません")

    return {"message": "学習記録を削除しました"}


@router.get("/study-records/stats/summary")
async def get_study_stats():
    """学習統計情報を取得"""
    records = db.get_all_study_records()

    if not records:
        return {
            "total_records": 0,
            "total_study_time": 0,
            "average_difficulty": 0,
            "categories": {},
        }

    total_time = sum(record.study_time for record in records)
    avg_difficulty = sum(record.difficulty for record in records) / len(records)

    # カテゴリ別統計
    categories = {}
    for record in records:
        if record.category:
            if record.category not in categories:
                categories[record.category] = {"count": 0, "total_time": 0}
            categories[record.category]["count"] += 1
            categories[record.category]["total_time"] += record.study_time

    return {
        "total_records": len(records),
        "total_study_time": total_time,
        "total_study_hours": round(total_time / 60, 2),
        "average_difficulty": round(avg_difficulty, 2),
        "categories": categories,
    }


@router.get("/study-records/stats/category", response_model=List[CategoryStats])
async def get_category_stats():
    """カテゴリ別詳細統計情報を取得"""
    records = db.get_all_study_records()

    if not records:
        return []

    # カテゴリ別統計を計算
    category_stats = {}
    for record in records:
        if record.category:
            if record.category not in category_stats:
                category_stats[record.category] = {
                    "count": 0,
                    "total_time": 0,
                    "difficulties": [],
                }
            category_stats[record.category]["count"] += 1
            category_stats[record.category]["total_time"] += record.study_time
            category_stats[record.category]["difficulties"].append(record.difficulty)

    # CategoryStatsオブジェクトに変換
    result = []
    for category, stats in category_stats.items():
        avg_difficulty = sum(stats["difficulties"]) / len(stats["difficulties"])
        avg_time = stats["total_time"] / stats["count"]

        result.append(
            CategoryStats(
                category=category,
                count=stats["count"],
                total_time=stats["total_time"],
                total_hours=round(stats["total_time"] / 60, 2),
                average_difficulty=round(avg_difficulty, 2),
                average_time=round(avg_time, 2),
            )
        )

    return result


@router.get("/study-records/stats/difficulty", response_model=List[DifficultyStats])
async def get_difficulty_stats():
    """難易度別詳細統計情報を取得"""
    records = db.get_all_study_records()

    if not records:
        return []

    # 難易度別統計を計算
    difficulty_stats = {}
    for record in records:
        difficulty = record.difficulty
        if difficulty not in difficulty_stats:
            difficulty_stats[difficulty] = {"count": 0, "total_time": 0}
        difficulty_stats[difficulty]["count"] += 1
        difficulty_stats[difficulty]["total_time"] += record.study_time

    # DifficultyStatsオブジェクトに変換
    result = []
    for difficulty, stats in difficulty_stats.items():
        avg_time = stats["total_time"] / stats["count"]

        result.append(
            DifficultyStats(
                difficulty=difficulty,
                count=stats["count"],
                total_time=stats["total_time"],
                total_hours=round(stats["total_time"] / 60, 2),
                average_time=round(avg_time, 2),
            )
        )

    return result


@router.get(
    "/study-records/stats/time-distribution", response_model=TimeDistributionStats
)
async def get_time_distribution_stats():
    """学習時間分布統計情報を取得"""
    records = db.get_all_study_records()

    if not records:
        return TimeDistributionStats(
            short_time=0, medium_time=0, long_time=0, total_records=0
        )

    # 時間分布を計算
    short_time = 0  # 30分未満
    medium_time = 0  # 30分-2時間
    long_time = 0  # 2時間以上

    for record in records:
        if record.study_time < 30:
            short_time += 1
        elif record.study_time < 120:
            medium_time += 1
        else:
            long_time += 1

    return TimeDistributionStats(
        short_time=short_time,
        medium_time=medium_time,
        long_time=long_time,
        total_records=len(records),
    )


@router.get("/study-records/stats/timeline", response_model=List[TimelineStats])
async def get_timeline_stats():
    """時系列統計情報を取得"""
    records = db.get_all_study_records()

    if not records:
        return []

    # 日別統計を計算
    timeline_stats = {}
    for record in records:
        # 日付を文字列に変換（YYYY-MM-DD形式）
        date_str = record.created_at.strftime("%Y-%m-%d")

        if date_str not in timeline_stats:
            timeline_stats[date_str] = {"total_time": 0, "count": 0}
        timeline_stats[date_str]["total_time"] += record.study_time
        timeline_stats[date_str]["count"] += 1

    # TimelineStatsオブジェクトに変換
    result = []
    for date_str, stats in timeline_stats.items():
        result.append(
            TimelineStats(
                date=date_str,
                total_time=stats["total_time"],
                total_hours=round(stats["total_time"] / 60, 2),
                count=stats["count"],
            )
        )

    # 日付順にソート
    result.sort(key=lambda x: x.date)
    return result
