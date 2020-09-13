import typing as t
from http import HTTPStatus

import attr


@attr.s
class Response:
    status: HTTPStatus = attr.ib()
    body: t.Union[str, bytes, t.TextIO, t.BinaryIO] = attr.ib()
