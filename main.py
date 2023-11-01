from typing import Optional, Dict, List
from model import Company, Section, Dish, CompanyFullPackage, Subsection
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return Section(id=1, name="FOOD")


@app.post("/cmcompany")
async def createModifyCompany(company: Company):
    return company


@app.post("/cmsection")
async def createModifySection(section: Section):
    return Section


@app.post("/cmsubsection")
async def createModifySubsection(subsection: Subsection):
    return subsection


@app.post("/cmdish")
async def createModifyDish(dish: Dish):
    return dish


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
        Espesials.dishes.append(speshial)

    result = CompanyFullPackage(companyInfo=company)
    result.menu.append(food)
    result.menu.append(drinkSS)
    result.menu.append(Espesials)

    return result
