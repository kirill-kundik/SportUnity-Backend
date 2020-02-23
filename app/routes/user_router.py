import datetime

import aiohttp.web

import app.postgres.queries as db


async def get_user(request):
    try:
        user_id = request.match_info["id"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        user = await db.get_user(conn, user_id)

        if not user:
            raise aiohttp.web.HTTPBadRequest()

        types = await db.get_user_types(conn, user.id)

    return aiohttp.web.json_response(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "description": user.description,
            "photo_url": user.photo_url,
            "types": [{
                "id": type_.id,
                "name": type_.name,
                "recent_loc_count": type_.recent_loc_count,
                "image_url": type_.image_url,
                "color": type_.color,
            } for type_ in types]
        }
    )


async def follow(request):
    try:
        body = await request.json()

        user_id = body["userId"]
        following_id = body["followingId"]
    except:
        raise aiohttp.web.HTTPBadRequest()

    async with request.app["db"].acquire() as conn:
        await db.add_followers(conn, user_id, following_id)

    return aiohttp.web.HTTPOk()


async def feed(request):
    try:
        body = await request.json()

        user_id = int(body["userId"])
    except:
        raise aiohttp.web.HTTPBadRequest()

    response = []

    async with request.app["db"].acquire() as conn:
        followers = await db.get_user_followers(conn, user_id)
        followers = [user_id] + [follower.following for follower in followers]

        followers_feed = await db.get_all_followers_feed(conn, followers)

        for event in followers_feed:
            follower = await db.get_user(conn, event.user_fk)
            started_following = await db.get_user(conn, event.following)
            response.append({
                "type": "following",
                "timestamp": event.followed_at,
                "follower": {
                    "id": follower.id,
                    "email": follower.email,
                    "name": follower.name,
                    "description": follower.description,
                    "image_url": follower.photo_url,
                },
                "started_following": {
                    "id": started_following.id,
                    "email": started_following.email,
                    "name": started_following.name,
                    "description": started_following.description,
                    "image_url": started_following.photo_url,
                }
            })

        activities_feed = await db.get_all_activities_feed(conn, followers)

        for event in activities_feed:
            user = await db.get_user(conn, event.user_fk)
            type_ = await db.get_type(conn, event.type_fk)
            event_obj = {
                "type": "activity",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "description": user.description,
                    "image_url": user.photo_url,
                },
                "activity": {
                    "id": event.id,
                    "name": event.name,
                    "status": event.status.name,
                    "expected_start": datetime.datetime.isoformat(
                        event.expected_start) if event.expected_start else None,
                    "start_time": datetime.datetime.isoformat(event.start_time) if event.start_time else None,
                    "end_time": datetime.datetime.isoformat(event.end_time) if event.end_time else None,
                    "description": event.description,
                    "type": {
                        "id": type_.id,
                        "name": type_.name,
                        "recent_loc_count": type_.recent_loc_count,
                        "image_url": type_.image_url,
                        "color": type_.color,
                    }
                }
            }
            if event.created_at:
                response.append({"timestamp": event.created_at, "status": "created", **event_obj})
            if event.start_time:
                response.append({"timestamp": event.start_time, "status": "started", **event_obj})
            if event.end_time:
                response.append({"timestamp": event.end_time, "status": "finished", **event_obj})
        response.sort(key=lambda i: i["timestamp"], reverse=True)

        for item in response:
            item["timestamp"] = datetime.datetime.isoformat(item["timestamp"])

        return aiohttp.web.json_response(response)


async def get_all_users(request):
    response = []
    async with request.app["db"].acquire() as conn:
        users = await db.get_all_users(conn)

        for user in users:
            types = await db.get_user_types(conn, user.id)

            response.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "description": user.description,
                    "image_url": user.photo_url,
                    "types": [{
                        "id": type_.id,
                        "name": type_.name,
                        "recent_loc_count": type_.recent_loc_count,
                        "image_url": type_.image_url,
                        "color": type_.color,
                    } for type_ in types]
                })

    return aiohttp.web.json_response(response)


def configure(app):
    router = app.router

    router.add_route('GET', '/user/{id}', get_user, name="get_user")
    router.add_route('POST', '/follow', follow, name="follow")
    router.add_route('POST', '/feed', feed, name='feed')
    router.add_route('GET', '/allUsers', get_all_users, name='all_users')
