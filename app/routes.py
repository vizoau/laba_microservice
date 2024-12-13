from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import User

router = APIRouter()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/users")
def create_user(request: Request, db: Session = Depends(get_db)):
    query_params = dict(request.query_params)
    params = {key: value for key, value in query_params.items() if key in ["name", "email"]}

    if len(params) < 2:
        raise HTTPException(status_code=422, detail="Both 'name' and 'email' are required")

    user = User(name=params['name'], email=params['email'])
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}")
def update_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Поиск пользователя в базе данных
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query_params = dict(request.query_params)
    name = query_params.get("name")
    email = query_params.get("email")

    if name:
        user.name = name

    if email:
        if "@" not in email:
            raise HTTPException(status_code=422, detail="Invalid email format")
        user.email = email

    if not name and not email:
        raise HTTPException(status_code=422, detail="At least one field ('name' or 'email') is required for update")

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
