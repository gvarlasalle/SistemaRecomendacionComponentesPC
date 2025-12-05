# backend/data_layer/database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, TIMESTAMP, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuración de base de datos
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class Component(Base):
    __tablename__ = 'components'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    brand = Column(String(100))
    price = Column(DECIMAL(10, 2), index=True)
    specs = Column(JSONB)
    compatibility_info = Column(JSONB)
    url = Column(Text)
    image_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String(50), nullable=False, index=True)
    budget_range = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    component_id = Column(Integer, index=True)
    interaction_type = Column(String(50))
    rating = Column(DECIMAL(3, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Configuration(Base):
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    config_name = Column(String(255))
    components = Column(JSONB)
    total_price = Column(DECIMAL(10, 2))
    is_compatible = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()