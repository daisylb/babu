from sqlalchemy import Column, String, UnicodeText
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Model:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(String, primary_key=True)


class Content(UnicodeText):
    """
    Column type for body content.

    Identical to :class:`sqlalchemy.types.UnicodeText`, except that it
    marks the column as the target column for the main body text for
    some filetypes.
    """


__all__ = ["Model"]
