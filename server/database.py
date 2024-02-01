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


    async def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=True, get_id=False):
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
        if get_id:
            data = cursor.lastrowid

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
                timeslot TEXT,
                bat TEXT,
                turne INTEGER,
                status TEXT
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
                status
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        return await self.execute(sql=sql, parameters=data, get_id=True)


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
            #date_timeslot = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M')
            #days.append(date_timeslot.weekday())
            days.append(row[0][0])

        if days.count(asked_day) >= 2:
            return True
        else:
            return False


    async def get_status(self, _id):
        sql = "SELECT status FROM orders WHERE id = ?"

        status = await self.execute(sql=sql, parameters=(_id, ), commit=False, fetchone=True)

        return status[0]

    async def set_status(self, _id, _status):
        sql = "UPDATE orders SET status = ? WHERE id = ?"

        await self.execute(sql=sql, parameters=(_status, str(_id), ))


    async def get_sos(self, _id):
        sql = "SELECT * FROM orders WHERE id = ?"

        sos_with_id = await self.execute(sql=sql, parameters=(str(_id), ), fetchone=True, commit=False)

        sos = []

        for i in range(1, len(sos_with_id)):
            sos.append(sos_with_id[i])

        sos.append(sos_with_id[0])

        return sos


    async def modify_loop(self, queue):
        while True:
            command = await queue.get()

            sql = "UPDATE orders SET status = ? WHERE id = ?"

            await self.execute(sql=sql, parameters=(command["command"], str(command["id"]), ))

            queue.task_done()
