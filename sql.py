import json

import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from model import User, Company, Dish, Hierarchy,HierarchyItem,Section

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

    def cmsection(self, section: Section):

        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "INSERT INTO menudb.sections (id,company_id,name,parent_id,espeshial,deactivate)) "
            "VALUES (%(id)s, %(company_id)s, %(name)s, %(parent_id)s, %(espeshial)s, %(deactivate)s"
            "ON DUPLICATE KEY UPDATE "
            "company_id = %(company_id)s,"
            "name = %(name)s,"
            "parent_id = %(parent_id)s,"
            "espeshial = %(espeshial)s,"
            "deactivate = %(deactivate)s"
        )
        cursor.execute(query, section.model_dump())
        self.cnx.commit()
        result = self.getCompany(section.id)
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
        result = Hierarchy()
        query = (
            "SELECT `sections`.`id` as id,"
            "`sections`.`name` as title,"
            "`sections`.`parent_id`,"
            "`sections`.`espeshial`"
            "FROM `menudb`.`sections`"
            "where company_id=%s and parent_id is null"
        )
        cursor.execute(query, [company_id])
        fetch = cursor.fetchall()
        for gg in fetch:
            firstLevelChild = HierarchyItem(**gg)
            query = (
                "SELECT `sections`.`id` as id,"
                "`sections`.`name` as title,"
                "`sections`.`parent_id`,"
                "`sections`.`espeshial`"
                "FROM `menudb`.`sections`"
                "where  parent_id =%s"
            )
            cursor.execute(query, [int(gg['id'].replace('s',''))])
            fsub=cursor.fetchall();
            for fs in fsub:
                secondLevelSub= HierarchyItem(**fs)
                secondLevelSub.children=self.getHierarhyChilds(int(fs['id'].replace('s','')))
                firstLevelChild.children.append(secondLevelSub)
            result.dataTree.append(firstLevelChild)

        return result

    def getHierarhyChilds(self, id):
        cursor = self.cnx.cursor(dictionary=True)
        result = []
        query = (
            "SELECT id as id,"
            "name as title "
            "FROM menudb.dishes "
            "where parentId=%s"
        )
        cursor.execute(query, [id])
        fetch = cursor.fetchall()
        for gg in fetch:
            result.append(HierarchyItem(**gg))
        return result

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
