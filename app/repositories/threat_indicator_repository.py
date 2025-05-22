from uuid import UUID
from sqlalchemy.orm import Session

from app.models.threat_indicator import ThreatIndicator


class ThreatIndicatorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_threat(self, message_id: str, description: str = "") -> ThreatIndicator:
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
    
    def update_threat_status_by_msg_id(self, message_id: str) -> ThreatIndicator:
        db_threat = self.db.query(ThreatIndicator).filter(ThreatIndicator.message_id == message_id).first()
        db_threat.is_threat = not db_threat.is_threat
        self.db.commit()
        self.db.refresh(db_threat)

        return db_threat