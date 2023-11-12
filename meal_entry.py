from pydantic import BaseModel
from datetime import datetime

class MealEntry(BaseModel):

    recipe_name: str
    date: datetime
    task_id: str = None
    meal: str = None