"""Print a YAML document as a table: a stand-in for a real service."""

import sys

import yaml
from rich.console import Console
from rich.table import Table


def main() -> int:
    source = sys.argv[1] if len(sys.argv) > 1 else None
    text = open(source, encoding="utf-8").read() if source else sys.stdin.read()
    doc = yaml.safe_load(text) or {}
    if not isinstance(doc, dict):
        print("expected a YAML mapping", file=sys.stderr)
        return 1
    table = Table("key", "value", title=source or "stdin")
    for key, value in doc.items():
        table.add_row(str(key), str(value))
    Console().print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
