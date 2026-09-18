#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_wrong_words.py — 将「本人 CET-6 错词表」从自动化数据源同步进本 skill 的 references/wrong_words.json。

数据源（默认）：C:\\Users\\Administrator\\WorkBuddy\\2026-06-30-22-34-53
  - cet6-vocab-trainer\\cet6_wrong_words.json  （结构化：word / meaning / error_count / mastered）
  - cet6-wrong-words-list.md                  （含 美/英 音标、词性、释义、例句）

产出：references/wrong_words.json
  { word: { meaning, uk_ipa, us_ipa, pos, error_count, mastered } }

可复跑（幂等）。换数据源用 --source 指定根目录。
"""
import os, re, json, argparse

DEFAULT_SOURCE = r"C:\Users\Administrator\WorkBuddy\2026-06-30-22-34-53"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "references", "wrong_words.json")


def load_json(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def parse_md(path):
    """返回 {word: {uk_ipa, us_ipa, pos, meaning}}"""
    out = {}
    if not os.path.exists(path):
        return out
    txt = open(path, encoding="utf-8").read()
    for blk in re.split(r'\n###\s', txt):
        m = re.match(r'\s*(\d+)\.\s*□\s*([A-Za-z\'\-]+)\s*(?:\[([^\]]+)\])?', blk)
        if not m:
            continue
        word = m.group(2).lower()
        pos = m.group(3) or ""
        ipa_m = re.search(r'音标：美\s*(/[^/]+/)\s*英\s*(/[^/]+/)', blk)
        us_ipa = ipa_m.group(1) if ipa_m else ""
        uk_ipa = ipa_m.group(2) if ipa_m else ""
        mean_m = re.search(r'释义：([^\n]+)', blk)
        meaning = mean_m.group(1).strip() if mean_m else ""
        out[word] = {"uk_ipa": uk_ipa, "us_ipa": us_ipa, "pos": pos, "meaning": meaning}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE,
                    help="数据源根目录（含 cet6-vocab-trainer 与 cet6-wrong-words-list.md）")
    args = ap.parse_args()

    json_p = os.path.join(args.source, "cet6-vocab-trainer", "cet6_wrong_words.json")
    md_p = os.path.join(args.source, "cet6-wrong-words-list.md")
    data = load_json(json_p, {})
    md = parse_md(md_p)
    if not data:
        print(f"ERROR: 未在 {json_p} 读取到错词数据")
        return

    out = {}
    missing_ipa = []
    for w, e in data.items():
        w = w.lower()
        m = md.get(w, {})
        uk = m.get("uk_ipa", "")
        us = m.get("us_ipa", "")
        pos = m.get("pos", "")
        meaning = e.get("meaning") or m.get("meaning", "")
        if not uk and not us:
            missing_ipa.append(w)
        out[w] = {
            "meaning": meaning,
            "uk_ipa": uk,
            "us_ipa": us,
            "pos": pos,
            "error_count": e.get("error_count", 0),
            "mastered": e.get("mastered", False),
        }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"同步完成：{len(out)} 个错词 -> {OUT}")
    mastered = sum(1 for v in out.values() if v["mastered"])
    with_ipa = sum(1 for v in out.values() if v["uk_ipa"] or v["us_ipa"])
    print(f"  已掌握(mastered): {mastered} | 有音标: {with_ipa} | 无音标: {len(missing_ipa)}")
    if missing_ipa:
        print(f"  无音标词（前20）: {missing_ipa[:20]}")


if __name__ == "__main__":
    main()
