import typing as t
from .response import Response
from pathlib import Path, PurePosixPath
import attr
from shutil import rmtree


@attr.s
class UnsupportedStatus(ValueError):
    path: str
    response: Response


class Publisher(t.Protocol):
    def __call__(self, pages: t.Iterable[t.Tuple[str, Response]]):
        ...


class Directory(Publisher):
    def __init__(self, root):
        self.root = Path(root).resolve()

    def __call__(self, pages: t.Iterable[t.Tuple[str, Response]]):
        rmtree(self.root)
        for path, response in pages:
            if response.status != 200:
                raise UnsupportedStatus(path, response)
            path_obj = PurePosixPath(path).relative_to("/")
            target_path: Path = self.root / path_obj
            print(repr(path))
            print(target_path)
            if path.endswith('/'):
                target_path /= 'index.html'
            print(target_path)
            if not self.root in target_path.parents:
                raise ValueError(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with target_path.open("w") as f:
                f.write(response.body)
