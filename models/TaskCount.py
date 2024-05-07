from sqlalchemy import Column, Integer
from configs.database import Base


class TaskCounter(Base):
    __tablename__ = "task_counters"

    user_id = Column(Integer, primary_key=True)
    total_created = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)
