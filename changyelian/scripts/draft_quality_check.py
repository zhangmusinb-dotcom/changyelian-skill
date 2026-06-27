#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check whether a changyelian draft meets route-discovery and style gates."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROUTE_TABLE_HEADERS = (
    "路线类型",
    "路线名称",
    "工作机制",
    "当前阶段",
    "最大卡点",
    "价值量流向",
    "反证条件",
)

ROUTE_REQUIRED_ROWS = (
    "旧路线",
    "旧路线升级",
    "新材料路线",
    "新工艺路线",
    "新架构",
    "系统路线",
    "替代",
    "竞争路线",
)

CORRECTION_PATTERNS = (
    "不是",
    "不只是",
    "不能只看",
    "不能只",
    "而是",
    "这就是为什么",
    "到底",
    "有没有",
    "为什么",
    "说明什么",
)

HIGH_RISK_PHRASES = (
    "稳赚不赔",
    "稳赚",
    "最受益",
    "核心标的",
    "龙头股",
    "股票池",
    "买入",
    "卖出",
    "持有",
    "目标价",
    "低位",
    "潜伏",
    "翻倍",
    "弹性最大",
)

PCB_TOPIC_PATTERNS = (
    "PCB",
    "CCL",
    "覆铜板",
    "高多层",
    "高速板",
    "AI服务器",
    "AI 服务器",
    "服务器PCB",
    "电子布",
)

PCB_REQUIRED_GROUPS = {
    "材料等级": (
        "低损耗",
        "Dk",
        "Df",
        "PPO",
        "碳氢",
        "PTFE",
        "M7",
        "M8",
        "M9",
        "M10",
        "HVLP",
        "VLP",
        "玻纤布",
        "石英布",
    ),
    "工艺路线": (
        "mSAP",
        "半加成",
        "减成法",
        "高多层",
        "HDI",
        "背钻",
        "激光钻孔",
        "LDI",
        "电镀",
        "阻抗",
    ),
    "设备交期或投资": (
        "设备交期",
        "交期",
        "产线投资",
        "投资",
        "激光钻孔机",
        "LDI曝光机",
        "曝光机",
        "电镀线",
        "压合设备",
        "检测设备",
    ),
    "良率和客户认证": (
        "良率",
        "客户认证",
        "认证",
        "送样",
        "批量交付",
        "产能利用率",
        "可靠性测试",
    ),
    "反证指标": (
        "反证",
        "资本开支下调",
        "扩产过快",
        "设备交期缩短",
        "认证延后",
        "价格战",
        "库存",
        "应收账款",
        "替代",
    ),
}

SOURCE_MARKERS = (
    "资料来源",
    "来源",
    "核验",
    "S级",
    "S 级",
    "A级",
    "A 级",
    "公告",
    "年报",
    "官网",
    "白皮书",
    "行业协会",
    "权威媒体",
)


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, "无法用 utf-8 或 gb18030 读取文件")


def chinese_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def count_corrections(text: str) -> int:
    return sum(text.count(pattern) for pattern in CORRECTION_PATTERNS)


def extract_video_script(text: str) -> str:
    match = re.search(
        r"(?ms)^##\s*(?:\d+\.\s*)?(?:视频文案|口播正文)\s*$"
        r"(?P<body>.*?)"
        r"^##\s+",
        text + "\n## ",
    )
    return match.group("body").strip() if match else text


def has_route_table(text: str) -> bool:
    if "路线发现" not in text:
        return False
    header_count = sum(1 for header in ROUTE_TABLE_HEADERS if header in text)
    row_count = sum(1 for row in ROUTE_REQUIRED_ROWS if row in text)
    return header_count >= 6 and row_count >= 3


def is_pcb_topic(text: str) -> bool:
    return any(pattern in text for pattern in PCB_TOPIC_PATTERNS)


def has_numeric_claims(text: str) -> bool:
    return bool(re.search(r"\d+(?:\.\d+)?\s*(?:%|倍|年|个月|亿|万|层|微米|GT/s|Gbps|GB|mm|毫米|人民币)", text, re.IGNORECASE))


def check_route_table(text: str) -> list[Finding]:
    if has_route_table(text):
        return [Finding("PASS", "已发现路线发现表，且包含路线、机制、阶段、卡点、价值量和反证字段。")]
    return [
        Finding(
            "FAIL",
            "未发现合格路线发现表；成稿前必须补旧路线升级、新路线、替代/竞争路线、工作机制、当前阶段、最大卡点、价值量流向和反证条件。",
        )
    ]


def check_correction_density(script: str) -> list[Finding]:
    findings: list[Finding] = []
    total_len = chinese_len(script)
    if total_len == 0:
        return [Finding("FAIL", "未识别到中文口播正文，无法检查纠偏句密度。")]

    total_corrections = count_corrections(script)
    if total_len <= 300:
        windows = [(1, total_len, total_corrections)]
    else:
        chars = re.findall(r"[\u4e00-\u9fff]|[^\u4e00-\u9fff]", script)
        windows = []
        start = 0
        chinese_seen = 0
        while start < len(chars):
            end = start
            window_chinese = 0
            while end < len(chars) and window_chinese < 300:
                if re.match(r"[\u4e00-\u9fff]", chars[end]):
                    window_chinese += 1
                end += 1
            segment = "".join(chars[start:end])
            windows.append((chinese_seen + 1, chinese_seen + window_chinese, count_corrections(segment)))
            chinese_seen += window_chinese
            if end >= len(chars):
                break
            start = end

    bad_windows = [window for window in windows if window[2] > 3]
    if bad_windows:
        preview = "；".join(f"{start}-{end}字：{count}次" for start, end, count in bad_windows[:5])
        findings.append(Finding("FAIL", f"纠偏句密度过高，每 300 字上限 3 次；超限窗口：{preview}。"))
    else:
        findings.append(Finding("PASS", "纠偏句密度通过：每 300 字未超过 3 次。"))

    findings.append(Finding("INFO", f"口播正文约 {total_len} 个中文字符，纠偏/反问触发词共 {total_corrections} 次。"))
    return findings


def check_high_risk_phrases(text: str) -> list[Finding]:
    ignored_context = ("不能写", "禁止", "删除", "高风险", "规避", "不能学习", "不得写", "没有")
    scan_lines = [line for line in text.splitlines() if not any(marker in line for marker in ignored_context)]
    scan_text = "\n".join(scan_lines)
    hits = [phrase for phrase in HIGH_RISK_PHRASES if phrase in scan_text]
    if not hits:
        return [Finding("PASS", "未发现高风险财经表达。")]
    return [Finding("FAIL", f"发现高风险财经表达：{', '.join(hits)}。必须删除或改成产业验证口径。")]


def check_numeric_sources(text: str) -> list[Finding]:
    if not has_numeric_claims(text):
        return [Finding("INFO", "未发现明显数字断言。")]
    if any(marker in text for marker in SOURCE_MARKERS):
        return [Finding("PASS", "发现数字断言，同时存在来源/核验标记；仍需人工确认每个数字都有对应来源。")]
    return [
        Finding(
            "FAIL",
            "发现增长率、金额、交期、层数、线宽线距或速率等数字断言，但未发现来源/核验标记；数字必须标注来源等级或降级为待核验口径。",
        )
    ]


def check_pcb_depth(text: str) -> list[Finding]:
    if not is_pcb_topic(text):
        return [Finding("INFO", "未识别为 PCB/CCL 专项题材，跳过 PCB 颗粒度硬检查。")]

    findings: list[Finding] = []
    missing: list[str] = []
    for group_name, keywords in PCB_REQUIRED_GROUPS.items():
        if not any(keyword in text for keyword in keywords):
            missing.append(group_name)

    if missing:
        findings.append(
            Finding(
                "FAIL",
                "PCB/CCL 稿缺少专项颗粒度：" + "、".join(missing) + "。必须补材料等级、工艺路线、设备交期/投资、良率/客户认证和反证指标。",
            )
        )
    else:
        findings.append(Finding("PASS", "PCB/CCL 专项颗粒度通过：已覆盖材料、工艺、设备、良率/认证和反证指标。"))

    if "PCB都" in text or "所有 PCB" in text or "PCB 都" in text:
        findings.append(Finding("FAIL", "PCB 稿出现泛化表述，必须区分普通板、高速板、高多层板和 AI 服务器板。"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 changyelian 成稿是否通过路线发现和纠偏句密度硬门槛。")
    parser.add_argument("file", help="要检查的 markdown 或 txt 文件")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 2

    text = read_text(path)
    script = extract_video_script(text)
    findings = (
        check_route_table(text)
        + check_correction_density(script)
        + check_high_risk_phrases(text)
        + check_numeric_sources(text)
        + check_pcb_depth(text)
    )

    failed = False
    for finding in findings:
        print(f"[{finding.level}] {finding.message}")
        if finding.level == "FAIL":
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
