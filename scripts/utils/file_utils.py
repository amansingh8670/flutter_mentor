from pathlib import Path
from typing import Iterator


# ==========================================================
# FILE DISCOVERY
# ==========================================================

def iter_files(
    root: str | Path,
    extensions: tuple[str, ...] = (".dart",),
) -> Iterator[Path]:
    """
    Recursively yields files having the given extensions.
    """

    root = Path(root)

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() in extensions:
            yield path


# ==========================================================
# READ FILE
# ==========================================================

def read_file(
    path: str | Path,
) -> str:
    """
    Read a UTF-8 text file.
    """

    return Path(path).read_text(
        encoding="utf-8",
        errors="ignore",
    )


# ==========================================================
# WRITE FILE
# ==========================================================

def write_file(
    path: str | Path,
    content: str,
):
    """
    Write UTF-8 text.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )


# ==========================================================
# RELATIVE PATH
# ==========================================================

def relative_path(
    file_path: str | Path,
    repo_root: str | Path,
) -> str:
    """
    Relative path inside repository.
    """

    return str(
        Path(file_path).relative_to(
            Path(repo_root)
        )
    )


# ==========================================================
# FILE NAME
# ==========================================================

def file_name(
    path: str | Path,
) -> str:
    return Path(path).name


# ==========================================================
# FILE STEM
# ==========================================================

def file_stem(
    path: str | Path,
) -> str:
    return Path(path).stem


# ==========================================================
# FILE EXTENSION
# ==========================================================

def extension(
    path: str | Path,
) -> str:
    return Path(path).suffix.lower()


# ==========================================================
# EXISTS
# ==========================================================

def exists(
    path: str | Path,
) -> bool:
    return Path(path).exists()


# ==========================================================
# ENSURE DIRECTORY
# ==========================================================

def ensure_directory(
    directory: str | Path,
):
    Path(directory).mkdir(
        parents=True,
        exist_ok=True,
    )


# ==========================================================
# FILE SIZE
# ==========================================================

def file_size(
    path: str | Path,
) -> int:
    return Path(path).stat().st_size


# ==========================================================
# IS HIDDEN
# ==========================================================

def is_hidden(
    path: str | Path,
) -> bool:
    return any(
        part.startswith(".")
        for part in Path(path).parts
    )


# ==========================================================
# SHOULD INDEX
# ==========================================================

def should_index(
    path: str | Path,
) -> bool:
    """
    Skip generated/build folders.
    """

    path = Path(path)

    blocked = {
        ".dart_tool",
        "build",
        ".git",
        "ios",
        "android",
        "linux",
        "macos",
        "windows",
        "web",
        "test",
    }

    return not any(
        part in blocked
        for part in path.parts
    )


# ==========================================================
# DART FILES
# ==========================================================

def dart_files(
    repo_root: str | Path,
) -> Iterator[Path]:
    """
    Returns indexable Dart files.
    """

    for file in iter_files(
        repo_root,
        (".dart",),
    ):

        if should_index(file):
            yield file