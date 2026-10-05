# journal

极简日记 CLI：每天一个 Markdown 文件，纯本地、纯标准库、零依赖。

## 安装

```bash
cd journal
python3 -m journal --help
```

## 用法

```bash
journal add "今天学会了用 journal 写日记。"   # 写一条（带时间戳）
echo "管道输入" | journal add --stdin          # 从管道读
journal add --date 2026-10-01 "补写昨天的"     # 指定日期

journal today        # 看今天
journal show 2026-10-01
journal list         # 所有日期 + 条数
journal search "关键词"   # 全文搜索（带文件名:行号）
```

数据目录默认 `~/.journal`，`--dir` 或 `JOURNAL_DIR` 环境变量可覆盖。
无参数的 `add` 在终端里会提示输入、Ctrl-D 结束；管道/EOF 时直接读取。

文件格式示例（`~/.journal/2026-10-05.md`）：

```markdown
# 2026-10-05（周一）

## 09:30

今天学会了用 journal 写日记。

## 22:15

第二条。
```

## 诚实说明

- 条目是**明文 Markdown**，无加密——别写密码进去；要加密请用系统级方案（如加密磁盘）。
- `add` 只追加不修改，改错字请直接编辑文件。
- 时间戳按本机本地时间。
