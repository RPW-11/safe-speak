from uuid import UUID
from sqlalchemy.orm import Session

from app.models.threat_indicator import ThreatIndicator


class ThreatIndicatorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_threat(self, message_id, description: str = "") -> ThreatIndicator:
        db_threat = ThreatIndicator(
            message_id = message_id,
            is_threat = True if description != "" else False,
            description = description,
            user_description = ""
        )

        self.db.add(db_threat)
        self.db.commit()
        self.db.refresh(db_threat)

        return db_threat