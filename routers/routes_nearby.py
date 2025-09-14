# routes_nearby.py
from fastapi import APIRouter, Query, HTTPException
from db import db
from bson import ObjectId

router = APIRouter(prefix="/places")

@router.get("/nearby")
async def get_nearby_places(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: int = Query(5000, description="Search radius in meters")
):
    try:
        cursor = db.posts.find({
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
                "id": str(place["_id"]),  # Changed from "id" to "_id"
                "latitude": place["location"]["coordinates"][1],
                "longitude": place["location"]["coordinates"][0],
                "description_brief": place.get("description_brief", ""),
                "description_detail": place.get("description_detail", "")
            })
        return results
        
    except Exception as e:
        # Log the error and return a proper HTTP response
        print(f"Error in nearby places API: {e}")
        raise HTTPException(status_code=500, detail="Internal server error... contact pradeep")