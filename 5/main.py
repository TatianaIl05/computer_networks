from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Query, HTTPException

from parser import Parser
from database import Database


parser = Parser()
database = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    database.close() 
    parser.close()   

app = FastAPI(lifespan=lifespan)


@app.get("/parse")
def parse_quotes(url: str = Query(...)):

    try:
        quotes_data = parser.parse_quotes(url)
        
        if not quotes_data:
            return {
                "status": "warning",
                "message": "No quotes were parsed",
                "pages_parsed": 0,
                "quotes_saved": 0,
                "source_url": url
            }
        
        saved_count = database.save_quotes(quotes_data, url)
        
        return {
            "status": "success",
            "message": f"Successfully parsed and saved {saved_count} quotes",
            "pages_parsed": len(set([q[0] for q in quotes_data])),
            "quotes_saved": saved_count,
            "source_url": url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@app.get("/get_data")
def get_data():

    quotes = database.get_all_quotes()
    
    if not quotes:
        return {
            "status": "empty",
            "message": "No quotes found",
            "data": []
        }
    
    return {
        "status": "success",
        "count": len(quotes),
        "data": quotes
    }


@app.delete("/clean_db")
def clean_database(confirm: bool = Query(False)):
    if not confirm:
        raise HTTPException(status_code=400, detail="To confirm, use: DELETE /clean_db?confirm=true")
    
    try:
        database.clean_db()
        return {"status": "success", "message": "Database cleaned"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=80,
        reload=True
    )

