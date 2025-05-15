from database.session import SessionLocal

# DB 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()