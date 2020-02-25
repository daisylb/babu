from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr, declarative_base, as_declarative

@as_declarative()
class Model:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(String, primary_key=True)

__all__ = ['Model']