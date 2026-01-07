from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

app = FastAPI()

class Quote(BaseModel):
    text: str
    author: str
    tags: str

def get_db():
    conn = sqlite3.connect("quotes.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/quotes")
def read_quotes():
    db = get_db()
    rows = db.execute("SELECT * FROM quotes").fetchall()
    return [dict(r) for r in rows]

@app.post("/quotes")
def create_quote(q: Quote):
    db = get_db()
    cur = db.execute("INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)", (q.text, q.author, q.tags))
    db.commit()
    return {"id": cur.lastrowid, **q.dict()}

@app.put("/quotes/{qid}")
def update_quote(qid: int, q: Quote):
    db = get_db()
    db.execute("UPDATE quotes SET text=?, author=?, tags=? WHERE id=?", (q.text, q.author, q.tags, qid))
    db.commit()
    return {"id": qid, **q.dict()}

@app.delete("/quotes/{qid}")
def delete_quote(qid: int):
    db = get_db()
    db.execute("DELETE FROM quotes WHERE id=?", (qid,))
    db.commit()
    return {"message": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)