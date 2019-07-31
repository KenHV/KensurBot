
try:
    from userbot.modules.sql_helper import SESSION, BASE
except ImportError:
    raise AttributeError

from sqlalchemy import Boolean, Column, String, UnicodeText

class Welcome(BASE):
    __tablename__ = "welcome"
    chat_id = Column(String(14), primary_key=True)
    custom_welcome_message = Column(UnicodeText, nullable=False)
    media_file_id = Column(UnicodeText)

    def __init__(self, chat_id, custom_welcome_message, media_file_id=None):
        self.chat_id = str(chat_id)
        self.custom_welcome_message = custom_welcome_message
        self.media_file_id = media_file_id


Welcome.__table__.create(checkfirst=True)


#def get_welcome(chat_id):
#    try:
#        return SESSION.query(Welcome).get((str(chat_id)))
#    finally:
#        SESSION.close()

def get_current_welcome_settings(chat_id):
    try:
        return SESSION.query(Welcome).filter(Welcome.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def add_welcome_setting(chat_id, custom_welcome_message, media_file_id=None):
    to_check = get_welcome(chat_id)
    if not to_check:
        adder = Welcome(chat_id, custom_welcome_message, media_file_id)
        SESSION.add(adder)
        SESSION.commit()
        return True
    else:
        rem = SESSION.query(Welcome).get(str(chat_id))
        SESSION.delete(rem)
        SESSION.commit()
        adder = Welcome(chat_id, custom_welcome_message, media_file_id)
        SESSION.add(adder)
        SESSION.commit()
        return False

def rm_welcome_setting(chat_id):
    to_check = get_welcome(chat_id)
    if not to_check:
        return False
    else:
        rem = SESSION.query(Welcome).get(str(chat_id))
        SESSION.delete(rem)
        SESSION.commit()
        return True
