# AI-Powered Tarot & Dream Interpretation System

一个结合 **塔罗占卜** 与 **梦境解析** 的 AI 互动系统。  
项目通过 **规则式流程控制 + 本地知识库检索（RAG）+ 大语言模型生成**，为用户提供具有沉浸感与个性化风格的占卜/解梦体验。

---

## 1. Project Overview

本项目旨在实现一个本地可运行的 AI 占卜原型系统，支持两种核心模式：

- **Tarot Mode（塔罗模式）**
  - 用户输入问题
  - 系统引导用户凭直觉选择卡组 / 指示牌
  - 后端根据规则完成抽牌流程
  - 结合塔罗知识库进行语义检索
  - 由大模型生成最终解读

- **Dream Mode（解梦模式）**
  - 用户输入梦境内容
  - 系统从梦境语料库中召回相关解释片段
  - 结合检索内容与用户输入生成更自然的解析结果

该项目不仅关注“能不能回答”，也关注“**回答过程是否具有体验感**”。  
因此在实现层面同时包含：

- **后端推理与检索逻辑**
- **前端沉浸式交互设计**
- **本地部署与展示能力**

---

## 2. Key Features

### 2.1 Dual-Mode Interaction
系统支持双模式切换：

- 塔罗占卜
- 梦境解析

两种模式共享统一的 AI 服务框架，但在输入形式、检索知识源和交互流程上各自独立。

### 2.2 Rule-Based Tarot Workflow
塔罗模式不是简单地“随机回答”，而是基于预设流程控制进行：

- 用户输入问题与主题方向
- 引导用户选择 A / B / C 指示组
- 根据选中的组返回对应牌阵
- 组合牌义文本，构造检索查询
- 将召回结果与当前牌面共同送入模型生成解释

这种设计保证了系统既有仪式感，也有一定结构化逻辑。

### 2.3 RAG-Based Interpretation
项目引入 **Retrieval-Augmented Generation (RAG)** 机制：

- 使用本地塔罗 / 梦境语料构建知识库
- 使用向量模型生成 embedding
- 基于 FAISS 进行相似度检索
- 将召回文本与当前问题拼接给大模型
- 输出更贴合主题、减少空泛回答的解释结果

### 2.4 Local Knowledge Base
系统依赖本地构建的数据资源，包括但不限于：

- 塔罗牌义文本
- 塔罗案例数据
- 梦境解析语料
- 清洗后的结构化 chunk 数据
- FAISS 索引与 metadata

这样做的好处是：

- 可离线管理知识源
- 方便扩展领域数据
- 有助于控制回答风格和内容边界

### 2.5 Immersive Front-End Design
前端不仅承担输入输出，还承担“体验塑造”：

- 神秘风格主视觉
- 3D / 翻转式模式切换卡牌
- 抽牌、洗牌、加载等仪式化动画
- 牛皮纸 / 金色粒子 / 中世纪奇幻风格 UI
- 通过视觉反馈提升用户沉浸感

---

## 3. System Architecture

整体流程如下：

1. **User Input**
   - 用户输入问题或梦境文本
   - 在塔罗模式中进一步进行指示牌 / 卡组选取

2. **Workflow Control**
   - 后端根据模式选择不同服务逻辑
   - 塔罗模式执行规则式抽牌与 query 构造
   - 解梦模式直接构造 dream query

3. **Retriever**
   - 从本地向量库中召回最相关文本片段
   - 返回 top-k 结果作为上下文

4. **LLM Generation**
   - 将用户输入 + 检索结果 + 流程状态拼接成 prompt
   - 调用模型生成最终解释

5. **Frontend Rendering**
   - 前端展示结果，并通过动画与视觉设计强化体验

---

## 4. Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### Retrieval / NLP
- sentence-transformers
- FAISS
- 本地文本清洗与 chunk 构建脚本

### Frontend
- HTML / CSS / JavaScript
- 自定义动画与视觉交互
- 多版前端 bundle 用于 UI 迭代测试

### Data Processing
- 自定义脚本进行：
  - 数据清洗
  - chunk 构造
  - embedding 生成
  - 向量索引构建

---

## 5. Project Structure

当前项目目录大致如下：

```bash
tarot_dream_app/
├── app.py
├── requirements.txt
├── data/
├── frontend/
├── rag/
├── scripts/
├── services/
├── tarot_intro_frontend_bundle/
├── tarot_intro_frontend_bundle_v2/
├── tarot_intro_frontend_bundle_v3/
├── ...
└── tarot_intro_frontend_bundle_v11/
```



## 8. Installation & Run

### 8.1 Create Conda Environment

建议使用 `conda` 创建独立环境运行本项目：

```bash
conda create -n tarotdream python=3.10 -y
conda activate tarotdream
pip install -r requirement.txt
```

## 9. How to Run

本项目当前以后端本地启动为主，入口文件为 `app.py`。  
请注意，当前目录结构并不是 `app/main.py`，因此启动命令应使用：

```bash
uvicorn app:app --reload
```

