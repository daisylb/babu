from babu.routing import Router, DatabaseRoute, query
from . import models
from babu.response import Response

app = Router()


@app.db_view("/page/%s/", models.Page.id)
def foo(id):
    return Response(status=200, body=f"ID: {id}")
