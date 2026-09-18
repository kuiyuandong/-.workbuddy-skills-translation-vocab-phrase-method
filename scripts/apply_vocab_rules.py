#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_vocab_rules.py — 中英互译发布包「核心词汇」机械规则校验/修正工具
（translation-vocab-phrase-method skill 配套脚本）

功能（默认报告模式，不改文件）：
  1. 解析发布包 .md 的「核心词汇」表（3列：英文|音标|中文释义）。
  2. 标出命中 exclude_basic.txt 的基础功能词行（建议移除）。
  3. 标出命中 transliteration_exclude.txt 的中文音译专名行（提示人工移除）。
  4. 校验标题计数 （N） == 表内实际行数。
  5. 从 原文/参考译文 抽取「学术词(add_words.json) + >15字母词」候选，列出缺失项供补词。

--apply 模式：自动重写 .md 的 核心词汇 表（移除基础词、重排、重算计数），
             并自动备份为 .bak。HTML 需另行人工处理（脚本只动 .md）。

用法：
  python apply_vocab_rules.py <file_or_dir> [--apply]
"""
import os, re, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "references")
ADD_PATH = os.path.join(REF, "add_words.json")
EXC_PATH = os.path.join(REF, "exclude_basic.txt")
TRANS_PATH = os.path.join(REF, "transliteration_exclude.txt")

# ---------- 加载参考 ----------
def load_json(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def load_list(p):
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                out.append(line.lower())
    except Exception:
        pass
    return out

ADD = load_json(ADD_PATH, {})
ADD.pop("_meta", None)
EXCLUDE = set(load_list(EXC_PATH))
TRANS = set(load_list(TRANS_PATH))
ADD_WORDS = set(w.lower() for w in ADD.keys())

# ---------- 解析 ----------
def find_section(text, marker):
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if marker in ln and ln.lstrip().startswith("#"):
            start = i + 1
            break
    if start is None:
        return []
    out = []
    for ln in lines[start:]:
        if ln.lstrip().startswith("#"):
            break
        out.append(ln)
    return out

def get_corevocab_region(text):
    """返回核心词汇表在 lines 中的 (hdr_index, 表起始行, 表结束行)。表结束=最后一个 | 行。"""
    lines = text.splitlines()
    hdr = None
    for i, ln in enumerate(lines):
        if "核心词汇" in ln and ln.lstrip().startswith("#"):
            hdr = i
            break
    if hdr is None:
        return None
    s = e = None
    for j in range(hdr + 1, len(lines)):
        if lines[j].lstrip().startswith("|"):
            if s is None:
                s = j
            e = j
        elif s is not None:
            break
    if s is None:
        return (hdr, None, None)
    return (hdr, s, e)

def parse_rows(table_lines):
    rows = []
    for ln in table_lines:
        if re.match(r'^\s*\|[\s\-:|]+\|\s*$', ln):
            continue
        m = re.match(r'\|\s*([^|]+?)\s*\|', ln)
        if not m:
            continue
        word = m.group(1).strip()
        if word.lower() in ("英文", "word"):
            continue
        rows.append((word, ln))
    return rows

def get_title_count(text):
    m = re.search(r'（\s*(\d+)\s*）', text)
    return int(m.group(1)) if m else None

def extract_source_en(text):
    ori = "\n".join(find_section(text, "原文"))
    ref = "\n".join(find_section(text, "参考译文"))
    def is_english(s):
        return len(re.sub(r'[^A-Za-z]', '', s)) > 20
    return ori if is_english(ori) else ref

def candidate_missing(source_en, present_words):
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", source_en or "")
    words = [w.lower().strip("-'") for w in words if len(w) >= 4]
    missing = []
    seen = set()
    for w in words:
        if w in seen or w in present_words:
            continue
        seen.add(w)
        if w in ADD_WORDS or len(w) > 15:
            missing.append(w)
    return sorted(set(missing))

# ---------- 主流程 ----------
def process_file(path, apply=False):
    text = open(path, encoding="utf-8").read()
    region = get_corevocab_region(text)
    report = {"file": os.path.basename(path)}
    if region is None:
        report["corevocab"] = "无核心词汇表"
        return report

    lines = text.splitlines()
    hdr, s, e = region
    if s is None:
        report["corevocab"] = "核心词汇标题存在但无表格"
        return report

    table_lines = lines[s:e+1]
    rows = parse_rows(table_lines)
    present_words = set(w.lower() for w, _ in rows)
    title_n = get_title_count(text)
    cur_n = len(rows)

    removed = [w for w, _ in rows if w.lower() in EXCLUDE]
    flagged = [w for w, _ in rows if w.lower() in TRANS]
    src = extract_source_en(text)
    missing = candidate_missing(src, present_words)

    report["title_count"] = title_n
    report["table_rows"] = cur_n
    report["count_ok"] = (title_n == cur_n) if title_n is not None else "N/A"
    report["removed_basic"] = removed
    report["flagged_transliteration"] = flagged
    report["suggest_add"] = [f"{w} ({ADD.get(w,{}).get('ipa','?')} {ADD.get(w,{}).get('zh','')})" for w in missing]

    if apply:
        new_rows = [ln for w, ln in rows if w.lower() not in EXCLUDE]
        new_n = len(new_rows)
        # 重算标题计数（只改第一处）
        for i, ln in enumerate(lines):
            if re.search(r'（\s*\d+\s*）', ln):
                lines[i] = re.sub(r'（\s*\d+\s*）', f'（{new_n}）', ln, count=1)
                break
        # 仅重建核心词汇表区域 [s, e]，其余行原样保留（避免误伤「重点词组」等后续表格）
        header_row = table_lines[0]                       # | 英文 | 音标 | 中文释义 |
        sep_row = None
        for tl in table_lines[1:]:
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', tl):
                sep_row = tl
                break
        new_table = [header_row]
        if sep_row:
            new_table.append(sep_row)
        new_table += new_rows
        final = "\n".join(lines[:s] + new_table + lines[e+1:])
        bak = path + ".bak"
        open(bak, "w", encoding="utf-8").write(text)
        open(path, "w", encoding="utf-8").write(final)
        report["applied"] = True
        report["backup"] = os.path.basename(bak)
        report["new_count"] = new_n
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="发布包 .md 文件或目录")
    ap.add_argument("--apply", action="store_true", help="真正重写 .md（自动 .bak）")
    args = ap.parse_args()

    if os.path.isdir(args.target):
        files = [os.path.join(args.target, f) for f in sorted(os.listdir(args.target))
                 if f.endswith("_公众号发布包.md")]
    else:
        files = [args.target]

    for fp in files:
        try:
            r = process_file(fp, args.apply)
        except Exception as ex:
            r = {"file": os.path.basename(fp), "error": str(ex)}
        print("=" * 60)
        print(f"FILE: {r.get('file')}")
        for k, v in r.items():
            if k == "file":
                continue
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
