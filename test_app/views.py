from babu.routing import Router
from babu.views import template

from . import models

app = Router()


@app.db_view("/page/%s/", models.Page.id)
@template("test.html")
def foo(id):
    return {"blah": id}
