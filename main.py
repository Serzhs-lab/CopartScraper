from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from scraper import CopartScraper  # Make sure this matches your scraper class file
import uvicorn

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
def scrape_endpoint(request: ScrapeRequest):
    try:
        scraper = CopartScraper()
        result = scraper.scrape_single_url(request.url)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
