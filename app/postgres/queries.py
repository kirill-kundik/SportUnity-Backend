from app.postgres.db import *


async def add_activity(conn, name, status, expected_start, start_time, end_time, description, user_fk, type_fk):
    await conn.execute(activity.insert().values(
        name=name,
        status=status,
        expected_start=expected_start,
        start_time=start_time,
        end_time=end_time,
        description=description,
        user_fk=user_fk,
        type_fk=type_fk
    ))


async def add_point(conn, long, lat, activity_fk):
    await conn.execute(point.insert().values(long=long, lat=lat, activity_fk=activity_fk))


async def get_all_types(conn):
    res = await conn.execute(type_.select())
    return await res.fetchall()


async def get_user_active(conn, user_fk):
    res = await conn.execute(
        activity.select().where(activity.c.user_fk == user_fk).where(activity.c.status == ActivityStatus.ACTIVE)
    )
    return await res.fetchone()


async def get_user(conn, user_id):
    res = await conn.execute(
        user.select().where(user.c.id == user_id)
    )
    return await res.fetchone()


async def get_activity(conn, activity_id):
    res = await conn.execute(
        activity.select().where(activity.c.id == activity_id)
    )
    return await res.fetchone()


async def get_type(conn, type_id):
    res = await conn.execute(
        type_.select().where(type_.c.id == type_id)
    )
    return await res.fetchone()


async def get_user_types(conn, user_id):
    res = await conn.execute(
        user_to_type.select().where(user_to_type.c.user_fk == user_id)
    )
    res = await res.fetchall()

    return [await get_type(conn, r.type_fk) for r in res]


async def get_all_active(conn):
    res = await conn.execute(
        activity.select().where(activity.c.status == ActivityStatus.ACTIVE)
    )
    return await res.fetchall()


async def update_activity(conn, activity_id, name, status, expected_start, start_time, end_time, description, type_fk):
    await conn.execute(
        activity.update().where(activity.c.id == activity_id).values(
            name=name,
            status=status,
            expected_start=expected_start,
            start_time=start_time,
            end_time=end_time,
            description=description,
            type_fk=type_fk,
        )
    )


async def get_points(conn, activity_id, limit=None):
    stmt = point.select().where(point.c.activity_fk == activity_id).order_by(point.c.id.desc())
    if limit:
        stmt = stmt.limit(limit)
    res = await conn.execute(stmt)
    return await res.fetchall()


async def get_user_activities(conn, user_id):
    res = await conn.execute(activity.select().where(activity.c.user_fk == user_id))
    return await res.fetchall()


async def add_followers(conn, user_fk, following):
    await conn.execute(followers.insert().values(user_fk=user_fk, following=following))
