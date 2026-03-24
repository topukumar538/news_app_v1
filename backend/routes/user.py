from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from core.dependencies import get_db, get_current_user, get_current_active_user
from models import  User #news
from schemas.feedback import FeedbackCreate
from services import feedback_service
from schemas.user import ProfileUpdate

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/feedback")
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return feedback_service.submit_feedback(user["user_id"], data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/profile")
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user)
):
    if not data.username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = data.username.strip()
    db.commit()
    return {"message": "Profile updated successfully"}