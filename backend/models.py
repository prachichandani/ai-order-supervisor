from sqlalchemy import Column, Integer, String

from database import Base


class Run(Base):

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)

    workflow_id = Column(String, unique=True)

    status = Column(String)
    
    memory_summary = Column(String, default="")


class Activity(Base):

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    workflow_id = Column(String)

    type = Column(String)

    message = Column(String)