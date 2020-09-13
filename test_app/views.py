from babu.routing import Router, DatabaseRoute, query
from . import models
from babu.response import Response
from babu.views import template

app = Router()


@app.db_view("/page/%s/", models.Page.id)
@template('test.html')
def foo(id):
    return {'blah': id}
