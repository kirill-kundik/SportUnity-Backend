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
                    tables=[admin])


def drop_tables(engine):
    meta = MetaData()
    meta.drop_all(bind=engine,
                  tables=[admin])


def sample_data(engine):
    conn = engine.connect()
    conn.execute(admin.insert(), [
        {'email': 'admin@admin.com',
         'pass_hash': '$5$rounds=535000$hYkOykAwtwdNpZbd$N04R0fNDHWtpkGiGcIRVeg4ARkcwbhJCFDQYcgPnBOC'}
    ])
    # TODO insert basic info while initialize db
    # conn.execute(question.insert(), [
    #     {'question_text': 'What\'s new?',
    #      'pub_date': '2015-12-15 17:17:49.629+02'}
    # ])
    # conn.execute(choice.insert(), [
    #     {'choice_text': 'Not much', 'votes': 0, 'question_id': 1},
    #     {'choice_text': 'The sky', 'votes': 0, 'question_id': 1},
    #     {'choice_text': 'Just hacking again', 'votes': 0, 'question_id': 1},
    # ])
    conn.close()


def init_db():
    # setup_db(USER_CONFIG['postgres'])
    create_tables(engine=user_engine)
    sample_data(engine=user_engine)
    # drop_tables()
    # teardown_db(config)


if __name__ == '__main__':
    init_db()
