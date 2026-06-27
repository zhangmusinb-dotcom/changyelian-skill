#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check whether a markdown source list contains S/A/B/C source labels."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SOURCE_PATTERNS = {
    "S": re.compile(r"(?:^|[\s\-#：:])S\s*级", re.IGNORECASE),
    "A": re.compile(r"(?:^|[\s\-#：:])A\s*级", re.IGNORECASE),
    "B": re.compile(r"(?:^|[\s\-#：:])B\s*级", re.IGNORECASE),
    "C": re.compile(r"(?:^|[\s\-#：:])C\s*级", re.IGNORECASE),
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, "无法用 utf-8 或 gb18030 读取文件")


def check_sources(path: Path) -> tuple[dict[str, int], list[str]]:
    text = read_text(path)
    counts = {level: len(pattern.findall(text)) for level, pattern in SOURCE_PATTERNS.items()}
    warnings: list[str] = []

    if sum(counts.values()) == 0:
        warnings.append("未发现 S/A/B/C 来源标注，请补充来源等级。")
    if counts["S"] == 0 and counts["A"] == 0:
        warnings.append("证据质量不足：没有 S 级或 A 级来源。")
    if counts["C"] > 0 and counts["S"] == 0 and counts["A"] == 0 and counts["B"] == 0:
        warnings.append("不能作为事实依据：当前只有 C 级来源。")

    return counts, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 markdown 来源列表的证据质量。")
    parser.add_argument("file", help="要检查的 markdown 文件")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 2
    if path.suffix.lower() != ".md":
        print("提醒：该脚本主要用于 markdown 文件。", file=sys.stderr)

    counts, warnings = check_sources(path)
    print("来源标注统计：")
    for level in ("S", "A", "B", "C"):
        print(f"- {level}级：{counts[level]}")

    if not warnings:
        print("来源等级检查通过。")
        return 0

    print("\n提醒：")
    for warning in warnings:
        print(f"- {warning}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

