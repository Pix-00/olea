__all__ = [
    'BaseModel', 'Column', 'ForeignKey', 'UniqueConstraint', 'hybrid_property', 'orm',
    'relationship'
]

from functools import partial

from sqlalchemy import Column as BaseColumn
from sqlalchemy import ForeignKey, UniqueConstraint, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .main import ModelBase

Column = partial(BaseColumn, nullable=False)
BaseModel = declarative_base(cls=ModelBase)
