import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from fastapi import HTTPException
from model import User, Company, Dish, Hierarchy, HierarchyItem, Section, CompanyFullPackage, Payment, SortingPacket, \
    Promo

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

            if section.id:
                check_query += " AND id <> %(id)s"
                params['id'] = section.id

            cursor.execute(check_query, params)
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Section name is busy")
            section_data = section.model_dump(exclude=['subsections', 'dishes'])
            if not section.id:
                # Определение максимального значения sort
                cursor.execute("SELECT MAX(sort) as max_sort FROM menudb.sections WHERE company_id = %(companyId)s",
                               {'companyId': section.companyId})
                max_sort_result = cursor.fetchone()
                next_sort = (max_sort_result['max_sort'] if max_sort_result['max_sort'] is not None else 0) + 1

                # Вставка или обновление секции

                section_data['sort'] = next_sort  # Установка значения для sort
            query = (
                "INSERT INTO menudb.sections (id, company_id, name, parent_id, espeshial, sort) "
                "VALUES (%(id)s, %(companyId)s, %(name)s, %(parent_id)s, %(espeshial)s, %(sort)s) "
                "ON DUPLICATE KEY UPDATE "
                "company_id = %(companyId)s, "
                "name = %(name)s, "
                "parent_id = %(parent_id)s"
            )
            cursor.execute(query, section_data)
            self.cnx.commit()

            # Получение и возврат обновленных данных секции
            fetch_query = "SELECT * FROM menudb.sections WHERE id = %s"
            section_id = section.id if section.id else cursor.lastrowid
            cursor.execute(fetch_query, (section_id,))
            fetched_data = cursor.fetchone()

            if fetched_data:
                return Section(**fetched_data)

            raise HTTPException(status_code=500, detail="Ошибка при создании или обновлении секции.")

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_dishes(self, id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT * FROM menudb.dishes WHERE company_id = %s"
            cursor.execute(query, [id])
            fetch = cursor.fetchall()

            result = [Dish(**gg) for gg in fetch]
            return result
        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
        except Exception as e:
            # Обработка исключений, связанных с базой данных
            raise HTTPException(status_code=500, detail=str(e))

    def create_modify_promo(self, promo: Promo):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Получение данных промо
            promo_data = promo.dict()

            # Определение максимального значения sort, если id не задан
            if not promo_data['id']:
                cursor.execute("SELECT MAX(sort) as max_sort FROM menudb.promo WHERE type = %s", (promo.type,))
                max_sort_result = cursor.fetchone()
                next_sort = (max_sort_result['max_sort'] if max_sort_result['max_sort'] is not None else 0) + 1
                promo_data['sort'] = next_sort

            # Формирование запроса для вставки или обновления
            query = (
                "INSERT INTO menudb.promo (id, img, text, active, sort, type, company_id) "
                "VALUES (%(id)s, %(img)s, %(text)s, %(active)s, %(sort)s, %(type)s, %(company_id)s) "
                "ON DUPLICATE KEY UPDATE "
                "img = %(img)s, text = %(text)s, active = %(active)s, sort = %(sort)s, type = %(type)s, company_id = %(company_id)s"
            )

            # Выполнение запроса
            cursor.execute(query, promo_data)
            self.cnx.commit()

            # Получение и возврат обновленных данных промо
            promo_id = cursor.lastrowid if not promo.id else promo.id
            cursor.execute("SELECT * FROM menudb.promo WHERE id = %s", (promo_id,))
            result = cursor.fetchone()
            return result

        except mysql.connector.Error as db_error:
            # Обработка ошибок базы данных
            raise HTTPException(status_code=500, detail=str(db_error))

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            # Обработка других исключений
            raise HTTPException(status_code=500, detail=str(e))

    def create_modify_dish(self, dish: Dish):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Определение максимального значения sort
            dish_data = dish.model_dump(exclude=['sliderImgs', 'ingredients', 'specialMarks'])
            if not dish_data['id']:
                cursor.execute("SELECT MAX(sort) as max_sort FROM menudb.dishes WHERE parentId = %s", (dish.parentId,))
                max_sort_result = cursor.fetchone()
                next_sort = (max_sort_result['max_sort'] if max_sort_result['max_sort'] is not None else 0) + 1

                # Вставка или обновление блюда

                dish_data['sort'] = next_sort  # Установка значения для sort
            query = (
                "INSERT INTO menudb.dishes (id, name, mainImg, description, price, weight, isSpicy, parentId, companyId, active, sort) "
                "VALUES (%(id)s, %(name)s, %(mainImg)s, %(description)s, %(price)s, %(weight)s, %(isSpicy)s, "
                "%(parentId)s, %(companyId)s, %(active)s, %(sort)s) "
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
            cursor.execute(query, dish_data)
            self.cnx.commit()

            # Получение и возврат обновленных данных блюда
            result = self.get_dish(cursor.lastrowid if not dish.id else dish.id)
            return result

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_promo_list(self, company_id):
        return self.__get_promos(company_id)

    def get_dish(self, id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT * FROM menudb.dishes WHERE id = %s"
            cursor.execute(query, [id])
            dish_data = cursor.fetchone()

            if not dish_data:
                raise HTTPException(status_code=500, detail="Dish not found")

            return Dish(**dish_data)
        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
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
                "`sections`.`sort`,"
                "`sections`.`espeshial`"
                "FROM `menudb`.`sections`"
                "where company_id=%s and (parent_id is null or parent_id=0) "
                "ORDER BY sort ASC "
            )
            cursor.execute(query, [company_id])
            fetch = cursor.fetchall()

            for gg in fetch:
                first_level_child = HierarchyItem(**gg)
                if gg['espeshial']:
                    first_level_child.children = self.get_hierarhy_childs(gg['id'])
                else:
                    query = (
                        "SELECT `sections`.`id` as id,"
                        "`sections`.`name` as title,"
                        "`sections`.`parent_id`,"
                        "`sections`.`active`,"
                        "`sections`.`sort`,"
                        "`sections`.`espeshial`"
                        "FROM `menudb`.`sections`"
                        "where  parent_id =%s "
                        "ORDER BY sort ASC "
                    )
                    cursor.execute(query, [gg['id']])
                    fsub = cursor.fetchall()
                    for fs in fsub:
                        second_level_sub = HierarchyItem(**fs)
                        second_level_sub.children = self.get_hierarhy_childs(fs['id'])
                        first_level_child.children.append(second_level_sub)
                result.dataTree.append(first_level_child)

            return result
        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_hierarhy_childs(self, parent_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            result = []
            query = (
                "SELECT id as id,"
                "name as title, "
                "active as active, "
                "sort as sort, "
                "IFNULL(price, 0) as price "
                "FROM menudb.dishes "
                "where parentId=%s "
                "ORDER BY sort ASC "
            )
            cursor.execute(query, [parent_id])
            fetch = cursor.fetchall()
            for gg in fetch:
                result.append(HierarchyItem(**gg))
            return result

        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
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
            print(id, active, company_id, int(active == True))
            self.cnx.commit()
        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
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
        except HTTPException:
            # Пропускаем HTTPException и позволяем FastAPI обработать его самостоятельно
            raise
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
            if section.espeshial:
                section.dishes = self.__get_dishes(section.id)
            else:
                section.subsections = self.__get_subsections(section.id)
                for subsection in section.subsections:
                    subsection.dishes = self.__get_dishes(subsection.id)

        result.promo = self.__get_promos(result.companyInfo.id)

        return result

    def __get_promos(self, company_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "SELECT id, img, text, active, sort, type, company_id "
                "FROM menudb.promo "
                "WHERE company_id = %s "
                "ORDER BY sort"
            )
            cursor.execute(query, [company_id])
            fetch = cursor.fetchall()

            result = [Promo(**promo) for promo in fetch]

            return result

        except mysql.connector.Error as db_error:
            # Обработка ошибок базы данных
            print("Database error:", db_error)


        except Exception as e:
            # Обработка других исключений
            print("Произошла ошибка при получении промо:", e)

    def __get_sections(self, company_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "SELECT id, company_id, name, parent_id, espeshial, active, sort "
                "FROM menudb.sections "
                "WHERE ifnull(parent_id, 0) = 0 AND company_id = %s "
                "ORDER BY sort"
            )
            cursor.execute(query, [company_id])
            fetch = cursor.fetchall()

            result = []
            for gg in fetch:
                result.append(Section(**gg))

            return result

        except Exception as e:
            # В случае возникновения ошибки, вы можете обработать ее здесь
            print("Произошла ошибка при получении секций:", e)
            return []

    def __get_subsections(self, parent_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "SELECT id, company_id, name, parent_id, espeshial, active, sort "
                "FROM menudb.sections "
                "WHERE ifnull(parent_id, 0) = %s "
                "ORDER BY sort"
            )
            cursor.execute(query, [parent_id])
            fetch = cursor.fetchall()

            result = []
            for gg in fetch:
                result.append(Section(**gg))

            return result

        except Exception as e:
            # В случае возникновения ошибки, вы можете обработать ее здесь
            print("Произошла ошибка при получении подсекций:", e)
            return []

    def __get_dishes(self, parent_id):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = (
                "SELECT id, name, mainImg, description, price, weight, isSpicy, parentId, companyId, active, sort "
                "FROM menudb.dishes "
                "WHERE parentId = %s "
                "ORDER BY sort"
            )
            cursor.execute(query, [parent_id])
            fetch = cursor.fetchall()

            result = []
            for gg in fetch:
                result.append(Dish(**gg))

            return result

        except Exception as e:
            # В случае возникновения ошибки, вы можете обработать ее здесь
            print("Произошла ошибка при получении блюд:", e)
            return []

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

    def update_dish_sort(self, element: SortingPacket):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Получаем текущие данные элемента
            cursor.execute("SELECT sort, parentId FROM menudb.dishes WHERE id = %s", (element.id,))
            current = cursor.fetchone()

            if not current:
                raise HTTPException(status_code=404, detail="Элемент не найден")

            current_sort, parent_id = current['sort'], current['parentId']

            # Определяем направление сортировки и ищем соседний элемент
            if element.direction > 0:
                cursor.execute("""
                    SELECT id, sort FROM menudb.dishes
                    WHERE parentId = %s AND sort > %s
                    ORDER BY sort ASC LIMIT 1
                """, (parent_id, current_sort))
            else:
                cursor.execute("""
                    SELECT id, sort FROM menudb.dishes
                    WHERE parentId = %s AND sort < %s
                    ORDER BY sort DESC LIMIT 1
                """, (parent_id, current_sort))

            neighbor = cursor.fetchone()

            if not neighbor:
                raise HTTPException(status_code=404, detail="Соседний элемент не найден")

            # Меняем местами значения sort
            cursor.execute("UPDATE menudb.dishes SET sort = %s WHERE id = %s", (neighbor['sort'], element.id))
            cursor.execute("UPDATE menudb.dishes SET sort = %s WHERE id = %s", (current_sort, neighbor['id']))

            self.cnx.commit()

        except HTTPException as http_exc:
            # Передаем HTTPException дальше
            raise http_exc

        except Exception as e:
            # Любые другие исключения обрабатываем здесь
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    def update_section_sort(self, element: SortingPacket):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Получаем текущие данные элемента
            cursor.execute("SELECT sort, parent_id FROM menudb.sections WHERE id = %s", (element.id,))
            current = cursor.fetchone()

            if not current:
                raise HTTPException(status_code=404, detail="Секция не найдена")

            current_sort, parent_id = current['sort'], current['parent_id']

            # Определяем направление сортировки и ищем соседний элемент
            if element.direction > 0:
                cursor.execute("""
                    SELECT id, sort FROM menudb.sections
                    WHERE parent_id = %s AND sort > %s
                    ORDER BY sort ASC LIMIT 1
                """, (parent_id, current_sort))
            else:
                cursor.execute("""
                    SELECT id, sort FROM menudb.sections
                    WHERE parent_id = %s AND sort < %s
                    ORDER BY sort DESC LIMIT 1
                """, (parent_id, current_sort))

            neighbor = cursor.fetchone()

            if not neighbor:
                raise HTTPException(status_code=404, detail="Соседняя секция не найдена")

            # Меняем местами значения sort
            cursor.execute("UPDATE menudb.sections SET sort = %s WHERE id = %s", (neighbor['sort'], element.id))
            cursor.execute("UPDATE menudb.sections SET sort = %s WHERE id = %s", (current_sort, neighbor['id']))

            self.cnx.commit()

        except HTTPException as http_exc:
            # Передаем HTTPException дальше
            raise http_exc

        except Exception as e:
            # Любые другие исключения обрабатываем здесь
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    def update_promo_sort(self, element: SortingPacket):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Получаем текущие данные элемента, включая company_id
            cursor.execute("SELECT sort, company_id FROM menudb.promo WHERE id = %s", (element.id,))
            current = cursor.fetchone()

            if not current:
                raise HTTPException(status_code=404, detail="Промо-акция не найдена")

            current_sort, company_id = current['sort'], current['company_id']

            # Определяем направление сортировки и ищем соседний элемент в рамках того же company_id
            if element.direction > 0:
                cursor.execute("""
                    SELECT id, sort FROM menudb.promo
                    WHERE company_id = %s AND sort > %s
                    ORDER BY sort ASC LIMIT 1
                """, (company_id, current_sort))
            else:
                cursor.execute("""
                    SELECT id, sort FROM menudb.promo
                    WHERE company_id = %s AND sort < %s
                    ORDER BY sort DESC LIMIT 1
                """, (company_id, current_sort))

            neighbor = cursor.fetchone()

            if not neighbor:
                raise HTTPException(status_code=404, detail="Соседняя промо-акция не найдена")

            # Меняем местами значения sort в пределах одного company_id
            cursor.execute("UPDATE menudb.promo SET sort = %s WHERE id = %s", (neighbor['sort'], element.id))
            cursor.execute("UPDATE menudb.promo SET sort = %s WHERE id = %s", (current_sort, neighbor['id']))

            self.cnx.commit()

        except HTTPException as http_exc:
            # Передаем HTTPException дальше
            raise http_exc

        except Exception as e:
            # Любые другие исключения обрабатываем здесь
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    def fill_sort_order(self):
        try:
            cursor = self.cnx.cursor(dictionary=True)

            # Запросы и обработка для dishes
            cursor.execute("SELECT id, parentId FROM menudb.dishes ORDER BY parentId, id")
            dishes = cursor.fetchall()
            self._update_sort_order(cursor, dishes, 'dishes', 'parentId')

            # Запросы и обработка для sections
            cursor.execute("SELECT id, parent_id FROM menudb.sections ORDER BY parent_id, id")
            sections = cursor.fetchall()
            self._update_sort_order(cursor, sections, 'sections', 'parent_id')

            self.cnx.commit()

        except Exception as e:
            self.cnx.rollback()
            raise e

    def _update_sort_order(self, cursor, records, table_name, parent_field_name):
        sort_order = 0
        current_parent_id = None

        for record in records:
            # Убедитесь, что record является словарем
            if record[parent_field_name] != current_parent_id:
                sort_order = 1
                current_parent_id = record[parent_field_name]
            else:
                sort_order += 1

            cursor.execute(f"UPDATE menudb.{table_name} SET sort = %s WHERE id = %s", (sort_order, record['id']))
