import datetime
import time

import aiohttp.web

import app.couchbase.queries as couchbase
import app.postgres.queries as db


async def track(request):
    try:
        body = await request.json()

        long = body["lon"]
        lat = body["lat"]
        user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        activity = await db.get_user_active(conn, user_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()

        await db.add_point(conn, long, lat, activity.id)

    # cb = request.app["cb"]
    # await couchbase.insert(cb, f"{activity.id}-{int(time.time())}", long, lat)

    return aiohttp.web.HTTPOk


async def start_by_activity(request):
    pass


async def start_by_type(request):
    try:
        body = await request.json()

        type_id = body["typeId"]
        user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        await db.add_activity(
            conn, None, db.ActivityStatus.ACTIVE, None, datetime.datetime.now(), None, None, user_id, type_id
        )

    return aiohttp.web.HTTPOk()


async def add_activity(request):
    try:
        body = await request.json()

        user_id = body["userId"]
        expected_start = datetime.datetime.fromisoformat(body["expectedStart"])
        type_id = body["typeId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        await db.add_activity(
            conn, None, db.ActivityStatus.NOT_STARTED, expected_start, None, None, None, user_id, type_id
        )
    return aiohttp.web.HTTPOk()


async def copy_activity(request):
    try:
        body = await request.json()

        user_id = body["userId"]
        activity_id = request.match_info["id"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        activity = await db.get_activity(conn, activity_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()

        await db.add_activity(
            conn,
            activity.name,
            activity.status,
            activity.expected_start,
            activity.start_time,
            activity.end_time,
            activity.description,
            user_id,
            activity.type_fk
        )

    return aiohttp.web.HTTPOk()


async def get_activity(request):
    try:
        activity_id = request.match_info["id"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        activity = await db.get_activity(conn, activity_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()

    return aiohttp.web.json_response(
        {
            "id": activity.id,
            "name": activity.name,
            "status": activity.status.name,
            "expected_start": datetime.datetime.isoformat(activity.expected_start) if activity.expected_start else None,
            "start_time": datetime.datetime.isoformat(activity.start_time) if activity.start_time else None,
            "finish_time": datetime.datetime.isoformat(activity.finish_time) if activity.finish_time else None,
            "description": activity.description,
            "user_id": activity.user_fk,
            "type_id": activity.type_fk,
        }
    )


def configure(app):
    router = app.router

    router.add_route('POST', '/track', track, name='track')
    router.add_route('POST', '/activity', add_activity, name='activity')
    router.add_route('POST', '/startTrackType', start_by_type, name='start_by_type')
    router.add_route('POST', '/copyActivity/{id}', copy_activity, name='copy_activity')
    router.add_route('GET', '/activity/{id}', get_activity, name='get_activity')
