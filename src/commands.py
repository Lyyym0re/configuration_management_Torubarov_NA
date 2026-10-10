"""Команды оболочки для снимка виртуальной файловой системы."""

from dataclasses import dataclass, replace
from typing import TextIO

from src.vfs import (
    VfsEntry,
    VfsLoadError,
    VirtualFileSystem,
    describe_vfs,
    load_vfs,
)


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


def command_rm(state: ShellState, arguments: list[str]) -> None:
    """Удалить файл или каталог рекурсивно только из снимка VFS."""
    recursive = bool(arguments and arguments[0] in ("-r", "-R"))
    operands = arguments[1:] if recursive else arguments
    if len(operands) != 1:
        raise CommandError("использование: rm [-r] путь")
    path = operands[0]
    if path.startswith("-"):
        raise CommandError(f"неизвестный параметр: {path}")
    entry, parts = resolve_path(state, path)
    if not parts:
        raise CommandError("нельзя удалить корень VFS")
    if entry.is_directory and not recursive:
        raise CommandError(f"каталог требует -r: {path}")
    if entry.is_directory and state.current_path[:len(parts)] == parts:
        raise CommandError(f"нельзя удалить текущий каталог: {path}")
    assert state.filesystem is not None
    files, directories, size = _entry_totals(entry)
    root = _remove_entry(state.filesystem.root, parts)
    state.filesystem = replace(
        state.filesystem,
        root=root,
        file_count=state.filesystem.file_count - files,
        directory_count=state.filesystem.directory_count - directories,
        total_bytes=state.filesystem.total_bytes - size,
    )


def _entry_totals(entry: VfsEntry) -> tuple[int, int, int]:
    """Посчитать файлы, каталоги и байты удаляемого поддерева."""
    if not entry.is_directory:
        return 1, 0, entry.content_size
    files, directories, size = 0, 1, 0
    for child in entry.children:
        child_files, child_directories, child_size = _entry_totals(child)
        files += child_files
        directories += child_directories
        size += child_size
    return files, directories, size


def _remove_entry(node: VfsEntry, parts: tuple[str, ...]) -> VfsEntry:
    """Создать новую ветку снимка без указанного элемента."""
    if len(parts) == 1:
        children = tuple(
            child for child in node.children if child.name != parts[0]
        )
        return replace(node, children=children)
    children = tuple(
        _remove_entry(child, parts[1:]) if child.name == parts[0] else child
        for child in node.children
    )
    return replace(node, children=children)


def command_vfs_load(
    state: ShellState, arguments: list[str], output: TextIO
) -> None:
    """Заменить текущий снимок VFS новым снимком с диска."""
    if len(arguments) != 1:
        raise CommandError("использование: vfs-load путь")
    try:
        filesystem = load_vfs(arguments[0])
    except VfsLoadError as error:
        raise CommandError(f"не удалось загрузить VFS: {error}") from error
    state.filesystem = filesystem
    state.current_path = ()
    print(describe_vfs(filesystem), file=output)
