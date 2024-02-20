from datetime import datetime
from typing import Optional, Dict, List, Union
from pydantic import BaseModel


class Company(BaseModel):
    id: Optional[int] = None
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
    phone_number: str = None
    email: str = None
    full_name: str = None


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
    customer_name: str
    email: str
    phone: str
    password: str  # Предполагается, что пароль будет хеширован до записи
    company_name: str
    company_link: Optional[str] = None

class GptPromt(BaseModel):
    promt: str
    theme: str

class OrderBasketItem(BaseModel):
    id: Optional[int] = None
    dish_id: int
    count: int
    sum: int

class Order(BaseModel):
    id: Optional[int] = None
    customer_name : str
    custumer_email: Optional[str] = None
    customer_id: Optional[int] = None
    customer_phone: Optional[str] = None
    customer_channel: Optional[str] = None
    adress: Optional[str] = None
    geo_tag: Optional[str] = None
    delivery_type: Optional[str] = None
    delivery_time_start: Optional[datetime] = None
    delivery_time_end: Optional[datetime] = None
    status: str
    comment: Optional[str] = None
    delivery_price: float
    basket: List[OrderBasketItem] = []
