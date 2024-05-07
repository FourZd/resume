from configs.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    description = Column(String)
    created_at = Column(DateTime)
    completed = Column(Boolean, default=False)
