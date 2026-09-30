import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import your models from the core folder if you moved them
# from core.models import Base 

# Dynamic Path Discovery
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "tactical_db")

# Create folder if it doesn't exist (Safety Guard)
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'sentinel_v7_tactical.db')}"

class DatabaseManager:
    def __init__(self):
        # Setting check_same_thread=False allows the Frontend API to talk to it safely
        self.engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
        # Base.metadata.create_all(self.engine) 
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()