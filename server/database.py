import aiosqlite
import asyncio
from aiohttp import web


async def handler(request: web.Request) -> web.Response:
    return web.Response(text="Hello world")


async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes([web.get("/", handler)])
    return app



async def main():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS orders(id, name, sos_id)")
        #await db.execute("""
        #    INSERT INTO orders VALUES
        #        (0, 'Titouan', 3),
        #        (1, 'Anatole', 4)
        #""")

        await db.execute("""
            DELETE FROM orders WHERE id == 0
        """)

        await db.commit()

        async with db.execute("SELECT * FROM orders") as cursor:
            async for row in cursor:
                print(row)


if __name__ == "__main__":
    asyncio.run(main())
    web.run_app(init_app())
