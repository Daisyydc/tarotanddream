# 塔罗 / 解梦数据整理包

整理时间：2026-04-02

## 1. 这次我帮你整理了什么

这个数据包围绕你发来的 8 个链接，按 **“可直接做知识库 / 可做训练数据 / 可做业务逻辑参考 / 需要你本地补下载”** 四类整理。

### 已实际下载并放进包里的内容
1. **周公解梦 dream-decoder 数据**
   - 清洗后文件：
     - `cleaned/dream_decoder_data_clean.csv`
     - `cleaned/dream_decoder_data_clean.jsonl`
   - 记录数：**33,830**
   - 字段：`dream`, `decode`

2. **Hugging Face 三张牌 tarot readings 数据**
   - 清洗后文件：
     - `cleaned/Dendory_tarot_readings_clean.csv`
   - 记录数：**5,769**
   - 字段：`Card 1`, `Card 2`, `Card 3`, `Reading`

3. **AI-Diviner-Web 的塔罗静态配置**
   - 原始文件：
     - `raw/AI_Diviner_Tarot.ts`
   - 用途：
     - 牌名中英映射
     - 牌阵名称
     - 各牌阵抽牌数量

4. **tarot-reader 业务脚本**
   - 原始文件：
     - `raw/tarot_reader.py`
   - 用途：
     - 参考抽牌逻辑、数据结构、解读流程

5. **牌间关系理论文档**
   - 原始文件：
     - `raw/card-relations.md`
   - 用途：
     - 作为高质量规则型知识库，增强“多牌组合解释”

6. **说明类文件**
   - `raw/Dendory_tarot_README.md`
   - `raw/AbsoluteWinter_tarot_database_README.md`

### 没有自动完整下载的内容
1. **Kaggle: Complete Tarot Card Meanings - All 78 Cards**
   - 原因：Kaggle 通常需要登录/授权后下载
   - 建议：你本地登录 Kaggle 后手动下载，再补进知识库

2. **ducenand/JieMeng**
   - 这是抓取工程仓库，不是已经整理好的现成数据导出包
   - 更适合参考抓取逻辑，不适合直接拿来当知识库成品

3. **AbsoluteWinter/tarot-database**
   - README 能确认仓库方向是 “JSON + base64 图像数据库”
   - 但这次没有自动把整个仓库数据目录逐个拉下来
   - 如果你要，我下一轮可以继续针对这个仓库做“定向补抓”

---

## 2. 每个来源适合你项目里的哪个位置

| 来源 | 最适合的用途 | 是否建议直接进 Dify 知识库 |
|---|---|---|
| dream_decoder_data_clean | 解梦问答对 / 梦境解释语料 | **建议**，非常适合 |
| Dendory_tarot_readings_clean | 三张牌组合阅读训练语料 | **建议**，适合“最终解读节点” |
| AI_Diviner_Tarot.ts | 牌名、牌阵、前端配置 | 不建议直接全文塞知识库，建议抽取结构 |
| tarot_reader.py | 流程与程序逻辑参考 | 不建议直接塞知识库 |
| card-relations.md | 多牌关系解释规则 | **强烈建议**，很适合 RAG |
| Kaggle 78 cards meanings | 单牌静态牌义 | **建议补下** |
| JieMeng 抓取工程 | 数据采集参考 | 不建议直接进知识库 |
| AbsoluteWinter/tarot-database | 结构化塔罗库 + 图像方向 | 值得后续继续补抓 |

---

## 3. 我对你当前项目的推荐组合

### A. 先做“最小可用知识库”
优先用这 3 份：
1. `cleaned/dream_decoder_data_clean.csv`
2. `cleaned/Dendory_tarot_readings_clean.csv`
3. `raw/card-relations.md`

这样你就已经有：
- 解梦解释语料
- 三张牌组合解读语料
- 多牌关系理论规则

### B. 第二批再补
1. Kaggle 78 张牌单牌牌义
2. AbsoluteWinter 的 JSON 数据
3. 你自己整理过的专业塔罗文档

### C. 不建议直接一股脑上传的
1. `tarot_reader.py`
2. `AI_Diviner_Tarot.ts`
3. `JieMeng` 抓取工程代码

这些更适合你做：
- 字段抽取
- 规则设计
- 业务逻辑参考

---

## 4. 文件结构

```text
tarot_dream_data_pack/
├── cleaned/
│   ├── dream_decoder_data_clean.csv
│   ├── dream_decoder_data_clean.jsonl
│   └── Dendory_tarot_readings_clean.csv
├── raw/
│   ├── dream_decoder_data_raw.jsonl
│   ├── Dendory_tarot_readings.csv
│   ├── AI_Diviner_Tarot.ts
│   ├── tarot_reader.py
│   ├── card-relations.md
│   ├── AbsoluteWinter_tarot_database_README.md
│   └── Dendory_tarot_README.md
├── source_manifest.csv
└── report.md
```

---

## 5. 快速统计

### dream_decoder_data_clean
- 行数：**33,830**
- 列：`dream`, `decode`
- 特点：
  - 中文
  - 适合解梦类问答
  - 非常适合作为检索知识库或后续微调素材

### Dendory_tarot_readings_clean
- 行数：**5,769**
- 列：`Card 1`, `Card 2`, `Card 3`, `Reading`
- 特点：
  - 英文
  - 适合三张牌组合解读
  - 对你的 LLM3 最终报告节点尤其有参考价值

### AI_Diviner_Tarot.ts
- 英文标签数量：**79**
- 中文标签数量：**0**
- 牌阵数量：**0**
- 备注：
  - 文件里 `World` 出现了重复标签，后续你正式接系统时建议检查一次映射一致性

### card-relations.md
- 标题层级数量：**24**
- 内容方向：
  - 愚人之旅
  - 数字旅程
  - 元素关系
  - 对位牌
  - 宫廷牌关系
- 很适合做“增强解释规则库”

---

## 6. 下一步建议（按你的 Dify 项目来）

### 最推荐的上传顺序
1. 先上传 `raw/card-relations.md`
2. 再上传 `cleaned/dream_decoder_data_clean.csv`
3. 再上传 `cleaned/Dendory_tarot_readings_clean.csv`

### 你的两个核心节点可以这样分
- **LLM 2（验证节点）**
  - 更偏向检索 `card-relations.md`
  - 目标是让用户觉得“说到状态了”

- **LLM 3（最终解读节点）**
  - 更偏向检索 `Dendory_tarot_readings_clean.csv`
  - 如果是解梦模式，再检索 `dream_decoder_data_clean.csv`
  - 目标是生成完整、有结构的最终报告

### 建议你后续补做的事情
1. 把 Kaggle 的 78 张单牌牌义补下
2. 把 AbsoluteWinter 仓库的 JSON 数据进一步提取出来
3. 把中英文塔罗名称做一次统一映射表
4. 在入库前做字段清洗，避免同一张牌出现多个命名版本

---

## 7. 备注

- 这次整理的重点是：**先把你能马上用进 Dify 的资料包搭起来**
- 所以我优先处理了：
  - 可直接下载的公开文件
  - 可直接进知识库的语料
  - 对你当前塔罗/解梦工作流最有用的结构

