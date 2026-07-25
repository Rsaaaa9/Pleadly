---
title: Pleadly — Smart Job Search
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: AI-powered full-cycle career assistant — from JD to Day One
---

# 我求你了 / Pleadly

> AI招聘经理视角的全流程求职助手 — 从JD投递到入职，每一步都有你。
> AI-powered full-cycle career assistant — from job matching to day-1 survival guide.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Topics](https://img.shields.io/badge/topics-jobsearch%20|%20ai%20|%20career-orange)](https://github.com/topics/jobsearch)

---

[中文](#中文) | [English](#english)

---

## 中文

### 这是什么

**我求你了**（英文名 **Pleadly** = Plead + ly，「聪明地求职」）是一套面向应届生的全流程 AI 求职系统。输入你的简历和岗位 JD，AI 招聘经理帮你跑完从投递到入职的完整分析。

### 十步工作流

| Step | 模块 | 说明 |
|:---:|------|------|
| 1 | ATS 关键词检测 | 提取 JD 关键词 → 检查简历命中率 → 避免机器筛选翻车 |
| 2 | 岗位匹配度评分 | 6 维度百分制加权评分 → 🟢匹配 / 🟡冲击 / 🔴放弃 |
| 3 | JD 全维度拆解 | 公司背景 + 岗位业务 + 硬性要求 + 隐形需求 + 面试追问预测 |
| 4 | 简历逐行诊断 | 匹配点 + 冗余点 + 缺失点 + 风险点（均含修复方案） |
| 5 | 多 JD 优先级排序 | 6 维度加权排序 → 精力分配策略 |
| 6 | 差距学习计划 | 按严重度 + 紧急度 + 学习周期综合排序 |
| 7 | 全流程面试准备 | HR 初筛 → 笔试 → 技术面 → 行为面 → 终面 → 情景模拟，6 阶段逐题话术 |
| 8 | Mock 面试官模式 | 切换面试官角色 → 随机出题 → 追问 → 即时反馈 |
| 9 | Offer 薪资谈判 | 市场薪资对标 + 7 维度谈判点拆解 + 逐字话术脚本 |
| 10 | 公司文化入职指南 | 文化速写 + 第一周 Checklist + 首月关键动作 + 退出信号识别 |

### 设计原则

- **所有分析基于真实数据**：公司信息、行业薪资、面试题库来自联网检索和持续积累，不做编造
- **AI 辅助但不替代判断**：每一步都有明确的人机边界——AI 提供推荐和分析，最终决策责任属于用户
- **开箱即用的 Prompt 体系**：每个模块既是可运行的代码，也是可复制粘贴到任何 AI 工具中的独立 Prompt
- **RAG 知识库持续积累**：面试题库、公司信息、简历模板、薪资数据通过向量数据库统一管理
- **中英双语支持**：界面支持一键切换中文/英文，满足不同场景需求

### 项目结构

```
pleadly/
├── app/                  # 应用前端
│   ├── main.py           # Gradio 入口 + 双语 UI + 语言切换
│   └── components/       # 可复用组件
├── core/                 # 核心引擎
│   ├── engine.py         # Prompt Engine（十步工作流调度）
│   ├── agent.py          # Agent 工具调用（WebSearch / 文档解析）
│   └── prompts/          # 各步骤 Prompt 模板
├── rag/                  # RAG 知识库
│   ├── vector_store.py   # ChromaDB 管理 + 检索管道
│   └── data/             # 种子数据（面试题 / 公司信息 / 薪资 / 模板）
├── deploy/               # 部署配置（Dockerfile）
├── tests/                # 测试
├── CLAUDE.md             # Claude Code 终端入口（进入目录自动加载）
└── README.md
```

### 技术栈

| 层 | 技术 |
|------|------|
| 前端 | Gradio 5.0（中英双语界面） |
| 后端 | FastAPI + Uvicorn |
| LLM | DeepSeek API |
| RAG | ChromaDB + text2vec-base-chinese |
| Agent Tools | WebSearch + 文档解析 + 薪资检索 |

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/Rsaaaa9/Pleadly.git
cd Pleadly

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key

# 4. 启动
python app/main.py
# 访问 http://localhost:7860
# 点击 🇨🇳中文 / 🇺🇸English 切换语言
```

### License

MIT — 自由使用、修改、分发。保留署名。

---

## English

### What is Pleadly?

**Pleadly** (Plead + ly = "pleading smartly") is an AI-powered full-cycle job search system designed for new graduates. Paste your resume and a job description — an AI hiring manager runs you through the complete analysis from application to onboarding.

### The 10-Step Workflow

| Step | Module | Description |
|:---:|------|------|
| 1 | ATS Keyword Detection | Extract JD keywords → check resume hit rate → avoid auto-rejection |
| 2 | Job Match Score | 6-dimension weighted score → 🟢Match / 🟡Stretch / 🔴Skip |
| 3 | JD Deep Analysis | Company background + role context + hard requirements + hidden expectations |
| 4 | Resume Gap Diagnosis | Match points + redundancies + gaps + risks (all with fix plans) |
| 5 | Multi-JD Prioritization | 6-dimension weighted ranking → energy allocation strategy |
| 6 | Learning Plan | Gaps ranked by severity × urgency × learning time → roadmap |
| 7 | Interview Preparation | HR screen → tech → behavioral → final → scenario — 6 stages, detailed scripts |
| 8 | Mock Interview Mode | AI switches to interviewer role → random questions → follow-ups → instant feedback |
| 9 | Offer Negotiation | Market salary benchmarking + 7-dimension negotiation analysis + script |
| 10 | Culture & Survival Guide | Company culture snapshot + Week 1 checklist + Month 1 key moves + red flags |

### Design Principles

- **Real data only**: Company info, salary data, and interview questions come from web search and accumulated knowledge — never fabricated
- **AI assists, you decide**: Every step has a clear human-AI boundary — AI provides analysis and recommendations; the final call is yours
- **Prompt-first design**: Every module works as both executable code and a standalone prompt you can copy into any AI tool
- **Growing RAG knowledge base**: Interview Q&A, company profiles, resume templates, and salary data are managed through a vector database
- **Bilingual support**: Full Chinese/English UI with one-click language toggle

### Tech Stack

| Layer | Technology |
|------|------|
| Frontend | Gradio 5.0 (bilingual UI) |
| Backend | FastAPI + Uvicorn |
| LLM | DeepSeek API |
| RAG | ChromaDB + text2vec-base-chinese |
| Agent Tools | WebSearch + Document parsing + Salary retrieval |

### Quick Start

```bash
git clone https://github.com/Rsaaaa9/Pleadly.git
cd Pleadly
pip install -r requirements.txt
cp .env.example .env  # Edit with your DeepSeek API key
python app/main.py     # Open http://localhost:7860
```

### License

MIT — Free to use, modify, and distribute. Attribution appreciated.
