from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ComponentType(str, enum.Enum):
    PROCESSOR = "processor"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    GPU = "gpu"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"


class StoreSource(str, enum.Enum):
    PCFACTORY = "pcfactory"


class Component(Base):
    __tablename__ = "components"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    brand = Column(String(100), index=True)
    component_type = Column(Enum(ComponentType), nullable=False, index=True)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True)
    store_source = Column(Enum(StoreSource), nullable=False)
    specifications = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_type_brand", "component_type", "brand"),
    )