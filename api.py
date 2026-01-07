import sqlite3
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

app = FastAPI(title="名言佳句API")



class PostCreate(BaseModel):
    text: str
    author: str
    tags: str

class PostResponse(PostCreate):
    id: int
    
    model_config = ConfigDict(from_attributes=True)



def get_db_connection():
    conn = sqlite3.connect("quotes.db", check_same_thread=False)
    
    conn.row_factory = sqlite3.Row
    return conn



@app.get("/quotes", response_model=List[PostResponse])
async def get_quotes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes")
    rows = cursor.fetchall()
    conn.close()
    
    # 將 sqlite3.Row 轉換為 list of dicts
    return [dict(row) for row in rows]

@app.post("/quotes", response_model=PostResponse)
async def create_quote(quote: PostCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)"
    cursor.execute(query, (quote.text, quote.author, quote.tags))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {**quote.model_dump(), "id": new_id}

@app.put("/quotes/{quote_id}", response_model=PostResponse)
async def update_quote(quote_id: int, quote: PostCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 檢查是否存在
    cursor.execute("SELECT id FROM quotes WHERE id = ?", (quote_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Quote not found")
    
    query = "UPDATE quotes SET text = ?, author = ?, tags = ? WHERE id = ?"
    cursor.execute(query, (quote.text, quote.author, quote.tags, quote_id))
    conn.commit()
    conn.close()
    
    return {**quote.model_dump(), "id": quote_id}

@app.delete("/quotes/{quote_id}")
async def delete_quote(quote_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 檢查是否存在
    cursor.execute("SELECT id FROM quotes WHERE id = ?", (quote_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Quote not found")
    
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Quote deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    # 啟動伺服器，監聽 8000 端口
    uvicorn.run(app, host="127.0.0.1", port=8000)
