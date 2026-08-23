from sqlalchemy import Column, Integer, String
from database import Base

class User(Base): # this registers User with Base.metadata, an sqlaclchemy registry
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False) # unique attribute makes the db reject any insert that will duplicate an existing username and raises and integrity error
    hashed_password = Column(String, nullable=False)