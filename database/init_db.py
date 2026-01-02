from database.db import engine
from database.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized with all feedback tables.")

if __name__ == "__main__":
    init_db()