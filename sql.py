import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from model import User
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
        cursor = self.cnx.cursor()

        query = ("SELECT * FROM menudb.company "
                 "where id=1")
        cursor.execute(query)
        result=cursor.fetchall()
        return result

    def getUser(self, name: str):
        cursor = self.cnx.cursor(dictionary=True)
        query  = ("SELECT name,hash,companyId from menudb.users "
                  "where name=%s")
        cursor.execute(query,[name])
        gg=cursor.fetchone()
        if not gg:
            return gg
        result=User(**gg)
        return  result



    def newUser(self,user:User):
        cursor=self.cnx.cursor()
        query=("INSERT INTO menudb.users"
               "(name,hash,companyId)"
               " VALUES (%(name)s, %(hash)s, %(companyId)s)")
        cursor.execute(query,user.dict())
        self.cnx.commit()
        result=self.getUser(user.name)
        return result
