from babu.routing import NestingRouter, DatabaseRouter, query
from . import models
from babu.response import Response

app = NestingRouter()


def foo(id):
    return Response(status=200, body=f"ID: {id}")


dbr = DatabaseRouter("/page/%s/", query(models.Page.id), foo)
app.add(dbr)
