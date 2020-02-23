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


def configure(app):
    router = app.router

    router.add_route('GET', '/user/{id}', get_user, name="get_user")
