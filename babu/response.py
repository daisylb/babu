import attr
from http import HTTPStatus
import typing as t

@attr.s
class Response:
    status: HTTPStatus = attr.ib()
    body: t.Union[str, bytes, t.TextIO, t.BinaryIO] = attr.ib()