import functools
import typing as t

import jinja2
import mistletoe

from .response import Response

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader("leighbrenecki/templates/"),
    autoescape=jinja2.select_autoescape(("htm", "html", "xml")),
)


def template(name: str) -> t.Callable[[t.Callable], t.Callable]:
    the_template = environment.get_template(name)

    def decorator(func: t.Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = func(*args, **kwargs)
            return Response(200, the_template.render(**context))

        return wrapper

    return decorator


def markdown(value):
    return mistletoe.markdown(value)


environment.filters["markdown"] = markdown
