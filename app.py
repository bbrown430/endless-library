# app.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4

from src.anna_list import AnnaList
from src.io_utils import IOUtils

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory session state
search_sessions: Dict[str, Dict] = {}

# Models
class SearchRequest(BaseModel):
    query: str

@app.post("/search")
def search_books(request: SearchRequest):
    anna_list = AnnaList()
    books = anna_list.scrape(request.query)

    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    session_id = str(uuid4())
    search_sessions[session_id] = {
        "results": books,
        "index": 0
    }

    first_book = books[0]
    return {
        "session_id": session_id,
        "book": first_book.to_dict()
    }

@app.get("/next/{session_id}")
def get_next_book(session_id: str):
    session = search_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    index = session["index"]
    results = session["results"]

    if index + 1 >= len(results):
        raise HTTPException(status_code=404, detail="No more results")

    session["index"] += 1
    return {"book": results[session["index"]]}


@app.get("/download/{session_id}")
def download_book(session_id: str, user: str = Query(...)):
    session = search_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    index = session["index"]
    book = session["results"][index]

    io_utils = IOUtils()
    cdn = io_utils.get_cdn()
    
    # You can now use the `user` value here (e.g. for logging, metadata, routing)
    print(f"Downloading for user: {user}")

    success = io_utils.download_book(book, cdn)
    email_success = io_utils.send_email(book, user)

    if not success:
        raise HTTPException(status_code=500, detail="Download failed")
    
    if not email_success:
        raise HTTPException(status_code=500, detail="Book failed to send to Kindle")

    return {
        "message": "Download successful",
        "title": book.title,
        "user": user
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=38100)