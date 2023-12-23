import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from fastapi import HTTPException
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
            raise HTTPException(status_code=404, detail=f'Company not found')
        result = Company(**gg)
        return result

    def create_modify_company(self, company: Company):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "INSERT INTO menudb.company (id, name, description, title, address, phone, geoTag, instagram, faceBook, img) "
                "VALUES (%(id)s, %(name)s, %(description)s, %(title)s, %(address)s, %(phone)s, "
                "%(geoTag)s, %(instagram)s, %(faceBook)s, %(img)s) "
                "ON DUPLICATE KEY UPDATE "
                "name = %(name)s, "
                "description = %(description)s, "
                "title = %(title)s, "
                "address = %(address)s, "
                "phone = %(phone)s, "
                "geoTag = %(geoTag)s, "
                "instagram = %(instagram)s, "
                "faceBook = %(faceBook)s, "
                "img = %(img)s"
            )
            cursor.execute(query, company.model_dump(exclude=['workingTime']))
            self.cnx.commit()

            # Получаем обновленные данные компании
            result = self.get_company(company.id)
            return result

        except Exception as e:
            # Возвращаем информацию об ошибке
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    def create_modify_section(self, section: Section):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Проверка на существование секции с таким же наименованием и company_id
            check_query = (
                "SELECT id FROM menudb.sections "
                "WHERE name = %(name)s AND company_id = %(companyId)s"
            )
            params = {'name': section.name, 'companyId': section.companyId}

            # Если мы обновляем существующую секцию, исключаем её из проверки
            if section.id:
                check_query += " AND id <> %(id)s"
                params['id'] = section.id

            cursor.execute(check_query, params)
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Section name is busy")

            # Вставка или обновление секции
            query = (
                "INSERT INTO menudb.sections (id, company_id, name, parent_id, espeshial) "
                "VALUES (%(id)s, %(companyId)s, %(name)s, %(parent_id)s, %(espeshial)s) "
                "ON DUPLICATE KEY UPDATE "
                "company_id = %(companyId)s, "
                "name = %(name)s, "
                "parent_id = %(parent_id)s, "
                "espeshial = %(espeshial)s"
            )
            cursor.execute(query, section.model_dump(exclude=['subsections', 'dishes']))
            self.cnx.commit()

            # Получение id секции после вставки/обновления
            section_id = section.id if section.id else cursor.lastrowid

            # Получение и возврат обновленных данных секции
            fetch_query = "SELECT * FROM menudb.sections WHERE id = %s"
            cursor.execute(fetch_query, (section_id,))
            fetched_data = cursor.fetchone()

            if fetched_data:
                return Section(**fetched_data)

            raise HTTPException(status_code=500, detail="Ошибка при создании или обновлении секции.")

        except Exception as e:
            raise HTTPException(status_code=500, detail=e.detail)

    def get_dishes(self, id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT * FROM menudb.dishes WHERE company_id = %s"
            cursor.execute(query, [id])
            fetch = cursor.fetchall()

            result = [Dish(**gg) for gg in fetch]
            return result

        except Exception as e:
            # Обработка исключений, связанных с базой данных
            raise HTTPException(status_code=500, detail=str(e))

    def create_modify_dish(self, dish: Dish):
        try:
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

            # Получение и возврат обновленных данных блюда
            result = self.get_dish(cursor.lastrowid if not dish.id else dish.id)
            return result

        except Exception as e:
            # Обработка исключений, связанных с базой данных
            raise HTTPException(status_code=500, detail=str(e))

    def get_dish(self, id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT * FROM menudb.dishes WHERE id = %s"
            cursor.execute(query, [id])
            dish_data = cursor.fetchone()

            if not dish_data:
                raise HTTPException(status_code=500, detail="Dish not found")

            return Dish(**dish_data)

        except Exception as e:
            # Обработка исключений, связанных с базой данных
            raise HTTPException(status_code=500, detail=str(e))

    def get_dish_tree(self, company_id):
        try:
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
                first_level_child.children = self.get_hierarhy_childs(gg['id'])
                result.dataTree.append(first_level_child)

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_hierarhy_childs(self, parent_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            result = []
            query = (
                "SELECT `sections`.`id` as id,"
                "`sections`.`name` as title,"
                "`sections`.`parent_id`,"
                "`sections`.`active`,"
                "`sections`.`espeshial`"
                "FROM `menudb`.`sections`"
                "where parent_id=%s"
            )
            cursor.execute(query, [parent_id])
            sections = cursor.fetchall()

            for section in sections:
                section_item = HierarchyItem(**section)
                section_item.children = self.get_hierarhy_childs(section['id'])
                result.append(section_item)

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
        try:
            cursor = self.cnx.cursor()
            query = (
                "UPDATE menudb.sections "
                "SET active = %(active)s "
                "WHERE id = %(id)s "
                "AND company_id = %(company_id)s"
            )
            cursor.execute(query, {'id': id, 'active': active, 'company_id': company_id})
            self.cnx.commit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def set_dish_activity(self, id, active, company_id):
        try:
            cursor = self.cnx.cursor()
            query = (
                "UPDATE menudb.dishes "
                "SET active = %(active)s "
                "WHERE id = %(id)s "
                "AND companyId = %(company_id)s"
            )
            cursor.execute(query, {'id': id, 'active': active, 'company_id': company_id})
            self.cnx.commit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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

    def add_payment(self, user_name, payment):
        try:
            cursor = self.cnx.cursor()

            # Получаем максимальную дату expiration_date для текущего companyId
            max_exp_date_query = ("SELECT MAX(expiration_date) FROM menudb.billing "
                                  "WHERE companyId = %(companyId)s")
            cursor.execute(max_exp_date_query, {"companyId": payment.company_id})
            max_exp_date_result = cursor.fetchone()
            last_exp_date = max_exp_date_result[0].date() if max_exp_date_result and max_exp_date_result[
                0] else datetime.now().date()

            # Вычисляем новую expiration_date
            expiration_date = last_exp_date + timedelta(days=payment.months * 30)

            # Вставляем новую запись
            insert_query = ("INSERT INTO menudb.billing "
                            "(companyId, payment, tariff, expiration_date, user_name) "
                            "VALUES (%(companyId)s, %(payment)s, %(tariff)s, %(expiration_date)s, %(user_name)s)")
            cursor.execute(insert_query, {"companyId": payment.company_id, 'payment': payment.tariff * payment.months,
                                          'tariff': payment.tariff, 'expiration_date': expiration_date,
                                          'user_name': user_name})
            self.cnx.commit()

        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=str(err))
        finally:
            cursor.close()

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
