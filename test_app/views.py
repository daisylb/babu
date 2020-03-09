from babu.routing import Router, DatabaseRoute, query
from . import models
from babu.response import Response

app = Router()


def foo(id):
    return Response(status=200, body=f"ID: {id}")


dbr = DatabaseRoute("/page/%s/", query(models.Page.id), foo)
app.add(dbr)
