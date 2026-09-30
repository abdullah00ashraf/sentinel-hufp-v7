import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Pathing Logic: Always finds the root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "tactical_db")

# Safety Guard: Ensure the folder exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'sentinel_v7_tactical.db')}"

class SentinelDB:
    def __init__(self):
        # check_same_thread=False allows Web Dashboard to query safely
        self.engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def get_engine(self):
        return self.engine