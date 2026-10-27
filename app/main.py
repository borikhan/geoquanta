import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.index import GeoIndex, Point

app = FastAPI(title="GeoQuanta", version="0.1.0")
index = GeoIndex(float(os.getenv("CELL_DEGREES", "0.25")))

class PointIn(BaseModel):
    id: str = Field(min_length=1)
    lat: float
    lon: float
    metadata: dict = {}

class Search(BaseModel):
    lat: float
    lon: float
    radius_km: float = Field(default=25, gt=0, le=1000)
    limit: int = Field(default=20, ge=1, le=100)

@app.get("/healthz")
def health(): return {"status":"ok"}

@app.post("/v1/points", status_code=202)
def ingest(points: list[PointIn]):
    if len(points) > int(os.getenv("MAX_BATCH_SIZE", "10000")): raise HTTPException(413,"batch too large")
    try: count=index.add([Point(**point.model_dump()) for point in points])
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return {"accepted":count}

@app.post("/v1/search")
def search(query: Search):
    matches=index.nearest(query.lat,query.lon,query.radius_km,query.limit)
    return {"results":[{"id":p.id,"lat":p.lat,"lon":p.lon,"metadata":p.metadata,"distanceKm":round(d,3)} for p,d in matches]}
