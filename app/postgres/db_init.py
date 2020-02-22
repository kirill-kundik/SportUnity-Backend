from sqlalchemy import create_engine, MetaData

from app.postgres.db import *
from app.utils import BASE_DIR, get_config

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='postgres', port=5432
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG_PATH = BASE_DIR / 'config' / 'config.yaml'
USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def teardown_db(config):
    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine,
                    tables=[user, activity, type_, user_to_type, point])


def drop_tables(engine):
    meta = MetaData()
    meta.drop_all(bind=engine,
                  tables=[user, activity, type_, user_to_type, point])


def sample_data(engine):
    conn = engine.connect()
    conn.execute(
        type_.insert(), [
            {"name": "cycling", "recent_loc_count": 5, "image_url": ""},
            {"name": "running", "recent_loc_count": 5, "image_url": ""},
            {"name": "trekking", "recent_loc_count": 5, "image_url": ""},
            {"name": "skating", "recent_loc_count": 5, "image_url": ""},
            {"name": "gym", "recent_loc_count": 1, "image_url": ""},
            {"name": "walking", "recent_loc_count": 3, "image_url": ""},
        ]
    )
    conn.execute(
        user.insert(), [
            {"email": "kkk@gmail.com", "name": "Kirill Kirill", "description": "Long distance runner",
             "image_url": "https://i.imgur.com/UXOBdLU.jpg"}
        ]
    )
    conn.close()


def init_db():
    # setup_db(USER_CONFIG['postgres'])
    drop_tables(engine=user_engine)  # TODO: remember it
    create_tables(engine=user_engine)
    sample_data(engine=user_engine)
    # teardown_db(config)


if __name__ == '__main__':
    init_db()
