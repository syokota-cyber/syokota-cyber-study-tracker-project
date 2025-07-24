"""
FastAPIルート定義

Web APIのエンドポイントを定義します。
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from ..models.study_record import StudyRecord
from ..database.connection import DatabaseManager

router = APIRouter(prefix="/api/v1", tags=["study-records"])

# Pydanticモデル（APIのリクエスト・レスポンス用）
class StudyRecordCreate(BaseModel):
    title: str
    content: Optional[str] = None
    study_time: int = 0
    category: Optional[str] = None
    difficulty: int = 1

class StudyRecordUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    study_time: Optional[int] = None
    category: Optional[str] = None
    difficulty: Optional[int] = None

class StudyRecordResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    study_time: int
    category: Optional[str]
    difficulty: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# データベースマネージャーのインスタンス
db = DatabaseManager()

@router.get("/study-records", response_model=List[StudyRecordResponse])
async def get_study_records():
    """学習記録一覧を取得"""
    records = db.get_all_study_records()
    return records

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
        difficulty=record_data.difficulty
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
        raise HTTPException(status_code=400, detail="更新するデータが指定されていません")
    
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
            "categories": {}
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
        "categories": categories
    }