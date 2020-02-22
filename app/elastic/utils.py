from elasticsearch_async import AsyncElasticsearch


async def init_es(app):
    es = AsyncElasticsearch(hosts='es01')
    # es.indices.delete(index='index_name', ignore=[400, 404])  # if needed to drop previous indexes
    app['es'] = es


async def close_es(app):
    await app['es'].transport.close()
    # await app['es'].transport.wait_closed() # not needed anymore
