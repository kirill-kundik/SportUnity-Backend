import json


async def _make_request(cb, stmt, resp_type='get', url_prefix="/query/service"):
    url = "http://f4a4d6fc.ngrok.io" + url_prefix
    params = {
        "statement": stmt
    }
    response = None
    if resp_type == 'get':
        async with cb.get(url, params=params) as _resp:
            response = _resp
    elif resp_type == 'post':
        async with cb.post(url, params=params) as _resp:
            response = _resp

    assert response.status == 200
    response = await response.text()
    try:
        return json.loads(response)
    except:
        return response


async def insert(cb, key, long, lat):
    stmt = 'INSERT INTO `locations` ( KEY, VALUE ) ' \
           'VALUES ("%s",{ "lat": %s, "lon": %s}) RETURNING META().id as docid, *;' % (key, long, lat)

    await _make_request(cb, stmt, resp_type='post')


async def delete(cb, key):
    stmt = f"DELETE FROM `locations` where KEY LIKE '{key}%'"

    await _make_request(cb, stmt, resp_type='post')


async def get_nearby(cb, long, lat, distance="5km", limit=1000000):
    body = {
        "from": 0,
        "size": limit,
        "query": {
            "location": {
                "lon": float(long),
                "lat": float(lat),
            },
            "distance": distance,
            "field": "geo",
        },
    }
    async with cb.post(
            "http://cfa3a080.eu.ngrok.io/api/index/spatial-active-location-index/query",
            json=body
    ) as resp:
        assert resp.status == 200
        return await resp.json()
