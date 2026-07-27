"""
Pleadly Prompt Engine — 十步全流程工作流调度中心
负责: Prompt模板管理 → LLM调用 → 输出结构化
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from openai import OpenAI

# ── DeepSeek Client ──
_client: Optional[OpenAI] = None

def get_llm_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
    return _client

# ── Data Models ──

@dataclass
class AnalysisInput:
    resume_text: str
    jd_text: str
    extra_instructions: str = ""

@dataclass
class AnalysisResult:
    step_name: str
    content: str
    metadata: Dict[str, Any] = None

# ── Prompt Registry ──

STEP_PROMPTS = {
    "ats_check": "core/prompts/ats_check.py",
    "match_score": "core/prompts/match_score.py",
    "jd_analysis": "core/prompts/jd_analysis.py",
    "resume_diagnosis": "core/prompts/resume_diagnosis.py",
    "jd_ranking": "core/prompts/jd_ranking.py",
    "learning_plan": "core/prompts/learning_plan.py",
    "interview_prep": "core/prompts/interview_prep.py",
    "mock_interview": "core/prompts/mock_interview.py",
    "offer_eval": "core/prompts/offer_eval.py",
    "culture_guide": "core/prompts/culture_guide.py",
}

def get_prompt(step: str) -> str:
    """Load prompt template by step name."""
    prompt_file = STEP_PROMPTS.get(step)
    if prompt_file:
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            pass
    # Fallback — return built-in prompt
    return _get_builtin_prompt(step)

def _get_builtin_prompt(step: str) -> str:
    """Built-in fallback prompts when external files not found."""
    prompts = {
        "ats_check": ATS_CHECK_PROMPT,
        "match_score": MATCH_SCORE_PROMPT,
        "jd_analysis": JD_ANALYSIS_PROMPT,
        "resume_diagnosis": RESUME_DIAGNOSIS_PROMPT,
        "learning_plan": LEARNING_PLAN_PROMPT,
        "interview_prep": INTERVIEW_PREP_PROMPT,
    }
    return prompts.get(step, "")

# ── LLM Call ──

def call_llm(system_prompt: str, user_prompt: str, stream: bool = False) -> str:
    """Unified LLM call with DeepSeek."""
    client = get_llm_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
        stream=stream,
    )
    if stream:
        return response  # Returns stream object for caller to iterate
    return response.choices[0].message.content

# ── Engine ──

def run_step(
    step: str,
    user_input: AnalysisInput,
    rag_context: str = "",
    previous_steps: Dict[str, str] = None,
    user_context: str = "",  # v2: 用户信息库检索结果
) -> AnalysisResult:
    """Execute one step of the workflow."""
    prompt_template = get_prompt(step)
    if not prompt_template:
        return AnalysisResult(step_name=step, content=f"错误: 未找到步骤 '{step}' 的 Prompt。")

    # Build system prompt with all context
    context_blocks = []
    if rag_context:
        context_blocks.append(rag_context)
    if user_context:
        context_blocks.append(user_context)

    system_prompt = "你是Pleadly的AI招聘经理。严格按以下要求输出分析结果。禁止编造信息。\n"
    if context_blocks:
        system_prompt += "\n" + "\n".join(context_blocks)

    user_prompt = prompt_template.replace("{RESUME}", user_input.resume_text)
    user_prompt = user_prompt.replace("{JD}", user_input.jd_text)
    if previous_steps:
        for k, v in previous_steps.items():
            user_prompt = user_prompt.replace(f"{{{k.upper()}}}", v)

    try:
        content = call_llm(system_prompt, user_prompt)
        return AnalysisResult(step_name=step, content=content)
    except Exception as e:
        return AnalysisResult(step_name=step, content=f"分析出错: {str(e)}")

# ═══════════════════════════════════════════
# Built-in Prompt Templates (fallback)
# ═══════════════════════════════════════════

ATS_CHECK_PROMPT = """你是ATS简历筛选系统。请执行以下任务：

## 简历
{RESUME}

## 岗位JD
{JD}

## 任务
1. 从JD中提取所有高频关键词和必须出现的技能/经验术语
2. 逐条检测简历中是否出现这些关键词
3. 输出表格:

| 关键词 | JD中出现位置 | 简历中是否命中 | 如未命中建议插入位置 |
|------|------|:---:|------|
| [关键词] | [位置] | ✅/❌ | [建议] |

如关键硬性要求缺失，标红警告。"""

MATCH_SCORE_PROMPT = """你是招聘评估专家。为候选人进行岗位匹配度评分。

## 简历
{RESUME}

## 岗位JD
{JD}

## 评分维度(6维加权)
- 硬性门槛(学历/专业/年限/证书): 30分
- 技能栈匹配: 25分
- 行业经验匹配: 15分
- 项目/作品匹配: 15分
- 加分项命中: 10分
- 隐性匹配(学习能力/自驱力): 5分

## 输出格式
总分: XX/100 → 🟢高度匹配/🟡较匹配/🟠可冲/🔴不匹配/⚫放弃

每个维度写出评分依据和扣分点。"""

JD_ANALYSIS_PROMPT = """你是行业分析师。全面拆解以下岗位JD。

## JD
{JD}

## 输出结构
1. 公司背景(2-3句话讲清商业模式)
2. 岗位业务分析(入职后实际在做什么)
3. 硬性要求(🔴必须/🟡优选/🟢加分)
4. 隐形需求(JD没写但面试官在意的)
5. 面试追问方向(6-8题，标注真正在测什么)"""

RESUME_DIAGNOSIS_PROMPT = """你是简历诊断师。逐行对照JD诊断简历。

## JD分析(前面已完成)
{JD_ANALYSIS}

## 简历
{RESUME}

## 输出四部分
1. 匹配点(简历原文→JD哪条→强度⭐⭐⭐/⭐⭐/⭐)
2. 冗余点(简历原文→为什么冗余→删除/压缩/改写)
3. 缺失点(JD要求→现状→严重度🔴/🟡/🟢)
4. 风险点(原文→负面信号→风险等级→修复方案)"""

LEARNING_PLAN_PROMPT = """你是学习规划师。基于简历诊断中的缺失点，输出学习计划。

## 诊断结果
{DIAGNOSIS}

## 输出: 每条学习任务包含
- 要补的缺口(对应JD哪条)
- 学习内容 + 学习资源(优先免费)
- 预计周期 + 重要程度(🔴必须/🟡建议/🟢可选)
- 可验证产出(学到什么程度算学完了)

按 严重度+紧急度+学习周期 综合排序。"""

INTERVIEW_PREP_PROMPT = """你是面试教练。基于JD和候选人背景，准备全流程面试题库。

## JD分析
{JD_ANALYSIS}

## 诊断结果
{DIAGNOSIS}

## 输出6阶段
A. HR电话初筛(9题逐字话术)
B. 笔试/测评(预测题型+答题框架)
C. 技术面(分级题库 ⭐→⭐⭐→⭐⭐⭐)
D. 行为面(5个STAR故事)
E. 总监/终面(5-8个高层次问题)
F. 情景模拟(3-5角色扮演脚本)"""
