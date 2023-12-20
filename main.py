import uuid
from typing import Optional, Dict, List, Type
from model import Company, Section, Dish, CompanyFullPackage, Subsection, User, Hierarchy, HierarchyItem, \
    ServiceResponce, Payment
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
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
    user = sql.get_user(decoded_data["sub"])  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@app.get("/users/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/admin/update_token")
def get_user_me(userIn: User = Depends(get_current_user)):
    jwt_token = create_jwt_token({"sub": userIn.name}, EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME,
            "update_time": datetime.now() + EXPIRATION_TIME - timedelta(seconds=10),
            'company_id': userIn.companyId}


@app.post("/admin/token")
def authenticate_user(userIn: User):
    sql = MenuSQL()
    user = sql.get_user(userIn.name)  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(userIn.password, user.hash)

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or passwordd")
    jwt_token = create_jwt_token({"sub": user.name}, EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME,
            "update_time": datetime.now() + EXPIRATION_TIME - timedelta(seconds=10),
            'company_id': userIn.companyId}


@app.get("/admin/get_company")  # "/admin/getcompany"
async def get_company(current_user: User = Depends(get_current_user)):

    sql = MenuSQL()
    return sql.get_company(current_user.companyId)


@app.post("/admin/create_modify_company")  # "/admin/cmcompany"
async def create_modify_company(company: Company, current_user: User = Depends(get_current_user)):

    company.id = current_user.companyId
    sql = MenuSQL()
    return sql.create_modify_company(company)


@app.post("/admin/create_modify_section")  # "/admin/cmsection"
async def create_modify_section(section_in: Section, current_user: User = Depends(get_current_user)):

    section_in.companyId = current_user.companyId
    sql = MenuSQL()
    return sql.create_modify_section(section_in)


@app.post("/admin/create_modify_dish")  # "/admin/cmdish"
async def create_modify_dish(dish: Dish, current_user: User = Depends(get_current_user)):

    dish.companyId = current_user.companyId
    sql = MenuSQL()
    return sql.create_modify_dish(dish)


@app.get("/admin/get_dishes")  # "/admin/getdishes"
async def get_dishes(current_user: User = Depends(get_current_user)):

    sql = MenuSQL()
    return sql.get_dishes(current_user.companyId)


@app.get("/admin/get_dish")  # "/admin/getdish"
async def get_dish(id: int, current_user: User = Depends(get_current_user)):

    sql = MenuSQL()
    dish = sql.get_dish(id)
    if dish.companyId != current_user:
        raise Exception(f'Your company haven\'t dish with id {id}')
    return dish


@app.get("/admin/get_dish_tree")  # "/admin/getdishtree"
async def get_dish_tree(current_user: User = Depends(get_current_user)):

    sql = MenuSQL()
    return sql.get_dish_tree(current_user.companyId)


@app.post("/admin/set_section_activity")
async def set_section_activity(id, active, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.set_section_activity(id, active, current_user.companyId)


@app.post("/admin/set_dish_activity")
async def set_dish_activity(id, active, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.set_dish_activity(id, active, current_user.companyId)


@app.post("/admin/upload_file/")  # "/admin/uploadfile/"
async def create_upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    # save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}


@app.post("/support/add_user")  # "/signup"
async def sign_up(name: str, password: str, company_id: int = 0, current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Function only for administrators")
    sql = MenuSQL()
    if sql.get_user(name=name):
        raise HTTPException(status_code=400, detail="Nickname is busy")
    hashed_password = pwd_context.hash(password)
    new_user = sql.new_user(User(name=name, hash=hashed_password, companyId=company_id))
    return new_user

@app.post("/support/add_payment")
async def add_payment(payment: Payment, current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="Function only for administrators")
    sql = MenuSQL()
    sql.add_payment(current_user.name, payment)



@app.get("/{link}")
async def get_company_data(link: str,) -> ServiceResponce:
    result = ServiceResponce()

    try:
        sql_instance = MenuSQL()
        result.data['company_data'] = sql_instance.get_company_data(link)
        if not sql_instance.check_payment_status(result.data['company_data'].companyInfo.id):
            result.data.clear()
            result.result = False
            result.description = 'Company disabled'
    except Exception as e:
        result.result = False
        result.description = str(e)

    return result

