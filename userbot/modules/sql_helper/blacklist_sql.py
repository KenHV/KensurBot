try:
    from userbot.modules.sql_helper import BASE, SESSION
except ImportError:
    raise AttributeError

from sqlalchemy import Column, String


class Blacklist(BASE):
    __tablename__ = "blacklist"
    chat_id = Column(String(20), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)


Blacklist.__table__.create(checkfirst=True)


def get_blacklist():
    try:
        return SESSION.query(Blacklist).all()
    except BaseException:
        return None
    finally:
        SESSION.close()


def add_blacklist(chat_id):
    adder = Blacklist(str(chat_id))
    SESSION.add(adder)
    SESSION.commit()


def del_blacklist(chat_id):
    rem = SESSION.query(Blacklist).get(str(chat_id))
    if rem:
        SESSION.delete(rem)
        SESSION.commit()


def del_blacklist_all():
    SESSION.execute("""TRUNCATE TABLE blacklist""")
    SESSION.commit()
