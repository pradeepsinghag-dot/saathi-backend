from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from db import db
from bson import ObjectId
from typing import Optional

app = FastAPI()

# Allow all origins (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Pydantic Models
# ----------------------------
class Trip(BaseModel):
    destination: str = Field(..., example="Munnar")
    date: str = Field(..., example="2025-09-07")

class TripResponse(BaseModel):
    id: str
    destination: str
    date: str

# ----------------------------
# Helper to serialize MongoDB docs
# ----------------------------
def serialize_doc(doc):
    return {
        "id": str(doc["_id"]),
        "destination": doc["destination"],
        "date": doc["date"]
    }

# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Blogger API is running!"}

@app.post("/trips", response_model=TripResponse)
async def add_trip(trip: Trip):
    trip_dict = trip.dict()
    result = await db.trips.insert_one(trip_dict)
    return {"id": str(result.inserted_id), **trip_dict}

@app.get("/trips", response_model=list[TripResponse])
async def get_trips():
    trips = await db.trips.find().to_list(100)
    return [serialize_doc(trip) for trip in trips]

@app.put("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: str, trip: Trip):
    update_result = await db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": trip.dict()}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    updated = await db.trips.find_one({"_id": ObjectId(trip_id)})
    return serialize_doc(updated)

@app.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str):
    delete_result = await db.trips.delete_one({"_id": ObjectId(trip_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}
