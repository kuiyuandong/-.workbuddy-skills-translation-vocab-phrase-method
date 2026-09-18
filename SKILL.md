---
title: "中英互译·核心词汇与重点词组提取方法论"
summary: "从英译汉/汉译英双语素材中提取「核心词汇（单词级）」与「重点词组（词组级固定搭配/长专名）」的可复用方法论。适用于翻译每日一练、口译备考、双语白皮书/导游词等任何中英互译内容生产。"
read_when:
  - 用户要求从双语材料提取或审核「核心词汇」「重点词组」
  - 制作翻译每日一练 / 口译备考 / 双语阅读类公众号或练习包
  - 修订已有发布包的核心词汇表与重点词组（删简单词、补学术词、排音译专名）
  - 需要判断「哪些词进核心词汇、哪些短语进重点词组」
agent_created: true
---

# 定位

本 skill 是一套**方法论 + 工具**，解决中英互译内容生产里两个最常踩坑的环节：
**核心词汇表怎么选词、重点词组怎么挑短语**。它从「辽宁文旅厅白皮书双语翻译每日一练」系列沉淀而来，但规则本身**与具体素材解耦**，可复用到任何英译汉/汉译英场景（导游口试、白皮书、双语阅读、考试刷题等）。

> 配套 skill：`daily-english-wechat-article`（排版骨架 A/B）。本 skill 只管「选词 + 选词组」这一子问题，不直接产出发布包 HTML。

# 铁律：两表不重复

| 表 | 粒度 | 装什么 | 绝不装什么 |
|----|------|--------|-----------|
| **核心词汇** | 单词级 | 学术/学科词、超长词（>15 字母） | 词组、整块专名、音译地名、基础功能词 |
| **重点词组** | 词组级 | 中英不一一对应的固定搭配、长专名整块 | 单词、可逐词直译的普通短语 |

同一篇里，petrochemical 进**核心词汇**；"Shenyang Economic Zone" 进**重点词组**；两者不打架。

# 一、核心词汇规则

## 1.1 格式（3 列，无例句列）
```
| 英文 | 音标 | 中文释义 |
```
口译对照型素材**不加例句列**（源无例句，勿编造）。若某场景需要例句，那是另一个模板，不在本规则内。

## 1.2 四关准入（AND 关系，全过才保留 · 2026-09-18 定稿）
| 关 | 名称 | 判定 |
|----|------|------|
| **G1** | 非基础词 | 不在基础词停表内（见 1.3） |
| **G2** | 有口译价值 | 命中价值信号词（行业术语 / 口译正式表达 / 文旅场景词）**或** 长度 ≥ 6 字母（约 B1+） |
| **G3** | 释义具体 | 中文释义义项 < 3 个（"首都；省会；都城"才判泛义） |
| **G4** | 去冗 | 不与该篇 **≤3 词**难点词组的成分重复（长专名不参与去冗，防误杀核心词汇） |

**必须加入（满足任一即视为有口译价值，叠加执行）**
1. **学术 / 学科类词**：archaeological / civilization / society / eco-friendly / cultural / economic / historical / environment / ecological / petrochemical / geopark / agricultural / ecosystem / business-friendly / logistics / metropolis / fourth-generation / technological / technologies / artistic / physical / biological / environmental / popularization / social / botanical / horticultural / horticulture 等（权威清单见 `references/add_words.json`，可扩充）。
2. **超过 15 字母的词**（含连字符复合词，长度数连字符，如 business-friendly / fourth-generation）。

**数量规则**：目标 8–10 个 → 不足 8 按实际输出 → **不足 6 自动加「待人工补录」标记，绝不编造补位**。

**运行时唯一事实源**：`…\每日一练素材\vocab_phrase_rules.py`（本 skill 与它保持一致；改规则改代码那处）。

> **前提**：仅在「该词确实出现在本篇英文原文」时加入，**不编造**。缺失词查 Cambridge UK 音标（去点，与表内风格统一），中文取权威译法。

## 1.3 必须剔除（基础词停表，四关中的 G1）
判断标准：**人人都认识、不体现原文专业信息**。典型如 river / city / area / province / spring / beach / national / famous / history。

停表规模（2026-09-18 定稿）：**265 词**，分 8 组——自然地理泛词（水体/地貌/天象）、基础形容与方位、颜色、季节时间、常见动植物、人文聚落通用名词、高频抽象功能泛词、常见动词泛词。

**两处加载，任一处增补均生效**：
- `references/exclude_basic.txt`（本 skill，参考副本，已含全表）
- `…\每日一练素材\stop_words_user.txt`（**日常追加通道**，金玉维护，一行一词，支持 `#` 注释与多词短语）

> **金玉的约定（2026-09-18）**：日后发现 AI 把某个简单词列进了核心词汇，金玉提示、AI 追加进停表；**自然地理泛词组当前偏少，需持续扩充**。追加不改代码，写完即生效。
> 一行命令追加：`python add_stop.py "castle, tower"`（追加后自动报告影响面）。
> 注意：停表扩张会让更多篇目核心词汇跌破 6 个 → 需配套「按语境重写释义 + 人工补录」把有价值词补回来。

## 1.4 排除（红线：非可学词汇 + 加注需编造音标）
**中文音译专名一律不纳入核心词汇**，包括：
- 城市对：Qinhuangdao-Shenyang、Shenyang-Dalian
- 单地名音译：Qinhuangdao / Shenyang / Dalian / Chahai / Jinniushan
- 任何「音译自中文地名」的 hyphen 复合词

理由：音标需现编、无可学价值；必要专名留待**重点词组**整块处理。
（清单见 `references/transliteration_exclude.txt`，可按需扩充。）

## 1.5 音标权威来源（硬规矩）
- 一律查 **Cambridge UK / Merriam-Webster** 等权威词典，**去点统一风格**（如 `/ˌtek.nəˈlɒdʒ.ɪ.kəl/` → `/ˌteknəˈlɒdʒɪkəl/`）。
- **严禁从模型记忆生成音标**。
- 参考库：`D:\WorkBuddy\每日英语\ipa_tourism.json`（273 词，word→IPA）、`references/add_words.json`（学术/长词扩展包，含 IPA+中文）。

## 1.6 计数一致（易漏坑）
标题 `（N）` == 表内实际行数 == HTML 表内行数。三处必须一致，改词必同步。

# 二、重点词组规则

## 2.1 格式（青绿 callout，3 列）
```
| 中文词组 | 英文对应 | 记忆要点 |
```
- 难记的**固定译法**在「记忆要点」标 ⚠️。
- 位置：**朗读建议之后、喜马拉雅之前**（朗前喜后）。

## 2.2 六类判断（哪些中文词组值得提 · 2026-09-18 由五类扩为六类）
取「中英不一一对应、直译会错」的短语，分六类：
1. **经济/区划专有名词固定译法**：中文「区/带/圈」≠ 字面 zone/belt/rim，是固定搭配——经济区=**Zone**（Shenyang Economic Zone）、沿海经济带=**Belt**（Liaoning Coastal Economic Belt）、环渤海=**Rim**（Bohai Rim）；振兴=**revitalize**（非 revive/rejuvenate）；老工业基地=**old industrial base**（非 old industrial zone）。
2. **词序颠倒**：中文修饰语前置、英文常后置。例：振兴东北老工业基地 → revitalizing the old industrial base **in Northeast China**。
3. **复合词连字符**：城市合称用连字符（Shenyang-Dalian、Harbin-Dalian）；带连字符形容词（high-end、mid-range）。漏连字符是大坑。
4. **易混淆近义**：温泉=**hot spring**（地理温泉）≠ spa（疗养/水疗）；区 Zone ≠ 带 Belt ≠ 圈 Rim。
5. **经济地理专有名词**：经济区/带/圈/走廊/轴线等专名，含城市合称连字符与固定后缀（Rim/Belt/Zone）。
6. **机构与专有名录（新增，2026-09-18）**：国际组织/国家机关、公约名录、官方称号、评级体系等整块专名——United Nations List of Wetlands of International Importance（国际重要湿地名录）、World Heritage Site/List（世界遗产/名录）、national nature reserve（国家级自然保护区）、各类 **National … City/Site/Base**、**A-grade tourist attractions** 等。整块是固定叫法、不可逐词译，**归入疑难词组整块记忆**。
   > 自动抽取器 `extract_phrase_candidates(text)`（在 `vocab_phrase_rules.py`）可按信号提候选：机构/名录关键词、英文首字母大写链 ≥2 词、`of` 多层链 ≥2 层、中文「联合国 / 世界… / 国际… / 国家级…」模式、引号内固定称号。全窗口实测命中 322 条；**候选仅供人工核定，记忆要点不自动生成**。缩略词（WHO）须大小写敏感，否则误抓代词 who。

## 2.3 「记忆要点」写什么（每条 ⚠️ 维度）
- 字面直译陷阱（中文 X ≠ 英文直译 X）
- 动词/名词特定化（振兴≠revive）
- 词序/连字符/固定搭配（整块记）

## 2.4 提取流程
1. 扫原文挑「中英词序/用词不对应」短语
2. 查权威译法（对照参考译文、官方固定叫法如三大国家战略英文）
3. 标 ⚠️ 写难记点
4. 同篇成组（**3–4 行一组**，如 09-14 的 3 行、09-15 的 4 行）

## 2.5 边界
- 只取「原文确实出现 + 中文有对应翻译」的；源文件无此段时发布包**留空不补，不编造、不硬凑**。
- 与核心词汇表不重复（即核心词汇的 G4 去冗关；**只对 ≤3 词的短词组生效**——长专名成分词过多，参与去冗会把核心词汇误杀到 0 个，营口篇曾踩此坑）。
- **中文音译专名（Qinhuangdao 等）不进重点词组**（音标需编造、无可学价值）。

# 三、红线（用户强约束，跨场景生效）
- **事实零差错**：地名/厂名/数据不可错（"鞍钢"非"安钢"）。
- **内部运营信息绝不对读者呈现**（排期/替换窗口/自动化约定）。
- 不对外替金玉发声；外部操作（发邮件/发消息）先确认。

# 四、合规豁免（仅限辽宁文旅厅白皮书来源）
该系列素材取自**辽宁省文旅厅正式白皮书**（官方内容，非自由创作），**不涉及「喜马拉雅内容合规绕行规则」**——无需将国际组织类内容替换为旅行健康科普，也不受政治/军事/时政/宗教/股市/敏感财经等禁限约束。换其他来源的素材时，需重新评估合规。

# 五、工具脚本
`scripts/apply_vocab_rules.py` —— 对一个或多个发布包 `.md` 应用本 skill 的机械规则：
- 移除核心词汇表中 `exclude_basic.txt` 命中的基础词；
- 标出命中 `transliteration_exclude.txt` 的音译专名（提示人工移除）；
- 校验标题计数 `（N）` == 表内行数；
- 从原文/参考译文抽取「学术词 + >15 字母词」候选，列出缺失项供补词；
- 默认**只报告**；`--apply` 才重写 .md 表（自动备份 .bak），HTML 另行人工处理。

```bash
# 报告模式（安全，不改文件）
python scripts/apply_vocab_rules.py "D:\WorkBuddy\每日英语\发布包\2026-09-19_翻译每日一练_英译汉_第12题_公众号发布包.md"
# 批量目录
python scripts/apply_vocab_rules.py "D:\WorkBuddy\每日英语\发布包"
# 真正改写（先自动 .bak）
python scripts/apply_vocab_rules.py "D:\WorkBuddy\每日英语\发布包" --apply
```

# 六、参考文件
- `references/add_words.json`：学术/长词扩展包（28 词，含 Cambridge UK IPA + 中文），持续扩充。
- `references/exclude_basic.txt`：核心词汇必剔基础功能词清单。
- `references/transliteration_exclude.txt`：中文音译专名排除清单/规则。

# 七、TODO（待完善，逐步迭代）
- [x] 自动识别「长专名/机构名录类」抽取：已实现 `vocab_phrase_rules.extract_phrase_candidates()`（2026-09-18），全窗口命中 322 条候选，人工核定后入表。
- [ ] 停表持续扩充：**自然地理泛词组当前偏少**，金玉每次发现简单词即追加；追加通道 `stop_words_user.txt`（写完即生效）。
- [ ] 按语境重写释义：词典义泛（capital「首都；省会；都城」）但语境义具体（"湿地之都"）的词，需按语境改写释义才能过 G3——这类词在 60 篇里有若干，待批量处理。
- [ ] 核心词汇跌破 6 个的篇目补词：停表扩张后 29/60 篇不足 6 个（带「待人工补录」标记），需逐篇按语境补有价值词。
- [ ] 音标自动查词 API 接入（替代手工查 Cambridge），并去点归一化。
- [ ] `apply_vocab_rules.py` 增加 HTML 同步改写（目前只动 .md）。
- [ ] add_words.json 持续扩词（每次遇到新学术/学科词即补，并附 IPA 来源）。
- [ ] 已知遗留：已发布包 09-24/09-26/10-05 中 `technologies` 的音标写作 `/tekˈnɒlədʒi/`（单数 technology 的），正确应为 `/tekˈnɒlədʒiz/`；下次触碰这些包时一并修正（参考 `references/add_words.json` 已存正确值）。
