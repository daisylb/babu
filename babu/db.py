from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr, declarative_base

class _Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(String)


Model = declarative_base(cls=_Base)

__all__ = ['Model']