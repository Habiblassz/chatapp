from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import Base, engine, get_db
from models import User
# import models # this registers all the models(tables) created to Base.metadata
# and it is important because sqlalchemy needs to know about
# all the models before it can create tables for them
from pydantic import BaseModel
from passlib.context import CryptContext

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

