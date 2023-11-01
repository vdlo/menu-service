from typing import Optional, Dict, List
from pydantic import BaseModel

class Company(BaseModel):
    name: str = None
    title: str = None
    description: Optional[str] = None
    workingTime: Dict[str, str] = []
    address: str = None
    phone: str = None
    geoTag: Optional[str] = None
    instagram: Optional[str] = None
    faceBook: Optional[str] = None


class Section(BaseModel):
    id: int
    sectionName: str
    firstLevel: bool

class Dish(BaseModel):
    name: str
    mainImg: str
    sliderImgs: List[str] = []
    parentId: int
    description: str
    price: int
    weight: int
    ingredients: List[str] = []
    specialMarks: List[str] = []
    isSpicy: int = 0
