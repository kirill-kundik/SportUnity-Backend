from app.postgres.db import *


async def add_activity(conn): pass


async def update_activity(conn, type_id, user_id):
    await conn.execute(activity.insert().values(type_fk=type_id, user_fk=user_id))


async def add_point(conn, long, lat, activity_fk):
    await conn.execute(point.insert().values(long, lat, activity_fk))


async def get_all_types(conn):
    res = await conn.execute(type_.select())
    return await res.fetchall()


async def get_user_active(conn, user_fk):
    res = await conn.execute(
        activity.select().where(activity.c.user_fk == user_fk).where(activity.c.status == ActivityStatus.ACTIVE)
    )
    return await res.fetchone()
