try:
    from userbot.modules.sql_helper import SESSION, BASE
except ImportError:
    raise AttributeError

from sqlalchemy import Column, UnicodeText, LargeBinary, Numeric


class Snips(BASE):
    __tablename__ = "snips"
    snip = Column(UnicodeText, primary_key=True)
    reply = Column(UnicodeText)
    snip_type = Column(Numeric)
    media_id = Column(UnicodeText)
    media_access_hash = Column(UnicodeText)
    media_file_reference = Column(LargeBinary)

    def __init__(
        self,
        snip, reply, snip_type,
        media_id=None, media_access_hash=None, media_file_reference=None
    ):
        self.snip = snip
        self.reply = reply
        self.snip_type = snip_type
        self.media_id = media_id
        self.media_access_hash = media_access_hash
        self.media_file_reference = media_file_reference


Snips.__table__.create(checkfirst=True)


def get_snip(keyword):
    try:
        return SESSION.query(Snips).get(keyword)
    finally:
        SESSION.close()


def get_snips():
    try:
        return SESSION.query(Snips).all()
    finally:
        SESSION.close()


def add_snip(
        keyword,
        reply,
        snip_type,
        media_id,
        media_access_hash,
        media_file_reference):
    to_check = get_snip(keyword)
    if not to_check:
        adder = Snips(
            keyword,
            reply,
            snip_type,
            media_id,
            media_access_hash,
            media_file_reference)
        SESSION.add(adder)
        SESSION.commit()
        return True
    else:
        rem = SESSION.query(Snips).filter(Snips.snip == keyword)
        SESSION.delete(rem)
        SESSION.commit()
        adder = Snips(
            keyword,
            reply,
            snip_type,
            media_id,
            media_access_hash,
            media_file_reference)
        SESSION.add(adder)
        SESSION.commit()
        return False


def remove_snip(keyword):
    to_check = get_snip(keyword)
    if not to_check:
        return False
    else:
        rem = SESSION.query(Snips).filter(Snips.snip == keyword)
        rem.delete()
        SESSION.commit()
        return True
