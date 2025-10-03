from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models.components import Component, ComponentType

router = APIRouter()


@router.get("/components")
async def get_components(
    component_type: Optional[ComponentType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Component)
    if component_type:
        query = query.filter(Component.component_type == component_type)
    return query.offset(skip).limit(limit).all()


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    total = db.query(func.count(Component.id)).scalar()
    return {"total_components": total or 0}