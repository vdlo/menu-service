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
    id: int = None
    name: str
    mainImg: str
    sliderImgs: List[str] = []
    description: str
    price: float
    weight: int
    ingredients: List[str] = []
    specialMarks: List[str] = []
    isSpicy: int = 0
    parentId: int = 0
    active: bool = True


class Subsection(BaseModel):
    companyId: int = 0
    id: int
    name: str
    dishes: List[Dish] = []


class Section(BaseModel):
    companyId: int = 0
    id: int = 0
    name: str
    active: bool = True
    parent_id: int = None
    espeshial: bool = False
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
    price: float = 0
    children: List = []


class Hierarchy(BaseModel):
    dataTree: List[HierarchyItem] = []


class ServiceResponce(BaseModel):
    result: bool = True
    description: str = ''
    data: List = []
