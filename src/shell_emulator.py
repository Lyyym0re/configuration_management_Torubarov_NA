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
) -> None:
    """Обрабатывать команды до exit или конца входного потока."""
    while True:
        print(format_prompt(), end="", file=output_stream, flush=True)
        try:
            line = input_stream.readline()
        except (EOFError, KeyboardInterrupt):
            print(file=output_stream)
            break
        if line == "":
            break

        try:
            arguments = parse_command(line)
        except ParseError as error:
            print(f"Ошибка разбора команды: {error}", file=output_stream)
            continue
        if not dispatch_command(arguments, output_stream):
            break


def main() -> None:
    """Запустить интерактивный цикл команд."""
    repl()


if __name__ == "__main__":
    main()
