import aiohttp.web

import app.postgres.queries as db


async def type_all(request):
    types = []
    async with request.app["db"].acquire() as conn:
        for type_ in await db.get_all_types(conn):
            types.append({
                "id": type_.id,
                "name": type_.name,
                "recent_loc_count": type_.recent_loc_count,
                "image_url": type_.image_url,
                "color": type_.color,
            })

    return aiohttp.web.json_response(types)


def configure(app):
    router = app.router

    router.add_route('GET', '/getTypeList', type_all, name="getTypeList")
