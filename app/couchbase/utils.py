import aiohttp


async def init_cb(app):
    app["cb_base_url"] = ""
    cb = aiohttp.ClientSession(
        auth=aiohttp.BasicAuth("Administrator", "Year2018"),
    )
    params = {
        'statement': "SELECT * FROM locations USE KEYS \"1582026302900/a/84852/141421\"",
        # "statement": 'INSERT INTO `locations` ( KEY, VALUE ) VALUES ("my key",{ "lat": 50.12345, "lon": 30.12345}) RETURNING META().id as docid, *;'
    }

    async with cb.get("http://f4a4d6fc.ngrok.io/query/service", params=params) as resp:
        # print(await resp.json())
        # print(resp.status)
        assert resp.status == 200
    app["cb"] = cb


async def close_cb(app):
    await app["cb"].close()
