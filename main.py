from typing import Optional, Dict, List
from model import Company,Section,Dish
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()





class Menu(BaseModel):
    company: str
    sections: List[Section]


class Dish(BaseModel):
    dishName: str
    mainImg: str
    sliderImgs: List[str] = []
    subsectionId: int
    description: str
    price: int
    weight: int
    ingredients: List[str] = []
    specialMarks: List[str] = []
    isSpicy: int = 0
    parentSectionId: int


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/{name}")
async def getCompany(name: str)->Company:
    company = Company()
    company.name = name
    company.title = "Simple title, base "
    company.workingTime = {"Sunday": "10:00-22:00",
                           "Monday": "10:00-22:00",
                           "Tuesday": "10:00-22:00",
                           "Wednesday": "10:00-22:00",
                           "Thursday": "10:00-22:00",
                           "Friday": "10:00-22:00",
                           "Saturday": "10:00-22:00"}
    company.address = "Radanovici, Черногория"
    company.geoTag = "42.3487998848943, 18.767679742284034"
    company.phone = "+38269877678"
    company.instagram = "www.instagram.com/dfdfs"
    company.sections = {"food": 3, "bar": 5}
    return company


