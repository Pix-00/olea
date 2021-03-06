__all__ = ['Logger']

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .model import Log


class Logger():
    def __init__(self, path):
        self.path = path
        self.Session = None
        self.month = 0

        self.path.mkdir(exist_ok=True)

    def connect(self, year, month):
        engine = create_engine(f'sqlite:///{self.path}/{year}-{month}.db')
        session_factory = sessionmaker(bind=engine)
        self.month = month
        self.Session = scoped_session(session_factory)

    def log(self, **kwargs):
        now = kwargs['now']
        if self.month != now.month:
            self.connect(now.year, now.month)

        session = self.Session()
        log = Log(**kwargs)
        session.add(log)
        session.commit()
        self.Session.remove()
