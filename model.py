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
    link: str = ''
    color_theme: str = 'green'


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
    sort: int = 0


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
    sort: int = 0


class Promo(BaseModel):
    id: int = 0
    img: str = ''
    text: str = ''
    active: int = 1
    sort: int = 0
    type: int = 0
    company_id: int = 0


class CompanyFullPackage(BaseModel):
    companyInfo: Company
    menu: List[Section] = []
    promo: List[Promo] = []

class User(BaseModel):
    name: str
    password: str = None
    hash: str = None
    companyId: int = 0
    admin: bool = 0


class HierarchyItem(BaseModel):
    id: int
    title: str
    price: float = 0
    children: List = []
    active: bool
    sort: int
    espeshial: bool = False


class Hierarchy(BaseModel):
    dataTree: List[HierarchyItem] = []


class ServiceResponce(BaseModel):
    result: bool = True
    description: str = ''
    data: Dict = {}


class Payment(BaseModel):
    tariff: int
    months: int
    company_id: int
    user_name: str = ''


class SortingPacket(BaseModel):
    id: int
    direction: int


class CustomerRequest(BaseModel):
    id: Optional[int]
    customer_name: str
    email: str
    phone: str
    password: str  # Предполагается, что пароль будет хеширован до записи
    company_name: str

class GptPromt(BaseModel):
    promt: str
    theme: str