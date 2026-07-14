# Job Fit Check — 岗位匹配检测 / Job Fit Checker

> 🔍 Reverse-engineer job descriptions. Rewrite resumes with surgical precision.  
> 🔍 逆向拆解岗位JD，像素级优化简历——让应届生看清"这个岗位到底要什么人"。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Prompts: 4](https://img.shields.io/badge/Prompts-4-blue.svg)](prompts/)
[![Lang: ZH+EN](https://img.shields.io/badge/Lang-ZH%20%7C%20EN-orange.svg)](#)

---

## What is this? / 这是什么？

A **prompt-based workflow** that transforms how fresh graduates match their resumes to job descriptions. It's a 4-step methodology originally built for a Xiaohongshu (RED) content creator, now open-sourced so anyone can use it.

一套**基于 Prompt 的工作流**，帮助应届生精准匹配简历与岗位。原本是为一个小红书账号设计的方法论，现在开源——任何人都能用。

**Every step is a prompt you can drop into ChatGPT, Claude, DeepSeek, Kimi, or any other LLM.**

---

## The 4-Step Workflow / 四步工作流

```
📥 INPUT: Your Resume + The Job Description (JD)
                      │
┌─────────────────────▼──────────────────────┐
│ ① Job Deconstruction / 岗位拆解              │
│    └─ prompts/job-analysis.md              │
│    Hard requirements, hidden needs,        │
│    core skills, bonus points,              │
│    likely interview angles                 │
├─────────────────────────────────────────── -┤
│ ② Resume Diagnosis / 简历诊断               │
│    └─ prompts/resume-diagnosis.md          │
│    Matches, redundancies, gaps, risks      │
├─────────────────────────────────────────── -┤
│ ③ Targeted Rewrite / 定向优化               │
│    └─ prompts/resume-rewrite.md            │
│    STAR rewrites, self-summary overhaul,   │
│    skills reordering, layout tweaks        │
├─────────────────────────────────────────── -┤
│ ④ Final Output / 终稿输出                   │
│    └─ prompts/final-output.md              │
│    Optimized full resume + Cover Letter    │
│    highlights + Application strategy       │
└─────────────────────┬──────────────────────┘
                      │
📤 OUTPUT: Complete diagnostic report + Optimized resume
```

---

## Quick Start / 快速开始

### Option 1: One-by-one (more control)

Copy each prompt in order, paste into your preferred LLM with your data.

1. Open [`prompts/job-analysis.md`](prompts/job-analysis.md) → Copy → Paste into LLM → Get analysis
2. Open [`prompts/resume-diagnosis.md`](prompts/resume-diagnosis.md) → Copy → Paste into LLM (with the analysis above) → Get diagnosis
3. Open [`prompts/resume-rewrite.md`](prompts/resume-rewrite.md) → Copy → Paste → Get rewrite suggestions
4. Open [`prompts/final-output.md`](prompts/final-output.md) → Copy → Paste → Get final polished resume

### Option 2: All-in-one (faster)

Copy all 4 prompts, chain them into one mega-prompt, and feed your resume + JD once.

### Option 3: Claude Code / SDK Agent

If you use [Claude Code](https://claude.ai/code), you can wire these prompts into a custom agent that triggers with one command. See [Advanced Usage](#advanced-usage--进阶用法) below.

---

## What You'll Get / 你会得到什么

| Step | Output |
|------|--------|
| ① | 硬性门槛 / 隐形需求 / 核心能力 / 加分项 / 面试追问方向 |
| ② | 匹配点 / 冗余内容(应删除) / 缺失项 / 风险点 |
| ③ | 每段经历 STAR 重写 / 自我评价定向修改 / 技能板块重组 / 排版建议 |
| ④ | 优化后简历全文 + Cover Letter 要点 + 投递渠道策略 |

---

## Examples / 示例

See [`examples/`](examples/) for complete walkthroughs with simulated data:

| Example | Scenario |
|---------|---------|
| [Product Manager (New Grad)](examples/product-manager.md) | CS major → PM role at a mid-size internet company |
| [Digital Marketing](examples/digital-marketing.md) | Marketing major with agency internship → Brand-side marketing role |

Each example shows the full 4-step output so you know exactly what to expect.

---

## How This Came About / 项目背景

This methodology was developed for a [Xiaohongshu (RED)](https://www.xiaohongshu.com) content creator account focused on helping Chinese fresh graduates optimize their resumes. The core insight:

> **"Recruiters spend 6 seconds per resume. Every word on yours must answer: what problem can you solve for me?"**

After optimizing 50+ real resumes, the patterns crystallized into a repeatable 4-step framework. This repo is that framework, made public.

*Follow the creator on RED (account coming soon) for bite-sized resume tips derived from this methodology.*

---

## Advanced Usage / 进阶用法

### Option A: Claude Code Agent (one-command trigger)

If you use [Claude Code](https://claude.ai/code):

1. Copy [`job-fit-check-agent.md`](job-fit-check-agent.md) to `~/.claude/agents/job-fit-check.md`
2. In Claude Code, type `/job-fit-check`
3. Paste your JD + resume. The agent runs all 4 steps automatically.

That's it. One command, full diagnostic report.

### Option B: Manual copy-paste (no tools needed)

Open each file in [`prompts/`](prompts/), copy the prompt, paste into ChatGPT / Claude / Kimi / DeepSeek. Fill in `[PASTE JD HERE]` and `[PASTE RESUME HERE]` placeholders. Run them in order (① → ② → ③ → ④).

### As a GitHub Action / CI

Coming soon — automatically run job-fit-check on every PR that modifies your resume LaTeX/Markdown file.

---

## Contributing / 贡献

Found a prompt that could be sharper? Have a real-world case study to share? PRs welcome.

1. Fork this repo
2. Improve a prompt or add an example
3. Submit a PR with your changes and why

See [CONTRIBUTING.md](CONTRIBUTING.md) for details (coming soon).

---

## License / 协议

MIT — take it, use it, remix it, teach with it. Just keep the attribution.

See [LICENSE](LICENSE) for full text.

---

<p align="center">
  <sub>Built with ❤️ for job seekers everywhere. | 为每一个求职者而建。</sub>
</p>
