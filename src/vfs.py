"""Загрузка файловой системы с диска в неизменяемую структуру памяти."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class VfsLoadError(OSError):
    """Ошибка чтения исходного каталога VFS."""


@dataclass(frozen=True)
class VfsEntry:
    """Файл или каталог, сохранённый в снимке VFS."""

    name: str
    relative_path: str
    is_directory: bool
    content: bytes | None = None
    children: tuple[VfsEntry, ...] = ()

    @property
    def content_size(self) -> int:
        """Вернуть размер содержимого файла в байтах."""
        return len(self.content or b"")


@dataclass(frozen=True)
class VirtualFileSystem:
    """Неизменяемый снимок каталога и его файлов в памяти."""

    source_path: str
    root: VfsEntry
    file_count: int
    directory_count: int
    total_bytes: int


def load_vfs(source_path: str) -> VirtualFileSystem:
    """Прочитать каталог VFS целиком, не изменяя источник на диске."""
    source = Path(source_path).expanduser()
    if source.is_symlink():
        raise VfsLoadError(f"Корень VFS не может быть ссылкой: {source_path}")
    if not source.is_dir():
        raise VfsLoadError(f"Путь VFS не является каталогом: {source_path}")

    root, file_count, directory_count, total_bytes = _read_directory(
        source,
        ".",
    )
    return VirtualFileSystem(
        source_path,
        root,
        file_count,
        directory_count,
        total_bytes,
    )


def _read_directory(
    directory: Path,
    relative_path: str,
) -> tuple[VfsEntry, int, int, int]:
    """Рекурсивно прочитать каталог и собрать счётчики снимка."""
    try:
        children = sorted(
            directory.iterdir(),
            key=lambda path: (path.name.casefold(), path.name),
        )
    except OSError as error:
        message = f"Не удалось прочитать каталог {directory}: {error}"
        raise VfsLoadError(message) from error

    entries: list[VfsEntry] = []
    file_count = 0
    directory_count = 0
    total_bytes = 0
    for child in children:
        child_path = _join_relative(relative_path, child.name)
        if child.is_symlink():
            message = f"Символическая ссылка не поддерживается: {child}"
            raise VfsLoadError(message)
        if child.is_dir():
            entry, files, directories, size = _read_directory(child, child_path)
            entries.append(entry)
            file_count += files
            directory_count += directories + 1
            total_bytes += size
        elif child.is_file():
            entries.append(_read_file(child, child_path))
            file_count += 1
            total_bytes += entries[-1].content_size
        else:
            message = f"Неподдерживаемый объект в каталоге VFS: {child}"
            raise VfsLoadError(message)

    name = directory.name if relative_path != "." else "."
    node = VfsEntry(name, relative_path, True, children=tuple(entries))
    return node, file_count, directory_count, total_bytes


def _read_file(path: Path, relative_path: str) -> VfsEntry:
    """Сохранить содержимое файла как неизменяемые байты."""
    try:
        content = path.read_bytes()
    except OSError as error:
        message = f"Не удалось прочитать файл {path}: {error}"
        raise VfsLoadError(message) from error
    return VfsEntry(path.name, relative_path, False, content)


def _join_relative(parent: str, name: str) -> str:
    """Собрать переносимый относительный путь элемента VFS."""
    return name if parent == "." else f"{parent}/{name}"


def describe_vfs(filesystem: VirtualFileSystem) -> str:
    """Сформировать краткую сводку загруженного снимка."""
    return (
        f"VFS загружена в память: файлов — {filesystem.file_count}, "
        f"каталогов — {filesystem.directory_count}, "
        f"данных — {filesystem.total_bytes} байт."
    )
