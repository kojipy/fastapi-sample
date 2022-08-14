from datetime import datetime

from sqlalchemy.orm import Session

from . import auth, models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = auth.get_hashed_password(user.password)
    token, limit = auth.create_token()
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()

    db_token = models.Token(token=token, token_limit=limit, user_id=db_user.id)
    db.add(db_token)
    db.commit()
    db.refresh(db_user)

    return db_user, token


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def authorized_tokens(db: Session):
    return (
        db.query(models.Token).filter(models.Token.token_limit > datetime.now()).all()
    )


def login(db: Session, user: schemas.UserLogin):
    user_db = get_user_by_email(db, user.email)

    if not user_db:
        return False

    if auth.get_hashed_password(user.password) != user_db.hashed_password:
        return False

    token, limit = auth.create_token()
    token_db = db.query(models.Token).filter(models.Token.user_id == user_db.id).first()
    token_db.token_limit = limit
    db.commit()
    db.refresh(token_db)

    return user_db, token
