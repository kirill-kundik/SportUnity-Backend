import aiohttp


async def init_cb(app):
    app["cb_base_url"] = ""
    cb = aiohttp.ClientSession(
        auth=aiohttp.BasicAuth("Administrator", "Year2018"),
    )
    params = {
        'statement': "SELECT * FROM locations USE KEYS \"1582026302900/a/84852/141421\"",
    }
    async with cb.get("http://f4a4d6fc.ngrok.io/query/service", params=params, headers={"Accept": "application/json"}) as resp:
        pass
    app["cb"] = cb
