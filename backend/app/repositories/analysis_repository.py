from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.entities import AnalysisRecord
from backend.app.core.logging import logger

class AnalysisRepository:
    """Repository handling persistence, pagination, and deletion of verification records."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, record: AnalysisRecord) -> AnalysisRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisRecord]:
        return self.db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()

    def list_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[List[AnalysisRecord], int]:
        offset = (page - 1) * page_size
        query = self.db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc())
        total = query.count()
        items = query.offset(offset).limit(page_size).all()
        return items, total

    def delete(self, analysis_id: str) -> bool:
        record = self.get_by_id(analysis_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
