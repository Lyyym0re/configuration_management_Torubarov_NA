"""Команды оболочки для снимка виртуальной файловой системы."""

from dataclasses import dataclass
from typing import TextIO

from src.vfs import VfsEntry, VirtualFileSystem


class CommandError(ValueError):
    """Ошибка выполнения команды оболочки."""


@dataclass
class ShellState:
    """Текущий каталог внутри загруженного снимка VFS."""

    filesystem: VirtualFileSystem | None = None
    current_path: tuple[str, ...] = ()

    @property
    def display_path(self) -> str:
        """Вернуть путь для приглашения оболочки."""
        if not self.current_path:
            return "~"
        return "~/" + "/".join(self.current_path)


def resolve_path(
    state: ShellState, raw_path: str
) -> tuple[VfsEntry, tuple[str, ...]]:
    """Найти элемент VFS по абсолютному или относительному пути."""
    if state.filesystem is None:
        raise CommandError("VFS не загружена")
    parts = [] if raw_path.startswith("/") else list(state.current_path)
    entry = _find_entry(state.filesystem.root, parts, raw_path)
    for part in raw_path.split("/"):
        if part == "" and not parts:
            continue
        if not entry.is_directory:
            raise CommandError(f"не каталог: {entry.name}")
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            entry = _find_entry(state.filesystem.root, parts, raw_path)
        else:
            parts.append(part)
            entry = _find_entry(state.filesystem.root, parts, raw_path)
    return entry, tuple(parts)


def _find_entry(
    root: VfsEntry, parts: list[str], raw_path: str
) -> VfsEntry:
    """Найти элемент снимка по уже нормализованным сегментам."""
    entry = root
    for part in parts:
        if not entry.is_directory:
            raise CommandError(f"не каталог: {entry.name}")
        child = next(
            (item for item in entry.children if item.name == part),
            None,
        )
        if child is None:
            raise CommandError(f"путь не найден: {raw_path}")
        entry = child
    return entry


def _single_path(arguments: list[str], default: str) -> str:
    """Принять один путь или использовать путь по умолчанию."""
    if len(arguments) > 1:
        raise CommandError("ожидается не более одного пути")
    return arguments[0] if arguments else default


def command_ls(
    state: ShellState, arguments: list[str], output: TextIO
) -> None:
    """Показать содержимое каталога или имя файла."""
    path = _single_path(arguments, ".")
    entry, _ = resolve_path(state, path)
    if not entry.is_directory:
        print(entry.name, file=output)
        return
    for child in entry.children:
        suffix = "/" if child.is_directory else ""
        print(f"{child.name}{suffix}", file=output)


def command_cd(state: ShellState, arguments: list[str]) -> None:
    """Перейти в каталог внутри VFS."""
    path = _single_path(arguments, "/")
    entry, parts = resolve_path(state, path)
    if not entry.is_directory:
        raise CommandError(f"не каталог: {path}")
    state.current_path = parts


def command_echo(arguments: list[str], output: TextIO) -> None:
    """Вывести аргументы одной строкой."""
    print(" ".join(arguments), file=output)


def command_tree(
    state: ShellState, arguments: list[str], output: TextIO
) -> None:
    """Показать дерево каталога внутри VFS."""
    path = _single_path(arguments, ".")
    entry, _ = resolve_path(state, path)
    if not entry.is_directory:
        raise CommandError(f"не каталог: {path}")
    print(f"{entry.name}/" if entry.name != "." else ".", file=output)
    _print_children(entry, "", output)


def _print_children(entry: VfsEntry, prefix: str, output: TextIO) -> None:
    """Рекурсивно вывести дочерние элементы в порядке снимка."""
    for index, child in enumerate(entry.children):
        last = index == len(entry.children) - 1
        branch = "`-- " if last else "|-- "
        suffix = "/" if child.is_directory else ""
        print(f"{prefix}{branch}{child.name}{suffix}", file=output)
        if child.is_directory:
            continuation = "    " if last else "|   "
            _print_children(child, prefix + continuation, output)
