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

SCHEMA = "MaksimDarvin_comment"

def get_conn():
    return pyodbc.connect(CONN_STR)




class Comment(BaseModel):
    id: Optional[int] = None
    portfolio_id: int
    user_id: int
    content: str




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
        WHERE TABLE_SCHEMA = '{SCHEMA}' AND TABLE_NAME = 'comments'
    )
    CREATE TABLE {SCHEMA}.comments (
        id INT IDENTITY PRIMARY KEY,
        portfolio_id INT,
        user_id INT,
        content NVARCHAR(MAX)
    )
    """)

    conn.commit()
    conn.close()

    return {"status": "comment ready"}




@app.get("/comments", response_model=List[Comment])
def get_all():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"SELECT id, portfolio_id, user_id, content FROM {SCHEMA}.comments")
    rows = cursor.fetchall()
    conn.close()

    return [Comment(id=r[0], portfolio_id=r[1], user_id=r[2], content=r[3]) for r in rows]




@app.post("/comments")
def create(c: Comment):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO {SCHEMA}.comments (portfolio_id, user_id, content)
        VALUES (?, ?, ?)
    """, c.portfolio_id, c.user_id, c.content)

    conn.commit()
    conn.close()

    return {"status": "created"}