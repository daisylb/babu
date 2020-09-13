import typing as t

from sqlalchemy import func
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import FromClause

from .response import Response


class Route(t.Protocol):
    def resolve(self, session: Session, url: str) -> t.Optional[Response]:
        ...

    def get_all(self, session: Session) -> t.Iterable[t.Tuple[str, Response]]:
        ...


class Router(Route):
    children: t.List[Route]

    def __init__(self, prefix=""):
        self.prefix = prefix
        self.children = []

    def resolve(self, session: Session, url: str) -> t.Optional[Response]:
        if not url.startswith(self.prefix):
            return None
        child_url = url[len(self.prefix) :]
        for child in self.children:
            output = child.resolve(session, child_url)
            if output is not None:
                return output
        return None

    def get_all(self, session) -> t.Iterable[t.Tuple[str, Response]]:
        for child in self.children:
            for url, content in child.get_all(session):
                yield self.prefix + url, content

    def add(self, router: Route):
        self.children.append(router)

    def db_view(self, url_pattern: str, *params: FromClause) -> "QueryDecorator":
        def on_decorate(query, view_func):
            self.add(DatabaseRoute(url_pattern, query, view_func))

        decorator = QueryDecorator(on_decorate, *params)
        return decorator


class QueryDecorator(Query):
    on_decorate: t.Callable

    def __init__(
        self,
        on_decorate: t.Callable[["QueryDecorator", t.Callable], None],
        *args,
        **kwargs,
    ):
        self.on_decorate = on_decorate  # type: ignore
        print(f"{args=}, {kwargs=}")
        super().__init__(*args, **kwargs)

    def __call__(
        self, callable: t.Callable[..., Response]
    ) -> t.Callable[..., Response]:
        self.on_decorate(self, callable)
        return callable


class DatabaseRoute(Route):
    def __init__(self, format_string, query, callable: t.Callable[..., Response]):
        self.query = query
        self.callable = callable
        self.url_entity = func.printf(
            format_string, *(x["expr"] for x in query.column_descriptions)
        )
        self.annotated_query = query.add_columns(self.url_entity).only_return_tuples(
            True
        )

    def resolve(self, session, url: str) -> t.Optional[Response]:
        result = (
            self.annotated_query.with_session(session)
            .filter(self.url_entity == url)
            .one_or_none()
        )
        if result is None:
            return None
        return self.callable(*result[:-1])

    def get_all(self, session) -> t.Iterable[t.Tuple[str, Response]]:
        for *params, url in self.annotated_query.with_session(session):
            yield url, self.callable(*params)


query = Query
