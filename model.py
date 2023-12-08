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
    img: str = None


class Dish(BaseModel):
    companyId: int = 0
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
    companyId: int = 0
    id: int
    name: str
    dishes: List[Dish] = []


class Section(BaseModel):
    companyId: int = 0
    id: int
    name: str
    deactivate: bool
    subsections: List[Subsection] = []
    dishes: List[Dish] = []


class CompanyFullPackage(BaseModel):
    companyInfo: Company
    menu: List[Section] = []


class User(BaseModel):
    name: str
    password: str = None
    hash: str = None
    companyId: int = 0


class HierarchyItem(BaseModel):
    id: int
    title: str
    children: List = []


class Hierarchy(BaseModel):
    dataTree : List[HierarchyItem] = []
