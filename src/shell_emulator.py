"""REPL и конфигурация эмулятора оболочки."""

import argparse
import getpass
import os
import shlex
import socket
import sys
from enum import Enum, auto
from typing import TextIO

from src.commands import (
    CommandError,
    ShellState,
    command_cd,
    command_echo,
    command_ls,
    command_rm,
    command_tree,
    command_vfs_load,
)
from src.vfs import VfsLoadError, describe_vfs, load_vfs

PROMPT_ENDING = "$ "


class ParseError(ValueError):
    """Ошибка синтаксиса введённой команды."""


class CommandStatus(Enum):
    """Результат обработки одной команды."""

    CONTINUE = auto()
    EXIT = auto()
    ERROR = auto()


def format_prompt(state: ShellState) -> str:
    """Собрать приглашение из текущих данных ОС."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:{state.display_path}{PROMPT_ENDING}"


def parse_command(line: str) -> list[str]:
    """Раскрыть переменные окружения и разобрать оболочечные кавычки."""
    expanded_line = os.path.expandvars(line)
    try:
        lexer = shlex.shlex(expanded_line, posix=True)
        lexer.whitespace_split = True
        lexer.escape = ""
        return list(lexer)
    except ValueError as error:
        raise ParseError(str(error)) from error


def dispatch_command(
    arguments: list[str], state: ShellState, output: TextIO
) -> CommandStatus:
    """Выполнить команду и вернуть её статус."""
    if not arguments:
        return CommandStatus.CONTINUE

    name, *command_arguments = arguments
    try:
        if name == "ls":
            command_ls(state, command_arguments, output)
        elif name == "cd":
            command_cd(state, command_arguments)
        elif name == "echo":
            command_echo(command_arguments, output)
        elif name == "tree":
            command_tree(state, command_arguments, output)
        elif name == "rm":
            command_rm(state, command_arguments)
        elif name == "vfs-load":
            command_vfs_load(state, command_arguments, output)
        elif name == "exit":
            return CommandStatus.EXIT
        else:
            raise CommandError(f"неизвестная команда: {name}")
    except CommandError as error:
        print(f"Ошибка: {error}", file=output)
        return CommandStatus.ERROR
    return CommandStatus.CONTINUE


def process_line(
    line: str, state: ShellState, output: TextIO
) -> CommandStatus:
    """Разобрать строку, выполнить команду и напечатать ошибку разбора."""
    try:
        arguments = parse_command(line)
    except ParseError as error:
        message = f"Ошибка разбора команды: {error}"
        print(message, file=output)
        return CommandStatus.ERROR
    return dispatch_command(arguments, state, output)


def repl(
    state: ShellState,
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
    startup_stream: TextIO | None = None,
) -> None:
    """Сначала выполнить демонстрационные команды, затем читать ввод."""
    streams: list[tuple[TextIO, bool, bool]] = []
    if startup_stream is not None:
        streams.append((startup_stream, False, True))
    is_interactive = getattr(input_stream, "isatty", lambda: True)()
    streams.append((input_stream, is_interactive, False))

    try:
        for stream, show_prompt_first, stop_on_error in streams:
            if not run_stream(
                stream,
                show_prompt_first,
                stop_on_error,
                state,
                output_stream,
            ):
                return
    except (EOFError, KeyboardInterrupt):
        print(file=output_stream)


def run_stream(
    stream: TextIO,
    show_prompt_first: bool,
    stop_on_error: bool,
    state: ShellState,
    output: TextIO,
) -> bool:
    """Обработать поток команд; остановить скрипт на первой ошибке."""
    while True:
        if show_prompt_first:
            print(format_prompt(state), end="", file=output, flush=True)
        line = stream.readline()
        if line == "":
            return True
        if not show_prompt_first:
            print(format_prompt(state), end="", file=output)
            print(line, end="", file=output)

        result = process_line(line, state, output)
        if result is CommandStatus.EXIT:
            return False
        if stop_on_error and result is CommandStatus.ERROR:
            return True
        if not stop_on_error and result is CommandStatus.ERROR:
            continue


def create_argument_parser() -> argparse.ArgumentParser:
    """Описать параметры запуска эмулятора."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="путь к стартовому скрипту команд эмулятора",
    )
    return parser


def print_configuration(arguments: argparse.Namespace) -> None:
    """Показать все параметры командной строки."""
    print("Параметры запуска:")
    print(f"VFS: {arguments.vfs or '<не задан>'}")
    print(f"Стартовый скрипт: {arguments.script or '<не задан>'}")


def main(argv: list[str] | None = None) -> None:
    """Показать настройки, загрузить VFS, выполнить скрипт и запустить REPL."""
    parser = create_argument_parser()
    arguments = parser.parse_args(argv)
    print_configuration(arguments)
    filesystem = None
    if arguments.vfs:
        try:
            filesystem = load_vfs(arguments.vfs)
        except VfsLoadError as error:
            print(f"Ошибка загрузки VFS: {error}")
        else:
            print(describe_vfs(filesystem))
    else:
        print("VFS не задана.")
    state = ShellState(filesystem)

    startup_path = arguments.script or os.environ.pop(
        "SHELL_EMULATOR_STARTUP", None
    )
    if startup_path is None:
        repl(state)
        return

    try:
        with open(startup_path, encoding="utf-8") as startup_stream:
            repl(state, startup_stream=startup_stream)
    except OSError as error:
        print(f"Не удалось прочитать стартовый скрипт: {error}")
        repl(state)


if __name__ == "__main__":
    main()
