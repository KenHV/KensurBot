from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from userbot import DB_URI
from userbot import LOGS


BASE = declarative_base()
engine = create_engine(DB_URI)


def start() -> scoped_session:
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


def delete_table(table_name):
    metadata = MetaData()
    metadata.reflect(engine)
    table = metadata.tables.get(table_name)
    if table is not None:
        LOGS.info(f"Deleting '{table_name}' table...")
        BASE.metadata.drop_all(engine, [table], checkfirst=True)


SESSION = start()
