#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan a markdown or text file for high-risk finance expressions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


RISK_WORDS = {
    "买入": "改为“公开资料显示的产业变化”或删除买卖动作。",
    "卖出": "改为“需要注意的经营或行业风险”。",
    "持有": "改为“商业模式和财报验证路径”。",
    "目标价": "删除价格判断，改为“市场预期差异”。",
    "低位": "删除位置暗示，改为“观察产业数据和财务兑现”。",
    "潜伏": "删除操作暗示，改为“持续跟踪公开资料”。",
    "翻倍": "删除收益暗示，改为“增长假设需要验证”。",
    "稳赚": "删除收益承诺，改为“存在不确定性”。",
    "牛股": "改为“产业链案例”。",
    "妖股": "删除情绪化股票标签。",
    "龙头股": "改为“该环节重要参与者”。",
    "核心标的": "改为“公开资料样本”。",
    "股票池": "改为“案例库”或“资料清单”。",
    "最受益": "改为“业务结构与该环节相关”。",
    "弹性最大": "改为“业务结构对该环节更敏感”。",
    "下周重点": "改为“后续可以观察行业数据变化”。",
    "重点关注": "改为“继续跟踪公开资料”。",
    "私信": "删除私信引流表达。",
    "进群": "删除进群引流表达。",
    "评论区发": "删除评论区发代码或名单表达。",
    "代码": "避免股票代码引导，必要时改为“资料来源”。",
    "带你操作": "删除带单表达。",
    "稳赚不赔": "删除收益承诺。",
    "低风险高收益": "删除风险收益承诺。",
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, "无法用 utf-8 或 gb18030 读取文件")


def scan(path: Path) -> list[tuple[int, str, str, str]]:
    text = read_text(path)
    hits: list[tuple[int, str, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for word, suggestion in RISK_WORDS.items():
            if word in line:
                hits.append((line_no, word, line.strip(), suggestion))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描文案中的高风险财经表达。")
    parser.add_argument("file", help="要扫描的 markdown 或 txt 文件")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 2
    if path.suffix.lower() not in {".md", ".txt"}:
        print("提醒：建议扫描 markdown 或 txt 文件。", file=sys.stderr)

    hits = scan(path)
    if not hits:
        print("未发现高风险词。")
        return 0

    print(f"发现 {len(hits)} 处高风险表达：")
    for line_no, word, line, suggestion in hits:
        print(f"\n第 {line_no} 行：命中“{word}”")
        print(f"原文：{line}")
        print(f"建议：{suggestion}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

