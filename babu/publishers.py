import typing as t
from .response import Response
from pathlib import Path, PurePosixPath
import attr
from shutil import rmtree, copyfileobj
from io import TextIOWrapper


# ! Utility functions

@attr.s
class UnsupportedStatus(ValueError):
    path: str = attr.ib()
    response: Response = attr.ib()


class Publisher(t.Protocol):
    def __call__(self, pages: t.Iterable[t.Tuple[str, Response]]):
        ...


def write(content: t.Union[str, bytes, t.TextIO, t.BinaryIO], output: t.BinaryIO):
    if isinstance(content, str):
        output.write(content.encode("utf8"))
    elif isinstance(content, bytes):
        output.write(content)
    elif isinstance(content.read(0), str):
        copyfileobj(
            content,
            TextIOWrapper(output, encoding="utf8", newline=""),
        )  # type: ignore
    elif isinstance(content.read(0), bytes):
        copyfileobj(content, output)  # type: ignore
    else:
        raise TypeError(content)


# ! Publishers


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
            if path.endswith("/"):
                target_path /= "index.html"
            if not self.root in target_path.parents:
                raise ValueError(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with target_path.open("wb") as f:
                write(response.body, f)
