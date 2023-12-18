import uuid
from typing import Optional, Dict, List
from model import Company, Section, Dish, CompanyFullPackage, Subsection, User, Hierarchy, HierarchyItem
from fastapi import FastAPI, HTTPException, Depends,File, UploadFile
from pydantic import BaseModel
from sql import MenuSQL
from passlib.context import CryptContext
from jwtA import create_jwt_token, verify_jwt_token
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

IMAGEDIR = "images/"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
app = FastAPI()

origins = ["*"]
EXPIRATION_TIME = timedelta(seconds=86400)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    sql = MenuSQL()
    user = sql.getUser(decoded_data["sub"])  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@app.get("/users/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin/update_token")
def get_user_me(userIn: User = Depends(get_current_user)):

    jwt_token = create_jwt_token({"sub": userIn.name}, EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME, "update_time": datetime.now()+EXPIRATION_TIME-timedelta(seconds=10),
            'company_id': userIn.companyId}

@app.post("/admin/token")
def authenticate_user(userIn:User):
    sql = MenuSQL()
    user = sql.getUser(userIn.name)  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(userIn.password, user.hash)

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or passwordd")
    jwt_token = create_jwt_token({"sub": user.name},EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME, "update_time": datetime.now()+EXPIRATION_TIME-timedelta(seconds=10),
            'company_id': userIn.companyId}
@app.get("/admin/getcompany")
async def GetCompany(current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.getCompany(current_user.companyId)


@app.post("/admin/cmcompany")
async def createModifyCompany(company: Company, current_user: User = Depends(get_current_user)):
    if not company.id == current_user.companyId:
        raise HTTPException(status_code=400, detail="Incorrect user identification")
    sql = MenuSQL()
    return sql.cmcompany(company)


@app.post("/admin/cmsection")
async def createModifySection(section_in: Section, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.cmsection(section_in)

@app.post("/admin/cmdish")
async def createModifyDish(dish: Dish, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.cmDish(dish)

@app.get("/admin/getdishes")
async def GetDishes(current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.getDishes(current_user.companyId)

@app.get("/admin/getdish")
async def GetDishes(id: int, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.getDish(id)

@app.get("/admin/getdishtree")
async def GetDishTree(current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.getDishTree(1)

@app.post("/admin/set_section_activity")
async def set_section_activity(id, active, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.set_section_activity(id,active)

@app.post("/admin/set_dish_activity")
async def set_dish_activity(id, active, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.set_dish_activity(id, active)
@app.post("/admin/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    # save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}

@app.get("/")
async def root():
    sql = MenuSQL()
    res = sql.getUser("admind")
    # newUser=User(name='admin',hash="dfsfsdfsdfsdf")
    # res=sql.newUser(newUser)
    return res


@app.post("/signup")
async def signUp(name: str, password: str):
    sql = MenuSQL()
    if sql.getUser(name=name):
        raise HTTPException(status_code=400, detail="Nickname is busy")
    hashed_password = pwd_context.hash(password)
    newUser = sql.newUser(User(name=name, hash=hashed_password))
    return newUser




@app.get("/{name}")
async def cetCompanyMenu(name: str) -> CompanyFullPackage:
    company = Company()
    company.id = 1
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
    dish = Dish(id=1, name="Meet", mainImg="some-link.jpg",
                description="Text about this dish. What the composition and blah dish. What the and blah blah blah",
                price=345, weight=13, )
    fish = Dish(id=2, name="fish", mainImg="some-link.jpg",
                description="Text about this dish. What the composition and blah dish. What the and blah blah blah",
                price=345, weight=13, )
    drink = Dish(id=3, name="drink", mainImg="some-link.jpg",
                 description="Text about this dish. What the composition and blah dish. What the and blah blah blah",
                 price=345, weight=13, )
    speshial = Dish(id=4, name="especial", mainImg="some-link.jpg",
                    description="Text about this dish. What the composition and blah dish. What the and blah blah blah",
                    price=345, weight=13, )

    food = Section(id=1, name="FOOD")
    drinkSS = Section(id=2, name="DRINK")
    Espesials = Section(id=3, name="ESPECIALS")
    speshials = Subsection(id=8, name="Espeshials")
    meet = Subsection(id=1, name="meet")
    for i in range(10):
        meet.dishes.append(dish)
    fishS = Subsection(id=2, name="fish")
    for i in range(10):
        fishS.dishes.append(fish)
    drinkS = Subsection(id=3, name="drink")
    for i in range(10):
        fishS.dishes.append(drink)
    food.subsections.append(meet)
    food.subsections.append(fishS)
    drinkSS.subsections.append(drinkS)

    for i in range(10):
        speshials.dishes.append(speshial)
    Espesials.subsections.append(speshials)

    result = CompanyFullPackage(companyInfo=company)
    result.menu.append(food)
    result.menu.append(drinkSS)
    result.menu.append(Espesials)

    return result
