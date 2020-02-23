import sys
import logging

from aiohttp import web

from app.postgres.db_init import init_db
from app.postgres.utils import close_pg, init_pg
from app.utils import get_config, setup_routes
from app.elastic.utils import close_es, init_es
from app.couchbase.utils import init_cb, close_cb


async def init_app(argv=None):
    app = web.Application()

    app['config'] = get_config(argv)

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_pg)
    app.on_startup.append(init_es)
    # app.on_startup.append(init_cb)
    app.on_cleanup.append(close_es)
    app.on_cleanup.append(close_pg)
    # app.on_cleanup.append(close_cb)

    # setup routes
    setup_routes(app)

    return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    init_db()

    app = init_app(argv)

    config = get_config(argv)
    web.run_app(app,
                host=config['host'],
                port=config['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
