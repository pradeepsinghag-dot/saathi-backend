# routes_nearby.py
from fastapi import APIRouter, Query
from db import db

router = APIRouter(prefix="/places")

@router.get("/nearby")
async def get_nearby_places(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: int = Query(500, description="Search radius in meters")
):
    cursor = db.places.find({
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]  # GeoJSON order
                },
                "$maxDistance": radius
            }
        }
    })

    results = []
    async for place in cursor:
        results.append({
            "id": str(place["id"]),
            "latitude": place["location"]["coordinates"][1],
            "longitude": place["location"]["coordinates"][0],
            "description_brief": place.get("description_brief", ""),
            "description_detail": place.get("description_detail", "")
        })
    return results
