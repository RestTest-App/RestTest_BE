from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

MODE = os.getenv("MODE", "dev")
if MODE == "dev":
    load_dotenv(".env.dev")

user = os.getenv("DB_USER", "")
password = quote_plus(os.getenv("DB_PASSWORD", ""))
host = os.getenv("DB_HOST", "")
port = os.getenv("DB_PORT", "")
database = os.getenv("DB_NAME", "")

DB_URL = (
    f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
    "?charset=utf8mb4"
)

engine = create_async_engine(
    DB_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "charset": "utf8mb4",
    }
, isolation_level="READ COMMITTED"
)
AsyncSessionLocal = async_sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)