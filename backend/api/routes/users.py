from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import User
from schemas.user import UserUpdate, User as UserSchema, BeliefUpdate
from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserSchema)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserSchema.from_orm(current_user)

@router.put("/profile", response_model=UserSchema)
def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user fields
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.interests is not None:
        current_user.interests = user_data.interests
    if user_data.belief_fingerprint is not None:
        current_user.belief_fingerprint = user_data.belief_fingerprint
    if user_data.bias_setting is not None:
        current_user.bias_setting = user_data.bias_setting
    
    db.commit()
    db.refresh(current_user)
    
    return UserSchema.from_orm(current_user)

@router.post("/beliefs")
def update_beliefs(
    belief_data: BeliefUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update beliefs for specific topic
    if not current_user.belief_fingerprint:
        current_user.belief_fingerprint = {}
    
    current_user.belief_fingerprint[belief_data.topic] = belief_data.beliefs
    db.commit()
    
    return {"message": f"Beliefs updated for topic: {belief_data.topic}"} 