from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import db
from bson import ObjectId

app = FastAPI()

# Allow all origins (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/")
def read_root():
    return {"message": "Blogger API is running!"}

@app.post("/trips")
async def add_trip(trip: dict):
    result = await db.trips.insert_one(trip)
    trip["_id"] = str(result.inserted_id)
    return {"id": trip["_id"], "trip": trip}

@app.get("/trips")
async def get_trips():
    trips = await db.trips.find().to_list(100)
    return [serialize_doc(trip) for trip in trips]
