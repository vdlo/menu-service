import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from model import User, Company, Dish, Hierarchy, HierarchyItem, Section, CompanyFullPackage, Payment

config = {
    'user': 'admin',
    'password': 'RhceDL!2',
    'host': 'menu-service.me',
    'database': 'menudb',
    'raise_on_warnings': True
}


class MenuSQL:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)

    def __del__(self):
        self.cnx.close()

    def get_company(self, id):
        cursor = self.cnx.cursor(dictionary=True)

        query = ("SELECT * FROM menudb.company "
                 "where id=%s")
        cursor.execute(query, [id])

        gg = cursor.fetchone()
        if not gg:
            return gg
        result = Company(**gg)
        return result

    def create_modify_company(self, company: Company):
        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "INSERT INTO menudb.company (id, name, description, title, address, phone, geoTag, instagram, faceBook, "
            "img)"
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
        result = self.get_company(company.id)
        return result

    def create_modify_section(self, section: Section):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "INSERT INTO menudb.sections (id, company_id, name, parent_id, espeshial) "
                "VALUES (%(id)s, %(companyId)s, %(name)s, %(parent_id)s, %(espeshial)s) "
                "ON DUPLICATE KEY UPDATE "
                "company_id = %(companyId)s,"
                "name = %(name)s,"
                "parent_id = %(parent_id)s,"
                "espeshial = %(espeshial)s"
            )
            cursor.execute(query, section.model_dump(exclude=['subsections', 'dishes']))
            self.cnx.commit()
            result = 'ok'
            return result
        except Exception as e:
            return str(e)

    def get_dishes(self, id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * from menudb.dishes "
                 "where company_id=%s")
        cursor.execute(query, [id])
        fetch = cursor.fetchall()
        result = []
        for gg in fetch:
            result.append(Dish(**gg))
        return result

    def create_modify_dish(self, dish: Dish):
        cursor = self.cnx.cursor(dictionary=True)
        query = (
            "INSERT INTO menudb.dishes (id, name, mainImg, description, price, weight, isSpicy, parentId, companyId, active) "
            "VALUES (%(id)s, %(name)s, %(mainImg)s, %(description)s, %(price)s, %(weight)s, %(isSpicy)s, "
            "%(parentId)s, %(companyId)s, %(active)s) "
            "ON DUPLICATE KEY UPDATE "
            "description = %(description)s, "
            "name = %(name)s, "
            "mainImg = %(mainImg)s, "
            "price = %(price)s, "
            "weight = %(weight)s, "
            "isSpicy = %(isSpicy)s, "
            "parentId = %(parentId)s, "
            "companyId = %(companyId)s, "
            "active = %(active)s"
        )
        cursor.execute(query, dish.model_dump(exclude=['sliderImgs', 'ingredients', 'specialMarks']))
        self.cnx.commit()
        result = self.get_dish(cursor.lastrowid)
        return result

    def get_dish(self, id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM menudb.dishes "
                 "where id=%s")
        cursor.execute(query, [id])
        gg = cursor.fetchone()
        if not gg:
            return gg
        result = Dish(**gg)
        return result

    def get_dish_tree(self, company_id):
        cursor = self.cnx.cursor(dictionary=True)
        result = Hierarchy()
        query = (
            "SELECT `sections`.`id` as id,"
            "`sections`.`name` as title,"
            "`sections`.`parent_id`,"
            "`sections`.`active`,"
            "`sections`.`espeshial`"
            "FROM `menudb`.`sections`"
            "where company_id=%s and (parent_id is null or parent_id=0)"
        )
        cursor.execute(query, [company_id])
        fetch = cursor.fetchall()
        for gg in fetch:
            first_level_child = HierarchyItem(**gg)
            query = (
                "SELECT `sections`.`id` as id,"
                "`sections`.`name` as title,"
                "`sections`.`parent_id`,"
                "`sections`.`active`,"
                "`sections`.`espeshial`"
                "FROM `menudb`.`sections`"
                "where  parent_id =%s"
            )
            cursor.execute(query, [gg['id']])
            fsub = cursor.fetchall()
            for fs in fsub:
                second_level_sub = HierarchyItem(**fs)
                second_level_sub.children = self.get_hierarhy_childs(fs['id'])
                first_level_child.children.append(second_level_sub)
            result.dataTree.append(first_level_child)

        return result

    def get_hierarhy_childs(self, id):
        cursor = self.cnx.cursor(dictionary=True)
        result = []
        query = (
            "SELECT id as id,"
            "name as title, "
            "active as active, "
            "IFNULL(price, 0) as price "
            "FROM menudb.dishes "
            "where parentId=%s"
        )
        cursor.execute(query, [id])
        fetch = cursor.fetchall()
        for gg in fetch:
            result.append(HierarchyItem(**gg))
        return result

    def get_user(self, name: str):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT name,hash,companyId, admin from menudb.users "
                 "where name=%s")
        cursor.execute(query, [name])
        gg = cursor.fetchone()
        if not gg:
            return gg
        result = User(**gg)
        return result

    def new_user(self, user: User):
        cursor = self.cnx.cursor()
        query = ("INSERT INTO menudb.users"
                 "(name,hash,companyId)"
                 " VALUES (%(name)s, %(hash)s, %(companyId)s)")
        cursor.execute(query, user.model_dump())
        self.cnx.commit()
        result = self.get_user(user.name)
        return result

    def set_section_activity(self, id, active, company_id):
        cursor = self.cnx.cursor()
        query = ('\n'
                 '        UPDATE menudb.sections\n'
                 '        SET\n'
                 '        active = %(active)s\n'
                 '        WHERE id = %(id)s\n'
                 '        and company_id = %(company_id)s\n'
                 '        ')
        cursor.execute(query, {'id': id, 'active': active, 'company_id': company_id})
        self.cnx.commit()

    def set_dish_activity(self, id, active, company_id):
        cursor = self.cnx.cursor()
        query = ('\n'
                 '        UPDATE menudb.dishes\n'
                 '        SET\n'
                 '        active = %(active)s\n'
                 '        WHERE id = %(id)s\n'
                 '        and companyId = %(company_id)s\n'
                 '        ')
        cursor.execute(query, {'id': id, 'active': active, 'company_id': company_id})
        self.cnx.commit()

    def get_company_by_link(self, link: str):

        cursor = self.cnx.cursor(dictionary=True)
        query = ('SELECT * FROM menudb.company\n'
                 'where link = %s')
        cursor.execute(query, [link])
        gg = cursor.fetchone()
        if not gg:
            return False
        result = Company(**gg)
        return result

    def get_company_data(self, link: str):
        company_info = self.get_company_by_link(link)
        if not company_info:
            raise Exception('Company not found')

        result = CompanyFullPackage(companyInfo=company_info)
        result.menu = self.__get_sections(result.companyInfo.id)
        for section in result.menu:
            section.subsections = self.__get_subsections(section.id)
            for subsection in section.subsections:
                subsection.dishes = self.__get_dishes(subsection.id)

        return result

    def __get_sections(self, company_id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ('SELECT * FROM menudb.sections\n'
                 'where ifnull(parent_id,0) = 0 \n'
                 'and company_id = %s')
        cursor.execute(query, [company_id])
        fetch = cursor.fetchall()
        result = []
        for gg in fetch:
            result.append(Section(**gg))

        return result

    def __get_subsections(self, parent_id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ('SELECT * FROM menudb.sections\n'
                 'where ifnull(parent_id,0) =  %s')
        cursor.execute(query, [parent_id])
        fetch = cursor.fetchall()
        result = []
        for gg in fetch:
            result.append(Section(**gg))

        return result

    def __get_dishes(self, parent_id):
        cursor = self.cnx.cursor(dictionary=True)
        query = ('SELECT * FROM menudb.dishes\n'
                 'where parentId = %s')
        cursor.execute(query, [parent_id])
        fetch = cursor.fetchall()
        result = []
        for gg in fetch:
            result.append(Dish(**gg))

        return result

    def add_payment(self, user_name, payment: Payment):
        payment_sum = payment.tariff * payment.months
        expiration_date = datetime.now().date() + timedelta(days=payment.months * 30)

        cursor = self.cnx.cursor()
        query = ("INSERT INTO menudb.billing "
                 "(companyId, payment, tariff, expiration_date, user_name) "
                 "VALUES (%(companyId)s, %(payment)s, %(tariff)s, %(expiration_date)s, %(user_name)s)")
        cursor.execute(query, {"companyId": payment.company_id, 'payment': payment_sum, 'tariff': payment.tariff,
                               'expiration_date': expiration_date, 'user_name': user_name})
        self.cnx.commit()

    def check_payment_status(self, company_id):
        cursor = self.cnx.cursor()
        query = ("SELECT MAX(expiration_date) FROM menudb.billing "
                 "WHERE companyId = %(companyId)s")
        cursor.execute(query, {"companyId": company_id})
        result = cursor.fetchone()

        if result and result[0] is not None:
            max_expiration_date = result[0].date()
            current_date = datetime.now().date()
            return current_date <= max_expiration_date
        else:
            # Возвращаем False, если запись не найдена или expiration_date равен None
            return False