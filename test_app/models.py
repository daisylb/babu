from sqlalchemy import Column, String
from babu.db import Base

class Page(Base):
    title = Column(String)
    content = Column(String)