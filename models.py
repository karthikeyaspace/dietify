from pydantic import BaseModel
from typing import List


class User(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    height: int
    weight: int
    diet_type: List[str]
    cuisine: List[str]
    allergies: List[str] | None
    calorie_goal: int
