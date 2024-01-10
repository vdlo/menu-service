import os

import uuid
from typing import Optional, Dict, List, Type
import subprocess
import asyncio

from hashlib import sha1
import hmac
from model import Company, Section, Dish, CompanyFullPackage, Subsection, User, Hierarchy, HierarchyItem, \
    ServiceResponce, Payment, SortingPacket, Promo
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Request, Header
from pydantic import BaseModel
from sql import MenuSQL
from passlib.context import CryptContext
from jwtA import create_jwt_token, verify_jwt_token
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import telegram_bot as tg
# back
PROJECT_PATH_BACK = "/opt/menu-service"
PROJECT_PATH_FRONT = "/opt/menu-service_v1"
# front
GITHUB_WEBHOOK_SECRET_BACK = "back487318"
GITHUB_WEBHOOK_SECRET_FRONT = "front487318"
IMAGEDIR = "/opt/menu-service/images/"
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
        raise HTTPException(status_code=401, detail="Invalid token")
    sql = MenuSQL()
    user = sql.get_user(decoded_data["sub"])  # Получите пользователя из базы данных

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/admin/update_token")
def get_user_me(userIn: User = Depends(get_current_user)):
    jwt_token = create_jwt_token({"sub": userIn.name}, EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME,
            "update_time": datetime.now() + EXPIRATION_TIME - timedelta(seconds=10),
            'company_id': userIn.companyId}


@app.post("/admin/token")
def authenticate_user(user_in: User):
    sql = MenuSQL()
    user = sql.get_user(user_in.name)  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(user_in.password, user.hash)

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Incorrect username or passwordd")
    if user.admin:
        asyncio.run(tg.send_message(f'Login by administrator: username - {user.name}'))
    jwt_token = create_jwt_token({"sub": user.name}, EXPIRATION_TIME=EXPIRATION_TIME)
    return {"access_token": jwt_token, "token_type": "bearer", "maxAge": EXPIRATION_TIME,
            "update_time": datetime.now() + EXPIRATION_TIME - timedelta(seconds=10),
            'company_id': user_in.companyId}


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

@app.post("/admin/create_modify_promo")  # "/admin/cmdish"
async def create_modify_promo(promo: Promo, current_user: User = Depends(get_current_user)):
    promo.company_id = current_user.companyId
    sql = MenuSQL()
    return sql.create_modify_promo(promo)

@app.get("/admin/get_promo_list")  # "/admin/getdishes"
async def get_promo_list(current_user: User = Depends(get_current_user)) -> List[Promo]:
    sql = MenuSQL()
    return sql.get_promo_list(current_user.companyId)

@app.get("/admin/get_dishes")  # "/admin/getdishes"
async def get_dishes(current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.get_dishes(current_user.companyId)


@app.get("/admin/get_dish")  # "/admin/getdish"
async def get_dish(id: int, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    dish = sql.get_dish(id)
   # return this function
    if dish.companyId != current_user.companyId:
        raise HTTPException(status_code=403, detail=f'Your company haven\'t dish with id {id}')
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

@app.post("/admin/update_dish_sort")
async def update_dish_sort(element: SortingPacket, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.update_dish_sort(element)

@app.post("/admin/update_promo_sort")
async def update_dish_sort(element: SortingPacket, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.update_dish_sort(element)

@app.post("/admin/update_section_sort",)
async def update_promo_sort(element: SortingPacket, current_user: User = Depends(get_current_user)):
    sql = MenuSQL()
    return sql.update_promo_sort(element)

@app.post("/admin/upload_file/")
async def create_upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)) -> Dict[str, str]:
    try:
        # Генерация нового имени файла
        file.filename = f"{uuid.uuid4()}.jpg"
        contents = await file.read()

        # Создание каталога, если он не существует
        os.makedirs(IMAGEDIR, exist_ok=True)

        # Сохранение файла
        with open(os.path.join(IMAGEDIR, file.filename), "wb") as f:
            f.write(contents)

        return {"filename": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


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


@app.post("/support/webhook_back", include_in_schema=False)
async def webhook_back(
        request: Request,
        X_Hub_Signature: Optional[str] = Header(None),
):
    data = await request.json()
    event = request.headers.get("X-GitHub-Event")

    # Получаем данные тела запроса в формате bytes
    payload = await request.body()

    # Проверяем подлинность запроса с использованием секрета
    verify_webhook_signature(payload, X_Hub_Signature, GITHUB_WEBHOOK_SECRET_BACK)

    if event == "push":
        # Переходим в рабочий каталог
        os.chdir(PROJECT_PATH_BACK)
        current_directory = os.getcwd()
        print(f"Current Directory: {current_directory}")
        # Обновление вашего проекта при каждом push в репозиторий !!
        subprocess.run(["git", "pull", "origin", "master"])
        # Перезапуск службы
        subprocess.run(["sudo", "systemctl", "restart", "menu-back.service"])

        return {"status": "OK"}

    raise HTTPException(status_code=200, detail=f"Not a push event: {event}")


@app.post("/support/webhook_front", include_in_schema=False)
async def webhook_front(
        request: Request,
        X_Hub_Signature: Optional[str] = Header(None),
):
    data = await request.json()
    event = request.headers.get("X-GitHub-Event")

    payload = await request.body()

    verify_webhook_signature(payload, X_Hub_Signature, GITHUB_WEBHOOK_SECRET_FRONT)

    if event == "push":
        # Переходим в рабочий каталог
        os.chdir(PROJECT_PATH_FRONT)
        current_directory = os.getcwd()
        print(f"Current Directory: {current_directory}")

        # Обновляем код из репозитория
        subprocess.run(["git", "pull", "origin", "master"])

         # Перезапускаем приложение через systemctl
        subprocess.run(["sudo", "systemctl", "restart", "menu_service_front.service"])

    return {"status": "OK"}

    raise HTTPException(status_code=200, detail=f"Not a push event: {event}")


def verify_webhook_signature(payload: bytes, signature: str, secret: str):
    # Получаем хеш HMAC-SHA1
    expected_signature = "sha1=" + hmac.new(secret.encode(), payload, sha1).hexdigest()

    # Сравниваем ожидаемую подпись с полученной от GitHub
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid GitHub Webhook signature")


@app.get("/{link}")
async def get_company_data(link: str, ) -> CompanyFullPackage:


    try:
        sql_instance = MenuSQL()
        result = sql_instance.get_company_data(link)
        return result
    except HTTPException:
        # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


