"""REPL и конфигурация эмулятора оболочки."""

import argparse
import getpass
import os
import shlex
import socket
import sys
from enum import Enum, auto
from typing import TextIO

PROMPT_ENDING = "$ "


class ParseError(ValueError):
    """Ошибка синтаксиса введённой команды."""


class CommandStatus(Enum):
    """Результат обработки одной команды."""

    CONTINUE = auto()
    EXIT = auto()
    ERROR = auto()


def format_prompt() -> str:
    """Собрать приглашение из текущих данных ОС."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~{PROMPT_ENDING}"


def parse_command(line: str) -> list[str]:
    """Раскрыть переменные окружения и разобрать оболочечные кавычки."""
    expanded_line = os.path.expandvars(line)
    try:
        return shlex.split(expanded_line, posix=True)
    except ValueError as error:
        raise ParseError(str(error)) from error


def command_stub(name: str, arguments: list[str], output: TextIO) -> None:
    """Напечатать имя команды-заглушки и её аргументы."""
    print(f"{name} {arguments}", file=output)


def dispatch_command(
    arguments: list[str], output: TextIO
) -> CommandStatus:
    """Выполнить команду и вернуть её статус."""
    if not arguments:
        return CommandStatus.CONTINUE

    name, *command_arguments = arguments
    if name in ("ls", "cd"):
        command_stub(name, command_arguments, output)
    elif name == "exit":
        return CommandStatus.EXIT
    else:
        print(f"Ошибка: неизвестная команда: {name}", file=output)
        return CommandStatus.ERROR
    return CommandStatus.CONTINUE


def process_line(line: str, output: TextIO) -> CommandStatus:
    """Разобрать строку, выполнить команду и напечатать ошибку разбора."""
    try:
        arguments = parse_command(line)
    except ParseError as error:
        message = f"Ошибка разбора команды: {error}"
        print(message, file=output)
        return CommandStatus.ERROR
    return dispatch_command(arguments, output)


def repl(
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
                output_stream,
            ):
                return
    except (EOFError, KeyboardInterrupt):
        print(file=output_stream)


def run_stream(
    stream: TextIO,
    show_prompt_first: bool,
    stop_on_error: bool,
    output: TextIO,
) -> bool:
    """Обработать поток команд; остановить скрипт на первой ошибке."""
    while True:
        if show_prompt_first:
            print(format_prompt(), end="", file=output, flush=True)
        line = stream.readline()
        if line == "":
            return True
        if not show_prompt_first:
            print(format_prompt(), end="", file=output)
            print(line, end="", file=output)

        result = process_line(line, output)
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
    """Показать настройки, выполнить стартовый скрипт и запустить REPL."""
    parser = create_argument_parser()
    arguments = parser.parse_args(argv)
    print_configuration(arguments)

    startup_path = arguments.script or os.environ.pop(
        "SHELL_EMULATOR_STARTUP", None
    )
    if startup_path is None:
        repl()
        return

    try:
        with open(startup_path, encoding="utf-8") as startup_stream:
            repl(startup_stream=startup_stream)
    except OSError as error:
        print(f"Не удалось прочитать стартовый скрипт: {error}")
        repl()


if __name__ == "__main__":
    main()
