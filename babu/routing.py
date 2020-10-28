import typing as t

from parse import parse
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

    def db_view(self, url_pattern: str, **kwargs: FromClause) -> "QueryDecorator":
        def on_decorate(query, view_func):
            self.add(DatabaseRoute(url_pattern, query, view_func))

        decorator = QueryDecorator(on_decorate, **kwargs)
        return decorator


class QueryDecorator(Query):
    on_decorate: t.Callable

    def __init__(
        self,
        on_decorate: t.Callable[["QueryDecorator", t.Callable], None],
        **kwargs,
    ):
        self.entity_name_map = kwargs
        self.on_decorate = on_decorate  # type: ignore
        super().__init__(tuple(kwargs.values()))

    def __call__(
        self, callable: t.Callable[..., Response]
    ) -> t.Callable[..., Response]:
        self.on_decorate(self, callable)
        return callable


class DatabaseRoute(Route):
    def __init__(self, url_pattern, query, callable: t.Callable[..., Response]):
        self.query = query
        self.callable = callable
        self.url_pattern = url_pattern

    def resolve(self, session, url: str) -> t.Optional[Response]:
        parse_result = parse(self.url_pattern, url)
        if parse_result is None:
            return None

        query = self.query

        for k, v in parse_result.named.entries():
            query = query.filter(query.entity_name_map[k] == v)

        result = query.with_session(session).one_or_none()
        if result is None:
            return None
        return self.callable(**result)

    def get_all(self, session) -> t.Iterable[t.Tuple[str, Response]]:
        for row in self.query.with_session(session):
            result_dict = {k: v for k, v in zip(self.query.entity_name_map.keys(), row)}
            print(f"{self.query.entity_name_map=} {row=} {result_dict=}")
            url = self.url_pattern.format(**result_dict)
            yield url, self.callable(**result_dict)


query = Query
