from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from db.session import get_db
from db.models import Story, FusionResult
from schemas.fusion import FusionResult as FusionResultSchema
from api.routes.auth import get_current_user
from services.fusion_engine import FusionEngine

router = APIRouter()

@router.get("/{story_id}", response_model=FusionResultSchema)
async def get_fusion_result(
    story_id: str,
    bias: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Check if fusion result already exists for this bias level
    existing_result = db.query(FusionResult).filter(
        FusionResult.story_id == story_id,
        FusionResult.bias_level == bias
    ).first()
    
    if existing_result:
        return FusionResultSchema.from_orm(existing_result)
    
    # Generate new fusion result
    try:
        fusion_engine = FusionEngine()
        fusion_data = await fusion_engine.fuse_narrative(
            story_id=story_id,
            bias=bias,
            db=db
        )
        
        # Save fusion result
        fusion_result = FusionResult(
            story_id=story_id,
            fused_narrative=fusion_data["fused_narrative"],
            modulated_narrative=fusion_data["modulated_narrative"],
            bias_level=bias,
            contradictions=fusion_data.get("contradictions", []),
            entities=fusion_data.get("entities", []),
            confidence=fusion_data.get("confidence", 1.0)
        )
        
        db.add(fusion_result)
        db.commit()
        db.refresh(fusion_result)
        
        return FusionResultSchema.from_orm(fusion_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate fusion result: {str(e)}"
        )

@router.post("/{story_id}/regenerate")
async def regenerate_fusion_result(
    story_id: str,
    bias: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Delete existing fusion result if it exists
    existing_result = db.query(FusionResult).filter(
        FusionResult.story_id == story_id,
        FusionResult.bias_level == bias
    ).first()
    
    if existing_result:
        db.delete(existing_result)
        db.commit()
    
    # Generate new fusion result
    try:
        fusion_engine = FusionEngine()
        fusion_data = await fusion_engine.fuse_narrative(
            story_id=story_id,
            bias=bias,
            db=db
        )
        
        # Save fusion result
        fusion_result = FusionResult(
            story_id=story_id,
            fused_narrative=fusion_data["fused_narrative"],
            modulated_narrative=fusion_data["modulated_narrative"],
            bias_level=bias,
            contradictions=fusion_data.get("contradictions", []),
            entities=fusion_data.get("entities", []),
            confidence=fusion_data.get("confidence", 1.0)
        )
        
        db.add(fusion_result)
        db.commit()
        db.refresh(fusion_result)
        
        return FusionResultSchema.from_orm(fusion_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate fusion result: {str(e)}"
        ) 