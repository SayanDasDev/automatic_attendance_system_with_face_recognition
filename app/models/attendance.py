"""
SQLAlchemy model for Attendance
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    # Create a unique constraint to ensure a student is only marked once per session
    __table_args__ = (
        UniqueConstraint('user_id', 'session_id', name='uix_user_session'),
    )
    
    # Relationships
    user = relationship("User", backref="attendances")
    session = relationship("Session", backref="attendances")
    
    def __repr__(self):
        return f"<Attendance user_id={self.user_id} session_id={self.session_id}>"
