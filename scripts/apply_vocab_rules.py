#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_vocab_rules.py — 中英互译发布包「核心词汇」机械规则校验/修正工具
（translation-vocab-phrase-method skill 配套脚本）

规则源（references/）：
  - add_words.json            学术/学科类 + >15 字母词（强制纳入主表）
  - exclude_basic.txt         核心词汇必剔基础功能词
  - transliteration_exclude.txt  中文音译专名（红线排除）
  - wrong_words.json          本人 CET-6 错词表（强制通道，命中即单独成表）

功能（默认报告模式，不改文件）：
  1. 解析发布包 .md 的「核心词汇」主表（3列：英文|音标|中文释义）。
  2. 标出命中 exclude_basic.txt 的基础功能词行（建议移除）。
  3. 标出命中 transliteration_exclude.txt 的中文音译专名行（提示人工移除）。
  4. 校验标题计数 （N） == 表内实际行数。
  5. 从 原文/参考译文 抽取「学术词 + >15字母词」候选，列出缺失项供补词。
  6. 标出命中 错词表 的原文单词（强制通道候选，建议单独成表）。

--apply         移除核心词汇主表中 exclude_basic.txt 命中的基础词，重排并重算计数。
--apply-error   在核心词汇板块内追加「个人错词」子表（SKILL.md §1.2.1），命中词从主表剔除，
                重算主表计数；自动备份 .bak。HTML 需另行人工处理。

用法：
  python apply_vocab_rules.py <file_or_dir> [--apply] [--apply-error]
"""
import os, re, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "references")
ADD_PATH = os.path.join(REF, "add_words.json")
EXC_PATH = os.path.join(REF, "exclude_basic.txt")
TRANS_PATH = os.path.join(REF, "transliteration_exclude.txt")
WRONG_PATH = os.path.join(REF, "wrong_words.json")

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
WRONG = load_json(WRONG_PATH, {})
ADD_WORDS = set(w.lower() for w in ADD.keys())
WRONG_WORDS = set(w.lower() for w in WRONG.keys())

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

# ---------- 错词表匹配（后缀回退，保守） ----------
def match_error_word(token):
    """返回 token 命中的错词表规范词；未命中返回 None。"""
    if not WRONG_WORDS:
        return None
    t = token.lower().strip("'-")
    if not t:
        return None
    if t in WRONG:
        return t
    if t.endswith("'s"):
        b = t[:-2]
        if b in WRONG:
            return b
    if t.endswith("ies") and len(t) > 4:
        if t[:-3] + "y" in WRONG:
            return t[:-3] + "y"
    if t.endswith("ied") and len(t) > 4:
        if t[:-3] + "y" in WRONG:
            return t[:-3] + "y"
    if t.endswith("es"):
        if t[-3] in "sxzh" or t[-4:-2] in ("ch", "sh"):
            if t[:-2] in WRONG:
                return t[:-2]
    if t.endswith("ed") and len(t) > 3:
        if t[:-2] in WRONG:
            return t[:-2]
        if len(t[:-2]) >= 2 and t[-3] == t[-4] and t[-3] in "bcdfghjklmnpqrstvwyz":
            if t[:-3] in WRONG:
                return t[:-3]
    if t.endswith("ing") and len(t) > 4:
        if t[:-3] in WRONG:
            return t[:-3]
        if len(t[:-3]) >= 2 and t[-4] == t[-5] and t[-4] in "bcdfghjklmnpqrstvwyz":
            if t[:-4] in WRONG:
                return t[:-4]
    if t.endswith("s") and len(t) > 2:
        if t[:-1] in WRONG:
            return t[:-1]
    return None

def find_error_word_hits(text, present_words):
    """返回 {规范词: (原文形式, info)}，仅含命中错词表且不在主表 present_words 的词。"""
    hits = {}
    if not WRONG_WORDS:
        return hits
    src = extract_source_en(text)
    for tok in re.findall(r"[A-Za-z][A-Za-z'\-]*", src or ""):
        canonical = match_error_word(tok)
        if not canonical or canonical in present_words or canonical in hits:
            continue
        hits[canonical] = (tok, WRONG.get(canonical, {}))
    return hits

def extract_subtable_words(text):
    """返回已存在「个人错词」子表中的词集合（避免重复插入）。"""
    out = set()
    in_sub = False
    for ln in text.splitlines():
        if "个人错词" in ln and ln.lstrip().startswith("#"):
            in_sub = True
            continue
        if in_sub and ln.lstrip().startswith("#"):
            in_sub = False
            continue
        if in_sub:
            m = re.match(r'\|\s*([^|]+?)\s*\|', ln)
            if m:
                w = m.group(1).strip().lower()
                if w not in ("英文", "word"):
                    out.add(w)
    return out

# ---------- 主流程 ----------
def process_file(path, apply=False, apply_error=False):
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
    err_hits = find_error_word_hits(text, present_words)

    report["title_count"] = title_n
    report["table_rows"] = cur_n
    report["count_ok"] = (title_n == cur_n) if title_n is not None else "N/A"
    report["removed_basic"] = removed
    report["flagged_transliteration"] = flagged
    report["suggest_add"] = [f"{w} ({ADD.get(w,{}).get('ipa','?')} {ADD.get(w,{}).get('zh','')})" for w in missing]
    report["error_word_hits"] = sorted(err_hits.keys())

    # ---- 改写 ----
    do_write = False
    if apply or apply_error:
        # 1) 基础词剔除
        keep = [(w, ln) for w, ln in rows if w.lower() not in EXCLUDE]
        # 2) 错词子表
        sub_block = None
        if apply_error:
            # 错词命中以「原文是否出现」为准，全部纳入子表；已在主表的移出主表避免重复（§1.2.1）
            hits = find_error_word_hits(text, set())
            sub_present = extract_subtable_words(text)
            hits = {c: v for c, v in hits.items() if c not in sub_present}
            if hits:
                n = len(hits)
                rows_sub = []
                for c, (of, info) in hits.items():
                    ipa = info.get("uk_ipa") or info.get("us_ipa") or ""
                    pos = info.get("pos", "")
                    meaning = info.get("meaning", "")
                    ec = info.get("error_count", 0)
                    rows_sub.append(f"| {c} | {ipa} | {pos} | {meaning} | {of} | {ec} |")
                sub_block = ["",
                             "### 个人错词（CET-6 错词表命中 · 强制纳入，%d 个）" % n,
                             "| 英文 | 音标 | 词性 | 中文释义 | 原文形式 | 个人错次 |",
                             "|----|----|----|----|----|----|"] + rows_sub
                keep = [(w, ln) for w, ln in keep if w.lower() not in hits]
        new_n = len(keep)
        # 重算标题计数（第一处 （N））
        for i, ln in enumerate(lines):
            if re.search(r'（\s*\d+\s*）', ln):
                lines[i] = re.sub(r'（\s*\d+\s*）', f'（{new_n}）', ln, count=1)
                break
        header_row = table_lines[0]
        sep_row = None
        for tl in table_lines[1:]:
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', tl):
                sep_row = tl
                break
        new_table = [header_row]
        if sep_row:
            new_table.append(sep_row)
        new_table += [ln for _, ln in keep]
        if sub_block:
            final = "\n".join(lines[:s] + new_table + sub_block + lines[e+1:])
        else:
            final = "\n".join(lines[:s] + new_table + lines[e+1:])
        do_write = apply or (apply_error and sub_block is not None)
        if do_write:
            bak = path + ".bak"
            open(bak, "w", encoding="utf-8").write(text)
            open(path, "w", encoding="utf-8").write(final)
            report["applied"] = True
            report["backup"] = os.path.basename(bak)
            report["new_count"] = new_n
            if sub_block:
                report["error_subtable_added"] = len(hits)
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="发布包 .md 文件或目录")
    ap.add_argument("--apply", action="store_true", help="真正重写 .md：移除基础词（自动 .bak）")
    ap.add_argument("--apply-error", action="store_true", help="追加「个人错词」子表（§1.2.1，自动 .bak）")
    args = ap.parse_args()

    if os.path.isdir(args.target):
        files = [os.path.join(args.target, f) for f in sorted(os.listdir(args.target))
                 if f.endswith("_公众号发布包.md")]
    else:
        files = [args.target]

    for fp in files:
        try:
            r = process_file(fp, args.apply, args.apply_error)
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
