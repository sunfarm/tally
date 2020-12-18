from dataclasses import dataclass

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
# from sqlalchemy.orm import registry

# mapper_registry = registry()

Base = declarative_base()

# @mapper_registry.mapped
@dataclass
class Tally(Base):
    # """"""
    # time_created: Column(DateTime(timezone=True), server_default=func.now())
    __tablename__ = "tally"
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())



