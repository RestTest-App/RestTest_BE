from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_USER")
password = quote_plus(os.getenv("DB_PASSWORD"))
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

# DB_URL = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
DB_URL = (
    f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
    "?charset=utf8mb4"
)

engine = create_async_engine(DB_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(autoflush=False, bind=engine)