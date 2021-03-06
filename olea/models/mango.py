__all__ = ['Mango']

from sqlalchemy_ import BaseModel, Column, ForeignKey, UniqueConstraint, relationship
from sqlalchemy_.types import JSONB, DateTime, Integer, String


class Mango(BaseModel):
    __tablename__ = 'mango'

    id = Column(String, primary_key=True)
    pit_id = Column(String, ForeignKey('pit.id', ondelete='CASCADE'))
    ver = Column(Integer, default=1)
    mime = Column(String)
    sha1 = Column(String, unique=True)
    modified_at = Column(DateTime)
    timestamp = Column(DateTime)

    metainfo = Column(JSONB)

    pit = relationship('Pit', back_populates='mangos')
    __table_args__ = (UniqueConstraint('pit_id', 'ver', name='_mango_uc'), )

    @property
    def mtype(self):
        return self.mime.split('/')[0]
