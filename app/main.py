from fastapi import FastAPI, HTTPException, Query
from app import database, models, crud, utils
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Fitness Booking API")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load sample data on server start
# @app.on_event("startup")
# async def startup_event():
#     await crud.load_seed_data()

# ✅ List all fitness classes
@app.get(
    "/classes",
    response_model=List[models.FitnessClass],
    tags=["Classes"],
    summary="Get all fitness classes",
    operation_id="getAllClasses"
)
async def get_classes(timezone: str = "Asia/Kolkata"):
    classes = await crud.get_all_classes()
    return [utils.convert_class_timezone(cls, timezone) for cls in classes]

# ✅ Book a class using numeric `class_id`
@app.post(
    "/book",
    response_model=models.Booking,
    tags=["Bookings"],
    summary="Book a fitness class",
    operation_id="bookClass"
)
async def book_class(booking: models.BookingRequest):
    return await crud.create_booking(booking)

# ✅ Retrieve all bookings by client email
@app.get(
    "/bookings",
    response_model=List[models.Booking],
    tags=["Bookings"],
    summary="Get user bookings by email",
    operation_id="getUserBookings"
)
async def get_user_bookings(email: str):
    return await crud.get_bookings_by_email(email)

# ✅ Signup request model
class SignupRequest(BaseModel):
    email: str
    password: str
    name:str
class LoginRequest(BaseModel):
    email: str
    password: str
# ✅ Signup endpoint
@app.post(
    "/signup",
    tags=["User"],
    summary="User signup",
    operation_id="signupUser"
)
async def signup(request: SignupRequest):
    return await crud.signup_user(request.email, request.password,request.name)

@app.post("/login")
async def login(request: LoginRequest):
    return await crud.login_user(request.email, request.password)