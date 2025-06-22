from app.database import class_collection, booking_collection,user_collection
from app import models
from datetime import datetime
from fastapi import HTTPException
import pytz
from passlib.context import CryptContext
from dateutil import parser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from datetime import datetime, timedelta

def get_future_datetime(days_offset: int, hour: int, minute: int = 0):
    now = datetime.now()
    future_date = now + timedelta(days=days_offset)
    return future_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

async def load_seed_data():
    if await class_collection.count_documents({}) == 0:
        sample_classes = [
            {
                "class_id": 1,
                "name": "Yoga",
                "datetime": get_future_datetime(1, 7),  # Tomorrow at 7:00 AM
                "instructor": "Ananya",
                "available_slots": 20
            },
            {
                "class_id": 2,
                "name": "Zumba",
                "datetime": get_future_datetime(2, 9),  # Day after tomorrow at 9:00 AM
                "instructor": "Rohit",
                "available_slots": 10
            },
            {
                "class_id": 3,
                "name": "HIIT",
                "datetime": get_future_datetime(3, 6, 30),  # 3 days later at 6:30 AM
                "instructor": "Kavya",
                "available_slots": 20
            },
            {
                "class_id": 4,
                "name": "Pilates",
                "datetime": get_future_datetime(4, 8),  # 4 days later at 8:00 AM
                "instructor": "Arjun",
                "available_slots": 5
            },
            {
                "class_id": 5,
                "name": "Strength Training",
                "datetime": get_future_datetime(5, 7, 30),  # 5 days later at 7:30 AM
                "instructor": "Meera",
                "available_slots": 7
            }
        ]
        await class_collection.insert_many(sample_classes)


# ✅ Get all classes
async def get_all_classes():
    classes = await class_collection.find({}).to_list(length=100)
    return [
        {
            "id": str(cls["_id"]),
            "class_id": cls["class_id"],
            "name": cls["name"],
            "datetime": cls["datetime"],
            "instructor": cls["instructor"],
            "available_slots": cls["available_slots"]
        }
        for cls in classes
    ]

# ✅ Create a booking
import logging
# Update your models.py to include timezone in BookingRequest


# Update your booking creation function in crud.py
async def create_booking(booking: models.BookingRequest):
    print(f"Received booking request: {booking}")
    print(f"class_id: {booking.class_id}, type: {type(booking.class_id)}")
    print(f"client_name: {booking.client_name}")
    print(f"client_email: {booking.client_email}")
    print(f"timezone: {booking.timezone}")
    
    try:
        cls = await class_collection.find_one({"class_id": int(booking.class_id)})
        print(f"Found class: {cls}")
        
        if not cls:
            print("Class not found!")
            raise HTTPException(status_code=404, detail="Class not found")

        if cls["available_slots"] <= 0:
            print("No available slots!")
            raise HTTPException(status_code=400, detail="No available slots")

        # 🚫 Prevent double booking: check class_id, client_email, datetime AND timezone
        existing = await booking_collection.find_one({
            "class_id": cls["class_id"],
            "client_email": booking.client_email,
            "datetime": booking.datetime,  
            "timezone": booking.timezone  # Include timezone in duplicate check
        })
        print(f"Existing booking check: {existing}")
        
        if existing:
            print("User already booked this class at this time in this timezone!")
            raise HTTPException(
                status_code=400,
                detail="You have already booked this class at this time in this timezone."
            )

        # Decrease slot count
        await class_collection.update_one(
            {"class_id": int(booking.class_id)},
            {"$inc": {"available_slots": -1}}
        )

        booking_doc = {
        "class_id": cls["class_id"],
        "class_name": cls["name"],
        "datetime": booking.datetime,  # ✅ Use the datetime sent from the frontend!
        "instructor": cls["instructor"],
        "client_name": booking.client_name,
        "client_email": booking.client_email,
        "timezone": booking.timezone
    }

        result = await booking_collection.insert_one(booking_doc)
        booking_doc["id"] = str(result.inserted_id)
        print(f"Booking created successfully: {booking_doc}")
        return models.Booking(**booking_doc)
        
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add endpoint to get user bookings


async def get_bookings_by_email(email: str):
    bookings = await booking_collection.find({"client_email": email}).to_list(length=100)
    results = []
    for booking in bookings:
        # dt = parser.isoparse(booking["datetime"]) if isinstance(booking["datetime"], str) else booking["datetime"]
        # formatted_datetime = dt.strftime("%d/%m/%Y %H:%M:%S")
        results.append({
            "id": str(booking["_id"]),
            "class_id": booking["class_id"],
            "class_name": booking["class_name"],
            "datetime": booking["datetime"],  # <-- Now this will be 11:00:00 for your example!
            "instructor": booking["instructor"],
            "client_name": booking["client_name"],
            "client_email": booking["client_email"],
            "timezone": booking.get("timezone", "Asia/Kolkata")
        })
    return results
    
async def signup_user(email: str, password: str, name: str):
    existing_user = await user_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(password)
    user_doc = {
        "email": email,
        "name": name,  # Store the name
        "hashed_password": hashed_password,
    }
    await user_collection.insert_one(user_doc)
    return {"email": email, "name": name}  # Return name as well

async def login_user(email: str, password: str):
    user = await user_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Return both email and name
    return {"email": user["email"], "name": user.get("name", "")}
