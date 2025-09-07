from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import db

app = FastAPI()

# Allow all origins (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Blogger API is running!"}

@app.post("/trips")
async def add_trip(trip: dict):
    result = await db.trips.insert_one(trip)
    return {"id": str(result.inserted_id), "trip": trip}

@app.get("/trips")
async def get_trips():
    trips = await db.trips.find().to_list(100)
    return trips
