from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from rag import ai, User

# Initialize FastAPI app
app = FastAPI()

# CORS configuration for Streamlit client
origins = ["http://localhost:8501", "http://127.0.0.1:8501"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# dummy user
user1 = User(
    id="1",
    name="Karthikeya",
    age=19,
    gender="male",
    height=174,
    weight=75,
    diet_type=["mediterranean", "keto"],
    cuisine=["indian", "asian"],
    allergies=["beef", "nuts"],
    calorie_goal=3500
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Diet Plan Generator API"}


@app.post("/generate")
async def generate_dietplan(user_profile: User):
    try:
        response = ai.generate_response(user_profile)
        if response is None:
            raise HTTPException(
                status_code=500, detail="Failed to generate diet plan")
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regenerate")
async def regenerate_diet_plan(query: str, user_profile: User, prev_response: dict):
    try:
        response = ai.regenerate_response(query, user_profile, prev_response)
        if response is None:
            raise HTTPException(
                status_code=500, detail="Failed to regenerate diet plan")
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ai, host="localhost", port=8080, reload=True)
