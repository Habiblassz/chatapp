from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import Base, engine, get_db
from models import User
# import models # this registers all the models(tables) created to Base.metadata
# and it is important because sqlalchemy needs to know about
# all the models before it can create tables for them
from pydantic import BaseModel
from passlib.context import CryptContext
import secrets

Base.metadata.create_all(bind=engine)

app = FastAPI()

pass_context = CryptContext(schemes=["bcrypt"])

sessions : dict[str, int] = {}

class SignupRequest(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    hashed_pass = pass_context.hash(data.password)

    new_user = User(username=data.username, hashed_password=hashed_pass)
    try:

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User name already exists. Please select a different username.")
    
    return {"message": f"User account created successfully! User_id: {new_user.id}"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user_account = db.query(User).filter(User.username == data.username).first()

    if not user_account or not pass_context.verify(data.password, user_account.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = user_account.id
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"message": "Welcoome to the home page."}


@app.get("/me")
def get_current_user(session_id: str | None = Cookie(default=None), db: Session=Depends(get_db)):
    if not session_id or not session_id in sessions:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    current_user = db.query(User).filter(User.id == sessions[session_id]).first()
    return {"username": current_user.username}