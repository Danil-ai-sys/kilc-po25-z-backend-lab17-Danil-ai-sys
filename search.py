from fastapi import APIRouter
from sqlalchemy import text

from app.deps import SessionDep
from app.routers.messages import get_room_or_404
from app.schemas import SearchHit

router = APIRouter(prefix="/rooms/{room_id}/search", tags=["search"])


@router.get("", response_model=list[SearchHit])
def search(room_id: int, q: str, session: SessionDep):
    get_room_or_404(session, room_id)
    # Values travel separately from the SQL text: :room_id and :pattern are placeholders.
    sql = text(
        "SELECT id, text FROM messages "
        "WHERE room_id = :room_id AND text LIKE :pattern "
        "ORDER BY id"
    )
    rows = session.execute(sql, {"room_id": room_id, "pattern": f"%{q}%"})
    return [{"id": row.id, "text": row.text} for row in rows]
