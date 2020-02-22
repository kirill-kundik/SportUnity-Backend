from sqlalchemy import (
    MetaData, Table, Column, Integer, String
)

__all__ = ['admin']

meta = MetaData()

admin = Table(
    'admin', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(255), nullable=True),
    Column('pass_hash', String(255), nullable=False)

)
