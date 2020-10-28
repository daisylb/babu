import typing as t
from importlib import import_module

import click
from ruamel.yaml import YAML  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from babu.db import Model

from ..publishers import Publisher
from .data_loader import load_path


@click.command()
@click.argument("import_path")
def cli(import_path):
    main(import_path)


def main(import_path):
    load_models(import_path)
    Session = create_db()
    session = Session()
    load_path(session, import_path)
    iterbl = build_site(session, import_path)
    publisher = load_publisher(import_path)
    publisher(iterbl)


def load_models(import_path: str):
    model_path = f"{import_path}.models"
    import_module(model_path)


def create_db() -> t.Callable[[], Session]:
    # TODO: replace this with an on-disk DB with change detection of some kind
    engine = create_engine("sqlite:///:memory:")
    Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session


def build_site(session: Session, import_path: str):
    views_path = f"{import_path}.views"
    views_mod = t.cast(t.Any, import_module(views_path))
    root_router = views_mod.app
    return root_router.get_all(session)


def load_publisher(import_path: str) -> Publisher:
    mod = t.cast(t.Any, import_module(import_path))
    return mod.publisher


if __name__ == "__main__":
    cli()
