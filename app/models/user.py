"""
SQLAlchemy model for User
"""

from sqlalchemy import Column, Integer, String

from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    def __repr__(self):
        return f"<User {self.name}>"
