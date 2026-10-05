#!/usr/bin/env python3
"""journal —— 极简日记 CLI。

条目就是 Markdown 文件：~/.journal/YYYY-MM-DD.md（--dir 可覆盖）。
纯本地、纯标准库。
"""

import argparse
import os
import re
import sys
from datetime import datetime, date

VERSION = "0.1.0"
DEFAULT_DIR = os.path.expanduser("~/.journal")
ENTRY_RE = re.compile(r"^## (\d{2}):(\d{2})\s*$", re.M)


def journal_dir(args) -> str:
    d = args.dir or os.environ.get("JOURNAL_DIR") or DEFAULT_DIR
    return os.path.expanduser(d)


def day_file(jdir: str, day: date) -> str:
    return os.path.join(jdir, day.strftime("%Y-%m-%d.md"))


def ensure_header(path: str, day: date):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {day.strftime('%Y-%m-%d')}（{weekday_cn(day)}）\n\n")


def weekday_cn(d: date) -> str:
    return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]


def cmd_add(args) -> int:
    jdir = journal_dir(args)
    day = args.date and date.fromisoformat(args.date) or date.today()
    if args.text:
        text = args.text
    elif args.stdin:
        text = sys.stdin.read().strip()
    else:
        # 没有参数：从 stdin 读，提示用户（管道/EOF 时干净报错）
        if sys.stdin.isatty():
            print("输入日记内容（Ctrl-D 结束）：", file=sys.stderr)
        text = sys.stdin.read().strip()
    if not text:
        print("error: 内容为空，未写入。", file=sys.stderr)
        return 1
    path = day_file(jdir, day)
    ensure_header(path, day)
    now = datetime.now().strftime("%H:%M")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"## {now}\n\n{text}\n\n")
    print(f"已记入 {os.path.basename(path)}（{now}）")
    return 0


def show_day(path: str):
    with open(path, encoding="utf-8") as f:
        sys.stdout.write(f.read())


def cmd_today(args) -> int:
    path = day_file(journal_dir(args), date.today())
    if not os.path.exists(path):
        print("今天还没有日记。用 `journal add \"...\"` 写第一条。")
        return 0
    show_day(path)
    return 0


def cmd_show(args) -> int:
    try:
        day = date.fromisoformat(args.day)
    except ValueError:
        print(f"error: 日期格式错误：{args.day}（应为 YYYY-MM-DD）", file=sys.stderr)
        return 1
    path = day_file(journal_dir(args), day)
    if not os.path.exists(path):
        print(f"{args.day} 没有日记。")
        return 0
    show_day(path)
    return 0


def count_entries(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        return len(ENTRY_RE.findall(f.read()))


def cmd_list(args) -> int:
    jdir = journal_dir(args)
    if not os.path.isdir(jdir):
        print("还没有任何日记。")
        return 0
    files = sorted(f for f in os.listdir(jdir) if f.endswith(".md"))
    if not files:
        print("还没有任何日记。")
        return 0
    total = 0
    for f in files:
        n = count_entries(os.path.join(jdir, f))
        total += n
        print(f"  {f[:-3]}  {n} 条")
    print(f"共 {len(files)} 天，{total} 条。")
    return 0


def cmd_search(args) -> int:
    jdir = journal_dir(args)
    kw = args.keyword
    if not os.path.isdir(jdir):
        print("还没有任何日记。")
        return 1
    hits = 0
    for f in sorted(os.listdir(jdir)):
        if not f.endswith(".md"):
            continue
        path = os.path.join(jdir, f)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        for i, line in enumerate(lines):
            if kw in line:
                hits += 1
                print(f"{f}:{i + 1}: {line}")
    if not hits:
        print(f"没有找到「{kw}」。")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="journal", description="极简日记：每天一个 Markdown 文件。")
    p.add_argument("--version", action="version", version=f"journal {VERSION}")
    p.add_argument("--dir", default=None, help="日记目录（默认 ~/.journal，可用 JOURNAL_DIR 环境变量覆盖）")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="写一条日记")
    a.add_argument("text", nargs="?", help="日记内容（省略则从 stdin 读取）")
    a.add_argument("--stdin", action="store_true", help="强制从 stdin 读取")
    a.add_argument("--date", default=None, help="指定日期 YYYY-MM-DD（默认今天）")
    a.set_defaults(func=cmd_add)

    t = sub.add_parser("today", help="查看今天的日记")
    t.set_defaults(func=cmd_today)

    s = sub.add_parser("show", help="查看某天的日记")
    s.add_argument("day", help="日期 YYYY-MM-DD")
    s.set_defaults(func=cmd_show)

    l = sub.add_parser("list", help="列出所有日记日期与条数")
    l.set_defaults(func=cmd_list)

    q = sub.add_parser("search", help="全文搜索")
    q.add_argument("keyword", help="关键词")
    q.set_defaults(func=cmd_search)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
