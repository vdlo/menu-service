import json

import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from model import User, Company, Dish

config = {
    'user': 'admin',
    'password': 'RhceDL!2',
    'host': 'menu-service.me',
    'database': 'menudb',
    'raise_on_warnings': True
}


class MenuSQL():
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)

    def __del__(self):
        self.cnx.close()

    def getCompany(self, id):
        cursor = self.cnx.cursor(dictionary=True)

        query = ("SELECT * FROM menudb.company "
                 "where id=%s")
        cursor.execute(query, [id])

        gg = cursor.fetchone()
        if not gg:
            return gg
        result = Company(**gg)
        return result

    def cmcompany(self, company: Company):
        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "INSERT INTO menudb.company (id, name, description, title, address, phone, geoTag, instagram, faceBook, img) "
            "VALUES (%(id)s, %(name)s, %(description)s, %(title)s, %(address)s, %(phone)s, "
            "%(geoTag)s, %(instagram)s, %(faceBook)s, %(img)s) "
            "ON DUPLICATE KEY UPDATE "
            "name = %(name)s,"
            "description = %(description)s,"
            "title = %(title)s,"
            "address = %(address)s,"
            "phone = %(phone)s,"
            "geoTag = %(geoTag)s,"
            "instagram = %(instagram)s,"
            "faceBook = %(faceBook)s,"
            "img = %(img)s"
        )
        cursor.execute(query, company.model_dump(exclude=['workingTime']))
        self.cnx.commit()
        result = self.getCompany(company.id)
        return result

    def getDishes(self, id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * from menudb.dishes "
                 "where company_id=%s")
        cursor.execute(query, [id])
        fetch = cursor.fetchall()
        result = []
        for gg in fetch:
            result.append(Dish(**gg))
        return result

    def cmDish(self, dish: Dish):
        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "INSERT INTO  "
        )

    def getDishTree(self, company_id):
        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "WITH RECURSIVE SectionTree AS ("
            "SELECT "
            "id, "
            "name AS title,"
            "parent_id "
            "FROM "
            "    sections "
            "UNION ALL "
            "SELECT "
            "d.id, "
            "d.name, "
            "d.parentId "
            "FROM "
            "dishes AS d "
            "JOIN "
            "SectionTree AS st ON d.parentId = st.id "
            ") "
            "SELECT "
            "    id, "
            "title, "
            "parent_id "
            "FROM "
            "SectionTree "
        )

        cursor.execute(query)
        result = cursor.fetchall()

        # Преобразование результата в JSON
        return  json.dumps(result, ensure_ascii=False, indent=2)

    def getUser(self, name: str):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT name,hash,companyId from menudb.users "
                 "where name=%s")
        cursor.execute(query, [name])
        gg = cursor.fetchone()
        if not gg:
            return gg
        result = User(**gg)
        return result

    def newUser(self, user: User):
        cursor = self.cnx.cursor()
        query = ("INSERT INTO menudb.users"
                 "(name,hash,companyId)"
                 " VALUES (%(name)s, %(hash)s, %(companyId)s)")
        cursor.execute(query, user.model_dump())
        self.cnx.commit()
        result = self.getUser(user.name)
        return result
