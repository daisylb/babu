from sqlalchemy import Column, String
from babu.db import Model


class Page(Model):
    title = Column(String)
    content = Column(String)
