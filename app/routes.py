# routes.py
import pathlib

from aiohttp import web


class IndexRouter:

    async def index(self, request):
        res = {"q": "qqq", "a": "aaa"}
        return web.json_response(res)

    def configure(self, app):
        router = app.router

        router.add_route('GET', '/', self.index, name='index')


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    routes = [IndexRouter()]
    for route in routes:
        route.configure(app)
