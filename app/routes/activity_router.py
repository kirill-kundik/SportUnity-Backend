import time

import aiohttp.web

import app.couchbase.queries as couchbase
import app.postgres.queries as db


async def track(request):
    try:
        body = await request.json()

        long = body["long"]
        lat = body["lat"]
        user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest

    async with request.app['db'].acquire() as conn:
        activity = await db.get_user_active(conn, user_id)
        await db.add_point(conn, long, lat, activity.id)

    cb = request.app["cb"]
    await couchbase.insert(cb, f"{activity.id}-{int(time.time())}", long, lat)

    return aiohttp.web.HTTPOk


async def start_by_type(request):
    try:
        body = await request.json()

        type_id = body["typeId"]
        user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest


def configure(app):
    router = app.router

    router.add_route('POST', '/track', track, name='track')
