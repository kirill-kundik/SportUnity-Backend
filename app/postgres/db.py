import enum

from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Enum, DateTime, ForeignKey, PrimaryKeyConstraint
)

__all__ = ['user', 'type_', 'activity', 'point', 'user_to_type', 'ActivityStatus']

meta = MetaData()


class ActivityStatus(enum.Enum):
    NOT_STARTED = 1
    ACTIVE = 2
    FINISHED = 3


user = Table(
    'user', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String),
    Column('name', String),
    Column('description', String),
    Column('photo_url', String),
)

type_ = Table(
    'type_', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('recent_loc_count', Integer, default=5),
    Column('image_url', String),
    Column('color', String),
)

activity = Table(
    'activity', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('status', Enum(ActivityStatus)),
    Column('expected_start', DateTime),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('description', String),

    Column('user_fk', Integer, ForeignKey('user.id', ondelete='cascade', onupdate='cascade')),
    Column('type_fk', Integer, ForeignKey('type_.id', ondelete='restrict', onupdate='cascade')),
)

point = Table(
    'point', meta,

    Column('id', Integer, primary_key=True),
    Column('long', String),
    Column('lat', String),

    Column('activity_fk', Integer, ForeignKey('activity.id', ondelete='cascade', onupdate='cascade')),
)

user_to_type = Table(
    'user_to_type', meta,

    Column('user_fk', Integer, ForeignKey('user.id', onupdate='cascade', ondelete='cascade')),
    Column('type_fk', Integer, ForeignKey('type_.id', ondelete='restrict', onupdate='cascade')),
    PrimaryKeyConstraint('user_fk', 'type_fk', name='user_to_type_pk')
)
