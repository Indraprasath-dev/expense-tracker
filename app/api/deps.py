from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]

# Temporary until login exists: the caller says which user they are.
UserId = Annotated[int, Query(gt=0, description="Temporary: id of the user who owns the data")]
