import typing as t
from sqlalchemy import func
from sqlalchemy.sql.expression import FromClause
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
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


class DatabaseRoute(Route):
    def __init__(
        self, query: RouteQuery, callable: t.Callable[..., Response]
    ):
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


class RouteQuery(Query):
    url_pattern: str
    parameter_map: t.Mapping[str, FromClause]

    def __init__(self, url_pattern: str, **params: t.Mapping[str, FromClause]):
        super().__init__(*params.values())
        self.url_pattern = url_pattern
        self.parameter_map = params

    def __call__(self, callable: t.Callable[..., Response]):
        pass