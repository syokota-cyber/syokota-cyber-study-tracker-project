"""
データベース接続管理

SQLiteデータベースへの接続、セッション管理、CRUD操作を提供します。
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..models.study_record import StudyRecord


class DatabaseManager:
    """
    データベース管理クラス
    
    SQLiteデータベースとの接続、テーブル作成、CRUD操作を管理します。
    """
    
    def __init__(self, db_path: str = "study_tracker.db"):
        """
        データベースマネージャーを初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 学習記録テーブルの作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    study_time INTEGER DEFAULT 0,
                    category TEXT,
                    difficulty INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_study_record(self, record: StudyRecord) -> int:
        """学習記録を追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO study_records (title, content, study_time, category, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (record.title, record.content, record.study_time, record.category, record.difficulty))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_study_record(self, record_id: int) -> Optional[StudyRecord]:
        """学習記録を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, content, study_time, category, difficulty, created_at, updated_at
                FROM study_records WHERE id = ?
            """, (record_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_study_record(row)
            return None
    
    def get_all_study_records(self) -> List[StudyRecord]:
        """全ての学習記録を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, content, study_time, category, difficulty, created_at, updated_at
                FROM study_records ORDER BY created_at DESC
            """)
            
            return [self._row_to_study_record(row) for row in cursor.fetchall()]
    
    def update_study_record(self, record_id: int, **kwargs) -> bool:
        """学習記録を更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 更新可能なフィールド
            allowed_fields = ['title', 'content', 'study_time', 'category', 'difficulty']
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = ?")
            values.append(datetime.now())
            values.append(record_id)
            
            cursor.execute(f"""
                UPDATE study_records 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_study_record(self, record_id: int) -> bool:
        """学習記録を削除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM study_records WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_study_record(self, row) -> StudyRecord:
        """データベース行をStudyRecordオブジェクトに変換"""
        record = StudyRecord(
            id=row[0],
            title=row[1],
            content=row[2],
            study_time=row[3],
            category=row[4],
            difficulty=row[5]
        )
        record.created_at = datetime.fromisoformat(row[6])
        record.updated_at = datetime.fromisoformat(row[7])
        return record