"""Минимальный REPL для первого этапа эмулятора оболочки."""

import getpass
import os
import shlex
import socket
import sys
from typing import TextIO

PROMPT_ENDING = "$ "


class ParseError(ValueError):
    """Ошибка синтаксиса введённой команды."""


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
) -> bool:
    """Выполнить команду; вернуть False, когда нужно завершить REPL."""
    if not arguments:
        return True

    name, *command_arguments = arguments
    if name in ("ls", "cd"):
        command_stub(name, command_arguments, output)
    elif name == "exit":
        return False
    else:
        print(f"Ошибка: неизвестная команда: {name}", file=output)
    return True


def repl(
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
    startup_stream: TextIO | None = None,
) -> None:
    """Сначала выполнить демонстрационные команды, затем читать ввод."""
    streams = []
    if startup_stream is not None:
        streams.append((startup_stream, False))
    is_interactive = getattr(input_stream, "isatty", lambda: True)()
    streams.append((input_stream, is_interactive))

    try:
        for stream, show_prompt_first in streams:
            while True:
                if show_prompt_first:
                    print(
                        format_prompt(),
                        end="",
                        file=output_stream,
                        flush=True,
                    )
                line = stream.readline()
                if line == "":
                    break
                if not show_prompt_first:
                    print(format_prompt(), end="", file=output_stream)
                    print(line, end="", file=output_stream)

                try:
                    arguments = parse_command(line)
                except ParseError as error:
                    message = f"Ошибка разбора команды: {error}"
                    print(message, file=output_stream)
                    continue
                if not dispatch_command(arguments, output_stream):
                    return
    except (EOFError, KeyboardInterrupt):
        print(file=output_stream)


def main() -> None:
    """Запустить интерактивный цикл команд."""
    startup_path = os.environ.pop("SHELL_EMULATOR_STARTUP", None)
    if startup_path is None:
        repl()
        return

    try:
        with open(startup_path, encoding="utf-8") as startup_stream:
            repl(startup_stream=startup_stream)
    except OSError as error:
        print(f"Не удалось прочитать демонстрационные команды: {error}")
        repl()


if __name__ == "__main__":
    main()
