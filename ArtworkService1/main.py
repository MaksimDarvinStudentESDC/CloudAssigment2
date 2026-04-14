from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import pyodbc
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME]):
    raise Exception("Missing database environment variables")


CONN_STR = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server=tcp:{DB_SERVER},1433;"
    f"Database={DB_NAME};"
    f"Uid={DB_USER};"
    f"Pwd={DB_PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

SCHEMA = "MaksimDarvin_artwork"

def get_conn():
    return pyodbc.connect(CONN_STR)



class Artwork(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    author_id: int



@app.post("/init")
def init():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
    IF NOT EXISTS (
        SELECT * FROM sys.schemas WHERE name = '{SCHEMA}'
    )
    EXEC('CREATE SCHEMA {SCHEMA}')
    """)

    cursor.execute(f"""
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{SCHEMA}' AND TABLE_NAME = 'artworks'
    )
    CREATE TABLE {SCHEMA}.artworks (
        id INT IDENTITY PRIMARY KEY,
        title NVARCHAR(255),
        description NVARCHAR(MAX),
        author_id INT
    )
    """)

    conn.commit()
    conn.close()

    return {"status": "artwork ready"}




@app.get("/artworks", response_model=List[Artwork])
def get_all():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"SELECT id, title, description, author_id FROM {SCHEMA}.artworks")
    rows = cursor.fetchall()
    conn.close()

    return [Artwork(id=r[0], title=r[1], description=r[2], author_id=r[3]) for r in rows]




@app.post("/artworks")
def create(a: Artwork):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO {SCHEMA}.artworks (title, description, author_id)
        VALUES (?, ?, ?)
    """, a.title, a.description, a.author_id)

    conn.commit()
    conn.close()

    return {"status": "created"}