import argparse
import configparser
import csv
from pathlib import Path
import sys


CONFIG_FILE = Path(__file__).resolve().parents[1] / "config.ini"


def parse_numbers(value: str) -> set[int]:
    parts = [part.strip() for part in value.split(";")]
    if len(parts) != 6:
        raise ValueError("Enter exactly six integers separated by ';'.")

    try:
        return {int(part) for part in parts}
    except ValueError as exc:
        raise ValueError("All six values must be integers.") from exc


def get_forecast_file(config_file: Path = CONFIG_FILE) -> Path:
    config = configparser.ConfigParser()
    if not config.read(config_file, encoding="utf-8"):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    configured_path = Path(config.get("forecast", "forecast_output_file"))
    if not configured_path.is_absolute():
        configured_path = config_file.parent / configured_path
    return configured_path


def count_row_matches(numbers: set[int], forecast_file: Path) -> list[tuple[int, set[int]]]:
    matches_by_row = []
    with forecast_file.open("r", newline="", encoding="utf-8") as file:
        for row_number, row in enumerate(csv.reader(file, delimiter=";"), start=1):
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) != 6:
                raise ValueError(
                    f"{forecast_file}, row {row_number}: expected six integers."
                )
            try:
                row_numbers = {int(value.strip()) for value in row}
            except ValueError as exc:
                raise ValueError(
                    f"{forecast_file}, row {row_number}: expected six integers."
                ) from exc
            matches_by_row.append((row_number, numbers & row_numbers))
    return matches_by_row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Count how many input numbers occur in each configured forecast row."
    )
    parser.add_argument(
        "numbers",
        nargs="?",
        help="Six integers separated by semicolons, for example '1;2;3;4;5;6'.",
    )
    args = parser.parse_args(argv)

    try:
        number_string = args.numbers
        if number_string is None:
            number_string = input("Enter six integers separated by ';': ")
        numbers = parse_numbers(number_string)
        forecast_file = get_forecast_file()
        matches_by_row = count_row_matches(numbers, forecast_file)
        if not matches_by_row:
            raise ValueError(f"No forecast rows found in {forecast_file}.")
    except (configparser.Error, EOFError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for row_number, matches in matches_by_row:
        matched_values = ";".join(str(value) for value in sorted(matches)) or "none"
        print(f"Row {row_number}: {len(matches)} matching values ({matched_values})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
