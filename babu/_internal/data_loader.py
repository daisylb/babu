import typing as t
from importlib import import_module
from pathlib import Path, PurePath

from ruamel.yaml import YAML
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from ..db import Content, Model

yaml = YAML(typ="safe")
CONTENT = object()


def load_path(session: Session, import_path: str):
    module = import_module(import_path)
    data_root = Path(module.__file__).parent / "data"
    content_iterator = loop_over_tree(data_root)
    load_files(session, content_iterator)


def loop_over_tree(root: Path):
    for child in root.glob("**/*"):
        if not child.is_file():
            continue
        relative_path = child.relative_to(root)
        with child.open("r") as f:
            content = f.read()
        yield relative_path, content


def load_files(session: Session, files: t.Iterable[t.Tuple[PurePath, str]]):
    for path, content in files:
        load_file(session, path, content)


def load_file(session: Session, path: PurePath, content: str):
    data = deserialize_file(path.suffix, content)
    if "_type" in data:
        cls = Model._decl_class_registry[data["_type"]]  # type: ignore
    else:
        for model_class in Model._decl_class_registry.values():
            if hasattr(model_class, "babu_paths"):
                for path_glob in model_class.babu_paths:
                    if path.match(path_glob):
                        cls = model_class
                        break
    inst = cls()
    inst.id = path.with_name(path.stem).as_posix()
    for k, v in data.items():
        if k == "_type":
            continue
        if k == CONTENT:
            inspector = inspect(cls)
            for col in inspector.columns:
                if isinstance(col.type, Content):
                    k = col.name
                    break
            else:
                raise ValueError(f"Class {cls} has no content column")
        setattr(inst, k, v)
    session.add(inst)
    session.commit()


def deserialize_file(ext: str, content: str) -> dict:
    if ext in (".yml", ".yaml"):
        return yaml.load(content)
    if ext in (".md", ".mdn", ".mkd", ".mkdn", ".markdown"):
        return deserialize_markup(content)
    raise ValueError(ext)


def deserialize_markup(content: str) -> dict:
    if content.startswith("---"):
        # YAML front-matter
        _, front_matter_str, body_str = content.split("---", 2)
        result = yaml.load(front_matter_str)
        result[CONTENT] = body_str
        return result
    # No front-matter; the entire thing is content
    return {CONTENT: content}
