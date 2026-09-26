"""Feedback ownership validation and insert-or-update persistence."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.user.models import Conversation, Feedback, Message
from app.schemas.contract import FeedbackRequest


def save_feedback(db: Session, user_id: str, request: FeedbackRequest) -> None:
    message = db.get(Message, request.message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="ไม่พบข้อความที่ต้องการให้ feedback")

    conversation = db.get(Conversation, message.conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="ไม่พบบทสนทนาของข้อความนี้")
    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ให้ feedback กับข้อความนี้")
    if message.role != "assistant":
        raise HTTPException(status_code=400, detail="ให้ feedback ได้เฉพาะคำตอบของ COPIE")

    statement = select(Feedback).where(
        Feedback.message_id == request.message_id,
        Feedback.user_id == user_id,
    )
    feedback = db.exec(statement).first()
    if feedback is None:
        feedback = Feedback(message_id=request.message_id, user_id=user_id, rating=request.rating)

    feedback.rating = request.rating
    feedback.reason = request.reason if request.rating == "down" else None
    feedback.comment = request.comment if request.rating == "down" else None
    db.add(feedback)
    db.commit()
