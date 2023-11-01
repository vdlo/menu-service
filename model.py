from typing import Optional, Dict, List, Union
from pydantic import BaseModel


class Company(BaseModel):
    id: int = 0
    name: str = None
    title: str = None
    description: Optional[str] = None
    workingTime: Dict[str, str] = []
    address: str = None
    phone: str = None
    geoTag: Optional[str] = None
    instagram: Optional[str] = None
    faceBook: Optional[str] = None


class Dish(BaseModel):
    id: int
    name: str
    mainImg: str
    sliderImgs: List[str] = []
    description: str
    price: int
    weight: int
    ingredients: List[str] = []
    specialMarks: List[str] = []
    isSpicy: int = 0


class Subsection(BaseModel):
    id: int
    name: str
    dishes: List[Dish] = []


class Section(BaseModel):
    id: int
    name: str
    subsections: List[Subsection] = []
    dishes: List[Dish] = []


class CompanyFullPackage(BaseModel):
    companyInfo: Company
    menu: List[Section] = []
