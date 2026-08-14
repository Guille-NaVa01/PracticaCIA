from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Defines tu variable
TU_PASSWORD = "12345"

# 2. Usas la 'f' antes de las comillas e insertas la variable con {}
DATABASE_URL = f"postgresql://postgres:{TU_PASSWORD}@localhost/chat_seguro"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()