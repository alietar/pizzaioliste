import aiosqlite
import datetime

class DataBase:
    def __init__(self, path_to_db="assets/sos.db"):
        self.path_to_db = path_to_db

    async def connect(self):
        self.db = await aiosqlite.connect(self.path_to_db)

        await self.create_table_sos()


    async def close(self):
        await self.db.close()


    async def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=True):
        if not parameters:
            parameters = ()

        data = None
        cursor = await self.db.cursor()

        await cursor.execute(sql, parameters)

        if commit:
            await self.db.commit()
        if fetchone:
            data = await cursor.fetchone()
        if fetchall:
            data = await cursor.fetchall()

        await cursor.close()

        return data


    async def create_table_sos(self):
        sql = """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                order_date DATETIME,
                fname TEXT,
                lname TEXT,
                email TEXT,
                sos INTEGER,
                sos_name TEXT,
                timeslot DATETIME,
                bat TEXT,
                turne INTEGER,
                done BOOLEAN
            )
        """

        await self.execute(sql=sql)


    async def add_sos(self, data: list):
        sql = """
            INSERT INTO orders (
                order_date,
                fname,
                lname,
                email,
                sos,
                sos_name,
                timeslot,
                bat,
                turne,
                done
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        await self.execute(sql=sql, parameters=data)


    async def get_all_sos(self):
        sql = """
            SELECT * FROM orders
        """

        return await self.execute(sql=sql, fetchall=True, commit=False)



    async def check_user_limit(self, email: str, asked_day):
        """
            Check user's daily limit of SOSs, which is 2, based on his email
        """
        sql = "SELECT timeslot FROM orders WHERE email = ?"

        rows = await self.execute(sql=sql, parameters=(email, ), commit=False, fetchall=True)

        days = []

        for row in rows:
            date_timeslot = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M')
            days.append(date_timeslot.weekday())

        if days.count(asked_day) >= 2:
            return True
        else:
            return False
