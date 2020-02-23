import datetime

import aiohttp.web

import app.postgres.queries as db


async def track(request):
    try:
        body = await request.json()
        user_id = int(body[0]["userId"])
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        activity = await db.get_user_active(conn, user_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()
        for item in body:
            await db.add_point(conn, item["lon"], item["lat"], activity.id)

    # cb = request.app["cb"]
    # await couchbase.insert(cb, f"{activity.id}-{int(time.time())}", long, lat)

    return aiohttp.web.HTTPOk()


async def start_by_activity(request):
    try:
        body = await request.json()

        activity_id = body["activityId"]
        _user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        activity = await db.get_activity(conn, activity_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()

        await db.update_activity(
            conn,
            activity_id,
            activity.name,
            db.ActivityStatus.ACTIVE,
            activity.expected_start,
            datetime.datetime.now(),
            None,
            activity.description,
            activity.type_fk
        )

    return aiohttp.web.HTTPOk()


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
            "end_time": datetime.datetime.isoformat(activity.end_time) if activity.end_time else None,
            "description": activity.description,
            "user_id": activity.user_fk,
            "type_id": activity.type_fk,
        }
    )


async def get_nearby(request):
    response = []

    async with request.app["db"].acquire() as conn:
        all_active = await db.get_all_active(conn)
        for active in all_active:
            type_ = await db.get_type(conn, active.type_fk)

            locations = await db.get_points(conn, active.id, type_.recent_loc_count)

            response.append({
                "user_id": active.user_fk,
                "color": type_.color,
                "image_url": type_.image_url,
                "locations": [
                    {"lat": loc.lat, "lon": loc.long}
                    for loc in locations
                ],
            })

    return aiohttp.web.json_response(response)


async def end_activity(request):
    try:
        body = await request.json()

        user_id = body["userId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        activity = await db.get_user_active(conn, user_id)

        if not activity:
            raise aiohttp.web.HTTPBadRequest()

        await db.update_activity(
            conn,
            activity.id,
            activity.name,
            db.ActivityStatus.FINISHED,
            activity.expected_start,
            activity.start_time,
            datetime.datetime.now(),
            activity.description,
            activity.type_fk
        )

    return aiohttp.web.HTTPOk()


async def check_activity(request):
    try:
        user_id = request.match_info["id"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app['db'].acquire() as conn:
        activity = await db.get_user_active(conn, user_id)

        if not activity:
            return aiohttp.web.json_response({
                "da": False,
            })
        return aiohttp.web.json_response({
            "da": True,
        })


async def user_activities(request):
    try:
        user_id = request.match_info["id"]
    except:
        raise aiohttp.web.HTTPBadRequest()
    response = []
    async with request.app['db'].acquire() as conn:
        activities = await db.get_user_activities(conn, user_id)

        for active in activities:
            type_ = await db.get_type(conn, active.type_fk)
            response.append({
                "id": active.id,
                "name": active.name,
                "status": active.status.name,
                "expected_start": datetime.datetime.isoformat(
                    active.expected_start) if active.expected_start else None,
                "start_time": datetime.datetime.isoformat(active.start_time) if active.start_time else None,
                "end_time": datetime.datetime.isoformat(active.end_time) if active.end_time else None,
                "description": active.description,
                "type": {
                    "id": type_.id,
                    "name": type_.name,
                    "recent_loc_count": type_.recent_loc_count,
                    "image_url": type_.image_url,
                    "color": type_.color,
                }
            })

    return aiohttp.web.json_response(response)


def configure(app):
    router = app.router

    router.add_route('POST', '/track', track, name='track')
    router.add_route('POST', '/activity', add_activity, name='activity')
    router.add_route('POST', '/startTrackType', start_by_type, name='start_by_type')
    router.add_route('POST', '/startTrackActivity', start_by_activity, name='start_by_activity')
    router.add_route('POST', '/copyActivity/{id}', copy_activity, name='copy_activity')
    router.add_route('GET', '/activity/{id}', get_activity, name='get_activity')
    router.add_route('GET', '/getNearby', get_nearby, name='get_nearby')
    router.add_route('POST', '/stopTrack', end_activity, name='end_activity')
    router.add_route('GET', '/check/{id}', check_activity, name='check_activity')
    router.add_route('GET', '/activities/{id}', user_activities, name='user_activities')
