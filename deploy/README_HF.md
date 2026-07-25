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

# 🎯 Pleadly — 聪明地求职

**AI 招聘经理视角的全流程求职助手**
**AI-Powered Full-Cycle Career Assistant**

粘贴你的简历 + 岗位JD → AI 跑完从投递到入职的完整分析。
Paste your resume + JD → AI runs the full analysis from application to onboarding.

[中文](#-中文) · [English](#-english)

---

## 🇨🇳 中文

### 🔥 功能

| 步骤 | 功能 | 做什么 |
|:---:|------|------|
| ① | ATS 关键词检测 | JD关键词 → 简历命中率 → 防机器筛选翻车 |
| ② | 岗位匹配度评分 | 6维度百分制加权 → 🟢匹配 🟡冲击 🔴放弃 |
| ③ | JD 全维度拆解 | 公司背景 + 硬性要求 + 隐形需求 + 面试追问预测 |
| ④ | 简历逐行诊断 | 匹配点/冗余/缺失/风险（均含修复方案） |
| ⑥ | 差距学习计划 | 缺口 × 紧急度 × 学习周期 → 学习路线图 |
| ⑦ | 全流程面试准备 | HR初筛→技术面→行为面→终面，逐题话术 |

### 🚀 使用方法

1. 粘贴你的 **简历**（或上传 docx/pdf）
2. 粘贴目标岗位的 **JD**
3. （可选）输入 **公司名称** → 自动联网搜索背景和面经
4. 点击 **一键全流程分析** → 等待 1-3 分钟获取完整报告

### 🌍 语言

点击页面顶部的 **🇨🇳 中文 / 🇺🇸 English** 按钮一键切换界面语言。

### ⚙️ 环境变量

在 Hugging Face Spaces 的 Settings → Secrets 中配置：

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（**必填**） |
| `DEEPSEEK_BASE_URL` | API 地址（默认 `https://api.deepseek.com`） |

### 🔒 隐私

你的简历和JD仅用于本次分析，**不会存储**。所有AI调用通过 DeepSeek API。

---

## 🇬🇧 English

### 🔥 Features

| Step | Module | What it does |
|:---:|------|------|
| ① | ATS Keyword Detection | Extract JD keywords → resume hit rate → avoid auto-filtering |
| ② | Job Match Score | 6-dimension weighted score → Match / Stretch / Skip |
| ③ | JD Deep Analysis | Company research + hard reqs + hidden expectations |
| ④ | Resume Gap Diagnosis | Match / Redundancy / Gap / Risk (all with fix plans) |
| ⑥ | Learning Plan | Gap × urgency × timeline → personalized roadmap |
| ⑦ | Interview Prep | HR → Technical → Behavioral → Final — full scripts |

### 🚀 How to Use

1. Paste your **resume** (or upload docx/pdf)
2. Paste the **job description**
3. (Optional) Enter **company name** → auto web search for background & interview intel
4. Click **Run Full Analysis** → wait 1-3 minutes for the complete report

### 🌍 Language

Click **🇨🇳 中文 / 🇺🇸 English** at the top to toggle the interface language.

### ⚙️ Environment Variables

Configure in Hugging Face Spaces → Settings → Secrets:

| Variable | Description |
|------|------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API Key (**required**) |
| `DEEPSEEK_BASE_URL` | API endpoint (default: `https://api.deepseek.com`) |

### 🔒 Privacy

Your resume and JD are used only for this session — **never stored**. All AI calls go through the DeepSeek API.

---

## 📂 Source Code

[github.com/Rsaaaa9/Pleadly](https://github.com/Rsaaaa9/Pleadly)
