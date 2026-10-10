"""Запустить и проверить диалог первого этапа без команды exit."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run.py"


def main() -> int:
    """Показать диалог REPL и проверить ожидаемые примеры."""
    variable_name = "SHELL_EMULATOR_DEMO"
    variable_value = "value from environment"
    environment = os.environ.copy()
    environment[variable_name] = variable_value
    environment["PYTHONIOENCODING"] = "utf-8"
    commands = (
        f'ls "${variable_name}"\n'
        f'cd "folder with spaces" "${variable_name}"\n'
        "unknown-command argument\n"
        "cd \"unterminated\n"
    )
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        input=commands,
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=ROOT,
        env=environment,
        check=False,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    expected_output = (
        f"ls ['{variable_value}']",
        f"cd ['folder with spaces', '{variable_value}']",
        "Ошибка: неизвестная команда: unknown-command",
        "Ошибка разбора команды:",
    )
    missing = [text for text in expected_output if text not in result.stdout]
    if result.returncode != 0 or missing:
        print(f"Проверка не пройдена. Не найдено: {missing}", file=sys.stderr)
        return 1
    print("Проверка этапа 1 пройдена.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
