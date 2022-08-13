from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def has_api_token(request: Request):
    if "x-api-token" not in request.headers.keys():
        raise HTTPException(status_code=404, detail="`x-api-token` not contained")
    return request


db_session = Depends(get_db)
has_token = Depends(has_api_token)


@app.get("/health-check")
def health_check(db: Session = db_session):
    return {"status": "ok"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, response: Response, db: Session = db_session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user, token = crud.create_user(db=db, user=user)
    response.headers["X-API-TOKEN"] = token
    return user


@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    request: Request = has_token,
    db: Session = db_session,
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    request: Request = has_token,
    db: Session = db_session,
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int,
    item: schemas.ItemCreate,
    request: Request = has_token,
    db: Session = db_session,
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    request: Request = has_token,
    db: Session = db_session,
):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
