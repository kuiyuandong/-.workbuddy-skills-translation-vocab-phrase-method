#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_vocab_rules_html.py — 中英互译发布包「核心词汇」个人错词子表的 HTML 镜像修正
（translation-vocab-phrase-method skill 配套脚本，与 apply_vocab_rules.py 的 --apply-error 对齐）

逻辑（与 md --apply-error 完全对应）：
  1. 复用 apply_vocab_rules 的 find_error_word_hits + wrong_words.json，得到 {规范词:(原文形式,info)}。
  2. 若 html 已含「个人错词」子表 -> 跳过（幂等）。
  3. 解析 html 核心词汇主表，若命中词在主表 -> 移除该行并递减计数（🔤 核心词汇（N））。
  4. 在「核心词汇」</section> 之后、「朗读建议」之前插入「个人错词」子表（6 列：英文|音标|词性|中文释义|原文形式|个人错次）。
  5. 自动备份 .bak；无命中或无改动则为 no-op。

用法：
  python apply_vocab_rules_html.py <file_or_dir>
"""
import os, re, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_vocab_rules as A   # 复用 WRONG / find_error_word_hits / extract_source_en

TD = 'style="border:1px solid #dddddd;padding:8px 10px;"'

def html_core_rows(html):
    """返回 (核心词汇计数, 主表 <tr> 行列表, 表起始位置信息)。"""
    m = re.search(r'🔤\s*核心词汇（(\d+)）', html)
    count = int(m.group(1)) if m else None
    # 找核心词汇 section 的 <tbody>
    hidx = html.find('🔤 核心词汇（')
    tbody_s = html.find('<tbody>', hidx)
    tbody_e = html.find('</tbody>', hidx)
    seg = html[tbody_s+len('<tbody>'):tbody_e]
    rows = re.findall(r'<tr[^>]*>.*?</tr>', seg, re.S)
    return count, rows, hidx, tbody_s, tbody_e

def row_word(row_html):
    m = re.search(r'<td[^>]*>(.*?)</td>', row_html, re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def build_sub_section(hits):
    n = len(hits)
    rows_html = []
    for c, (of, info) in hits.items():
        ipa = info.get('uk_ipa') or info.get('us_ipa') or ''
        pos = info.get('pos', '')
        meaning = info.get('meaning', '')
        ec = info.get('error_count', 0)
        rows_html.append(
            f'<tr><td {TD}>{c}</td><td {TD}>{ipa}</td><td {TD}>{pos}</td>'
            f'<td {TD}>{meaning}</td><td {TD}>{of}</td><td {TD}>{ec}</td></tr>')
    return (
        '\n<section style="margin:0 0 24px 0;">\n'
        f'  <p style="margin:0 0 10px 0;font-size:16px;font-weight:800;color:#1a1a2e;">'
        f'🔤 个人错词（CET-6 错词表命中 · 强制纳入，{n} 个）</p>\n'
        '  <table style="width:100%;border-collapse:collapse;font-size:13px;line-height:1.6;color:#2d3436;">\n'
        '    <thead>\n'
        '      <tr style="background-color:#1a1a2e;color:#ffffff;">\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">英文</th>\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">音标</th>\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">词性</th>\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">中文释义</th>\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">原文形式</th>\n'
        f'        <th style="border:1px solid #dddddd;padding:8px 10px;text-align:left;"">个人错次</th>\n'
        '      </tr>\n'
        '    </thead>\n'
        '    <tbody>\n'
        + '\n'.join('      ' + r for r in rows_html) + '\n'
        '    </tbody>\n'
        '  </table>\n'
        '</section>'
    )

def process_html(md_path, html_path):
    md_text = open(md_path, encoding='utf-8').read()
    # 主表现有词（用于判断命中词是否已在主表 -> 需移除）
    region = A.get_corevocab_region(md_text)
    present_main = set()
    if region and region[1] is not None:
        rows = A.parse_rows(md_text.splitlines()[region[1]:region[2]+1])
        present_main = set(w.lower() for w, _ in rows)
    # 全部命中（含已主表），与 md --apply-error 一致
    hits = A.find_error_word_hits(md_text, set())
    if not hits:
        return {"file": os.path.basename(html_path), "changed": False, "reason": "no hits"}

    html = open(html_path, encoding='utf-8').read()
    if '🔤 个人错词' in html:
        return {"file": os.path.basename(html_path), "changed": False, "reason": "already has sub-table"}

    count, rows, hidx, tbody_s, tbody_e = html_core_rows(html)
    hit_lc = set(h.lower() for h in hits.keys())
    kept = [r for r in rows if row_word(r).lower() not in hit_lc]
    removed = len(rows) - len(kept)
    new_count = (count - removed) if count is not None else count

    # 重写 <tbody> 内容
    new_tbody = '<tbody>' + ''.join(kept) + '</tbody>'
    html2 = html[:tbody_s] + new_tbody + html[tbody_e:]
    # 更新计数
    if new_count is not None and removed:
        html2 = re.sub(r'(🔤\s*核心词汇)（\d+）', rf'\1（{new_count}）', html2, count=1)

    # 插入子表：核心词汇 </section> 之后
    cidx = html2.find('🔤 核心词汇（')
    close_idx = html2.find('</section>', cidx)
    insert_at = close_idx + len('</section>')
    sub_html = build_sub_section(hits)
    html3 = html2[:insert_at] + sub_html + html2[insert_at:]

    if html3 == html:
        return {"file": os.path.basename(html_path), "changed": False, "reason": "no diff"}

    bak = html_path + '.bak'
    open(bak, 'w', encoding='utf-8').write(html)
    open(html_path, 'w', encoding='utf-8').write(html3)
    return {"file": os.path.basename(html_path), "changed": True,
            "removed_from_main": removed, "new_count": new_count,
            "sub_rows": len(hits), "backup": os.path.basename(bak)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="发布包 .md 或目录（对应 .html 同目录同名）")
    args = ap.parse_args()
    if os.path.isdir(args.target):
        files = sorted(f for f in os.listdir(args.target) if f.endswith("_公众号发布包.md"))
        base = args.target
    else:
        files = [os.path.basename(args.target)]
        base = os.path.dirname(os.path.abspath(args.target))
    for f in files:
        stem = f[:-len("_公众号发布包.md")]
        md_p = os.path.join(base, f)
        html_p = os.path.join(base, stem + "_公众号发布包.html")
        if not os.path.exists(html_p):
            print("SKIP (no html):", f); continue
        try:
            r = process_html(md_p, html_p)
        except Exception as ex:
            r = {"file": f, "error": str(ex)}
        print("=" * 60)
        print("FILE:", r.get("file"))
        for k, v in r.items():
            if k == "file": continue
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
