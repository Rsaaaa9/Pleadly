"""
Pleadly Gradio App — AI-Powered Full-Cycle Career Assistant
Launch: python app/main.py

双语支持 / Bilingual Support: 中文 (zh) | English (en)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from dotenv import load_dotenv
load_dotenv()

from core.engine import (
    AnalysisInput, run_step, get_llm_client
)
from core.agent import AgentOrchestrator, search_company_info, search_interview_experience

# ═══════════════════════════════════════════════════════════
# BILINGUAL TEXT DICTIONARY
# ═══════════════════════════════════════════════════════════
T = {
    "title_full": {
        "zh": "# 🎯 Pleadly — 聪明地求职\n### AI招聘经理视角的全流程求职助手",
        "en": "# 🎯 Pleadly — Job Search, Done Smart\n### AI-Powered Full-Cycle Career Assistant"
    },
    "hero_desc": {
        "zh": "粘贴你的**简历**和**岗位JD**，AI帮你跑完从投递到入职的完整分析。",
        "en": "Paste your **resume** and **job description** — AI runs the full analysis from application to onboarding."
    },
    "resume_label":   {"zh": "📄 你的简历", "en": "📄 Your Resume"},
    "resume_ph":      {"zh": "在此粘贴简历内容（或上传文件）\n\n郑灿坤\n教育背景:\n中南林业科技大学...", "en": "Paste your resume here (or upload a file)\n\nJohn Doe\nEducation:\nB.Sc. Computer Science..."},
    "resume_upload":  {"zh": "或上传简历文件（docx/pdf/txt）", "en": "Or upload resume file (docx/pdf/txt)"},
    "jd_label":       {"zh": "📋 岗位JD", "en": "📋 Job Description"},
    "jd_ph":          {"zh": "在此粘贴岗位JD\n\n职位名称: AI产品经理\n公司: XX科技\n任职要求:\n1. ...", "en": "Paste the job description here\n\nTitle: AI Product Manager\nCompany: Acme Corp\nRequirements:\n1. ..."},
    "company_label":  {"zh": "公司名称（可选，用于联网背景调查和面经搜索）", "en": "Company name (optional — enables web search for background & interview experiences)"},
    "company_ph":     {"zh": "例如: 进迭时空、健康元、字节跳动", "en": "e.g. Google, Stripe, ByteDance"},
    "run_all_btn":    {"zh": "🚀 一键全流程分析", "en": "🚀 Run Full Analysis"},
    "clear_btn":      {"zh": "🗑️ 清空", "en": "🗑️ Clear"},
    "zh_btn":         {"zh": "🇨🇳 中文", "en": "🇨🇳 中文"},
    "en_btn":         {"zh": "🇺🇸 English", "en": "🇺🇸 English"},
    "step_section":   {"zh": "### 🔧 分步分析（可选）", "en": "### 🔧 Step-by-Step Analysis (Optional)"},
    "acc_12":         {"zh": "Step 1-2: ATS检测 + 匹配评分", "en": "Step 1-2: ATS Check + Match Score"},
    "acc_34":         {"zh": "Step 3-4: JD拆解 + 简历诊断", "en": "Step 3-4: JD Analysis + Resume Diagnosis"},
    "acc_67":         {"zh": "Step 6-7: 学习计划 + 面试准备", "en": "Step 6-7: Learning Plan + Interview Prep"},
    "btn_1":          {"zh": "① ATS关键词检测", "en": "① ATS Keyword Check"},
    "btn_2":          {"zh": "② 岗位匹配度评分", "en": "② Job Match Score"},
    "btn_3":          {"zh": "③ JD全维度拆解（含公司背景）", "en": "③ JD Deep Analysis (+ Company Research)"},
    "btn_4":          {"zh": "④ 简历对照诊断", "en": "④ Resume Gap Diagnosis"},
    "btn_6":          {"zh": "⑥ 差距学习计划", "en": "⑥ Learning Plan"},
    "btn_7":          {"zh": "⑦ 全流程面试准备（含面经搜索）", "en": "⑦ Interview Prep (+ Real Experiences)"},
    "usage_title":    {"zh": "### 📖 使用说明", "en": "### 📖 How to Use"},
    "usage_steps": {
        "zh": "1. **粘贴简历** — 可以是纯文本，也可以上传 docx/pdf 文件\n2. **粘贴JD** — 从招聘网站直接复制\n3. **（可选）输入公司名** — 我会联网搜索公司背景和真实面经\n4. **点击分析** — 等待1-3分钟获取完整报告",
        "en": "1. **Paste your resume** — plain text or upload docx/pdf files\n2. **Paste the JD** — copy directly from any job board\n3. **(Optional) Enter company name** — I'll search company background and real interview experiences\n4. **Click analyze** — wait 1-3 minutes for the full report"
    },
    "privacy_title":  {"zh": "### 🔒 隐私说明", "en": "### 🔒 Privacy"},
    "privacy_text":   {"zh": "你输入的数据仅用于本次分析，不会存储。所有AI调用通过DeepSeek API。", "en": "Your data is used only for this analysis session and is never stored. All AI calls go through the DeepSeek API."},

    # ── v2: Library UI ──
    "lib_accordion":     {"zh": "📂 我的信息库（上传简历/项目/作品集，自动分块索引）", "en": "📂 My Info Library (upload resume/projects/portfolio - auto chunk & index)"},
    "lib_upload":        {"zh": "上传文档到此（简历 / 项目描述 / 作品集 / 证书 — docx/pdf/txt/md）", "en": "Upload documents (resume/project/portfolio/certificate - docx/pdf/txt/md)"},
    "lib_type_label":    {"zh": "文档类型", "en": "Document Type"},
    "lib_type_choices":  {"zh": ["自动检测", "简历", "项目文档", "证书", "其他"], "en": ["Auto-detect", "Resume", "Project Doc", "Certificate", "Other"]},
    "lib_label_label":   {"zh": "标签（可选）", "en": "Label (optional)"},
    "lib_label_ph":      {"zh": "例如: 校招版简历 / Pleadly详细文档", "en": "e.g. Campus Resume / Pleadly Details"},
    "lib_add_btn":       {"zh": "📥 添加到信息库", "en": "📥 Add to Library"},
    "lib_stats_btn":     {"zh": "📊 查看状态", "en": "📊 View Stats"},
    "lib_clear_btn":     {"zh": "🗑️ 清空信息库", "en": "🗑️ Clear Library"},
    "lib_default":       {"zh": "📭 信息库为空。上传你的简历、项目描述、作品集来增强分析质量。", "en": "📭 Library is empty. Upload your resume, projects, or portfolio to enhance analysis quality."},

    "default_output": {
        "zh": "👆 输入简历和JD后点击分析按钮。完整分析需要1-3分钟。\n\n**支持的分步功能：**\n- ① ATS关键词检测\n- ② 岗位匹配度评分（6维度百分制）\n- ③ JD全维度拆解（含公司背景联网搜索）\n- ④ 简历对照诊断（匹配/冗余/缺失/风险）\n- ⑥ 差距分析与学习计划\n- ⑦ 全流程面试准备（含真实面经搜索）",
        "en": "👆 Paste your resume and JD, then click the analysis button. Full analysis takes 1-3 minutes.\n\n**Available step-by-step features:**\n- ① ATS Keyword Detection\n- ② Job Match Score (6-dimension weighted)\n- ③ JD Deep Analysis (with company background research)\n- ④ Resume Gap Diagnosis (match / redundancy / gap / risk)\n- ⑥ Learning Plan (gap → resource → timeline)\n- ⑦ Interview Prep (with real interview experience search)"
    },
    "err_no_resume_jd": {"zh": "请同时输入简历和岗位JD。", "en": "Please enter both your resume and the job description."},
    "err_no_jd":        {"zh": "请先输入JD。", "en": "Please enter the job description first."},
    "status_searching":  {"zh": "正在联网搜索公司信息...\n", "en": "Searching for company information online...\n"},
    "status_found":      {"zh": "✅ 已搜索公司: ", "en": "✅ Company researched: "},
    "status_interview":  {"zh": "正在联网搜索真实面经...\n", "en": "Searching for real interview experiences online...\n"},
    "status_intv_done":  {"zh": "✅ 已搜索面经\n\n", "en": "✅ Interview experiences found\n\n"},
}

# ═══════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="slate",
).set(
    body_text_size="14px",
    button_primary_background_fill="*primary_500",
    button_primary_text_color="white",
)

# ═══════════════════════════════════════════════════════════
# AGENT STATE
# ═══════════════════════════════════════════════════════════
agent = AgentOrchestrator()

# ═══════════════════════════════════════════════════════════
# STEP FUNCTIONS
# ═══════════════════════════════════════════════════════════

def step_ats_check(resume: str, jd: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]
    agent.set_input(resume, jd)
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    user_ctx = agent.get_user_context_for_step("ats_check")
    result = run_step("ats_check", user_input, user_context=user_ctx)
    agent.state.step_results["ats_check"] = result.content
    return result.content

def step_match_score(resume: str, jd: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]
    agent.set_input(resume, jd)
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    user_ctx = agent.get_user_context_for_step("match_score")
    result = run_step("match_score", user_input, user_context=user_ctx)
    agent.state.step_results["match_score"] = result.content
    return result.content

def step_jd_analysis(resume: str, jd: str, company_hint: str, lang: str = "zh"):
    if not jd:
        return T["err_no_jd"][lang]
    agent.set_input(resume, jd)
    status = T["status_searching"][lang]
    if company_hint:
        company_info = search_company_info(company_hint)
        agent.state.company_research = company_info
        status += T["status_found"][lang] + company_hint + "\n"
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    rag_ctx = agent.get_rag_context()
    result = run_step("jd_analysis", user_input, rag_context=rag_ctx, user_context="")
    agent.state.step_results["jd_analysis"] = result.content
    return status + "\n" + result.content

def step_resume_diagnosis(resume: str, jd: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]
    if "jd_analysis" not in agent.state.step_results:
        user_input = AnalysisInput(resume_text=resume, jd_text=jd)
        r = run_step("jd_analysis", user_input)
        agent.state.step_results["jd_analysis"] = r.content
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    user_input.extra_instructions = agent.state.step_results.get("jd_analysis", "")
    user_ctx = agent.get_user_context_for_step("resume_diagnosis")
    result = run_step(
        "resume_diagnosis", user_input,
        previous_steps={"jd_analysis": agent.state.step_results.get("jd_analysis", "")},
        user_context=user_ctx,
    )
    agent.state.step_results["resume_diagnosis"] = result.content
    return result.content

def step_learning_plan(resume: str, jd: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]
    if "resume_diagnosis" not in agent.state.step_results:
        step_resume_diagnosis(resume, jd, lang)
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    user_ctx = agent.get_user_context_for_step("learning_plan")
    result = run_step(
        "learning_plan", user_input,
        previous_steps={"diagnosis": agent.state.step_results.get("resume_diagnosis", "")},
        user_context=user_ctx,
    )
    agent.state.step_results["learning_plan"] = result.content
    return result.content

def step_interview_prep(resume: str, jd: str, company_hint: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]
    status = ""
    if company_hint:
        status += T["status_interview"][lang]
        role_hint = jd.strip().split('\n')[0][:30] if jd else "AI"
        experiences = search_interview_experience(company_hint, role_hint)
        agent.state.interview_experiences = experiences
        status += T["status_intv_done"][lang]
    if "jd_analysis" not in agent.state.step_results:
        step_jd_analysis(resume, jd, company_hint, lang)
    if "resume_diagnosis" not in agent.state.step_results:
        step_resume_diagnosis(resume, jd, lang)
    user_input = AnalysisInput(resume_text=resume, jd_text=jd)
    rag_ctx = agent.get_rag_context()
    user_ctx = agent.get_user_context_for_step("interview_prep", max_chars=3000)
    result = run_step(
        "interview_prep", user_input, rag_context=rag_ctx,
        previous_steps={
            "jd_analysis": agent.state.step_results.get("jd_analysis", ""),
            "diagnosis": agent.state.step_results.get("resume_diagnosis", ""),
        },
        user_context=user_ctx,
    )
    agent.state.step_results["interview_prep"] = result.content
    return status + result.content

def run_all_steps(resume: str, jd: str, company_hint: str, lang: str = "zh"):
    if not resume or not jd:
        return T["err_no_resume_jd"][lang]

    labels = {
        "zh": ["第一步: ATS关键词检测","第二步: 岗位匹配度评分","第三步: JD全维度拆解",
               "第四步: 简历对照诊断","第六步: 差距分析与学习计划","第七步: 全流程面试准备"],
        "en": ["Step 1: ATS Keyword Detection","Step 2: Job Match Score",
               "Step 3: JD Deep Analysis","Step 4: Resume Gap Diagnosis",
               "Step 6: Learning Plan","Step 7: Interview Preparation"]
    }[lang]
    sep = "══════"
    out = []
    out.append(f"# ═{sep} {labels[0]} ═{sep}\n" + step_ats_check(resume, jd, lang))
    out.append(f"\n\n# ═{sep} {labels[1]} ═{sep}\n" + step_match_score(resume, jd, lang))
    out.append(f"\n\n# ═{sep} {labels[2]} ═{sep}\n" + step_jd_analysis(resume, jd, company_hint, lang))
    out.append(f"\n\n# ═{sep} {labels[3]} ═{sep}\n" + step_resume_diagnosis(resume, jd, lang))
    out.append(f"\n\n# ═{sep} {labels[4]} ═{sep}\n" + step_learning_plan(resume, jd, lang))
    out.append(f"\n\n# ═{sep} {labels[5]} ═{sep}\n" + step_interview_prep(resume, jd, company_hint, lang))
    return "\n".join(out)

def clear_all(lang):
    return ("", "", "", T["default_output"][lang])

# ═══════════════════════════════════════════════════════════
# LANGUAGE SWITCH — returns gr.update() for each component
# ═══════════════════════════════════════════════════════════

def build_lang_switch(lang):
    """Return a tuple of updates for all UI components when language changes."""
    t = lambda k: T[k][lang]
    return (
        # title_md (Markdown)
        gr.update(value=t("title_full")),
        # hero_desc_md (Markdown)
        gr.update(value=t("hero_desc")),
        # resume_label_md (Markdown)
        gr.update(value="### " + t("resume_label")),
        # resume_input (Textbox)
        gr.update(placeholder=t("resume_ph")),
        # resume_file (File)
        gr.update(label=t("resume_upload")),
        # jd_label_md (Markdown)
        gr.update(value="### " + t("jd_label")),
        # jd_input (Textbox)
        gr.update(placeholder=t("jd_ph")),
        # company_label_md (Markdown)
        gr.update(value=t("company_label")),
        # company_hint (Textbox)
        gr.update(placeholder=t("company_ph")),
        # run_all_btn (Button)
        gr.update(value=t("run_all_btn")),
        # clear_btn (Button)
        gr.update(value=t("clear_btn")),
        # output_box (Markdown)
        gr.update(value=t("default_output")),
        # step_section_md (Markdown)
        gr.update(value=t("step_section")),
        # acc_12 (Accordion)
        gr.update(label=t("acc_12")),
        # acc_34 (Accordion)
        gr.update(label=t("acc_34")),
        # acc_67 (Accordion)
        gr.update(label=t("acc_67")),
        # step1_btn (Button)
        gr.update(value=t("btn_1")),
        # step2_btn (Button)
        gr.update(value=t("btn_2")),
        # step3_btn (Button)
        gr.update(value=t("btn_3")),
        # step4_btn (Button)
        gr.update(value=t("btn_4")),
        # step6_btn (Button)
        gr.update(value=t("btn_6")),
        # step7_btn (Button)
        gr.update(value=t("btn_7")),
        # usage_title_md (Markdown)
        gr.update(value=t("usage_title")),
        # usage_steps_md (Markdown)
        gr.update(value=t("usage_steps")),
        # privacy_title_md (Markdown)
        gr.update(value=t("privacy_title")),
        # privacy_text_md (Markdown)
        gr.update(value=t("privacy_text")),
        # lib_accordion (Accordion)
        gr.update(label=t("lib_accordion")),
        # lib_file (File)
        gr.update(label=t("lib_upload")),
        # lib_doc_type (Dropdown)
        gr.update(label=t("lib_type_label"), choices=t("lib_type_choices")),
        # lib_label_input (Textbox)
        gr.update(label=t("lib_label_label"), placeholder=t("lib_label_ph")),
        # lib_add_btn_c (Button)
        gr.update(value=t("lib_add_btn")),
        # lib_stats_btn_c (Button)
        gr.update(value=t("lib_stats_btn")),
        # lib_clear_btn_c (Button)
        gr.update(value=t("lib_clear_btn")),
        # lib_stats_output (Markdown)
        gr.update(value=t("lib_default")),
        # lang_state (State)
        lang,
    )


# ═══════════════════════════════════════════════════════════
# GRADIO UI
# ═══════════════════════════════════════════════════════════

with gr.Blocks(theme=theme, title="Pleadly — Smart Job Search") as app:

    lang_state = gr.State("zh")
    L = "zh"  # initial language

    # ── Header ──
    title_md = gr.Markdown(value=T["title_full"]["zh"])

    with gr.Row():
        hero_desc_md = gr.Markdown(value=T["hero_desc"]["zh"])

    with gr.Row():
        zh_btn = gr.Button(T["zh_btn"]["zh"], size="sm", variant="secondary", min_width=80)
        en_btn = gr.Button(T["en_btn"]["en"], size="sm", variant="secondary", min_width=80)

    gr.Markdown("---")

    # ── Inputs ──
    with gr.Row():
        with gr.Column(scale=1):
            resume_label_md = gr.Markdown(value="### " + T["resume_label"]["zh"])
            resume_input = gr.Textbox(
                placeholder=T["resume_ph"]["zh"], lines=12, max_lines=20,
                show_label=False, elem_id="resume-input",
            )
            resume_file = gr.File(
                label=T["resume_upload"]["zh"],
                file_types=[".docx", ".pdf", ".txt", ".md"],
            )

        with gr.Column(scale=1):
            jd_label_md = gr.Markdown(value="### " + T["jd_label"]["zh"])
            jd_input = gr.Textbox(
                placeholder=T["jd_ph"]["zh"], lines=12, max_lines=20,
                show_label=False, elem_id="jd-input",
            )

    company_label_md = gr.Markdown(value=T["company_label"]["zh"])
    company_hint = gr.Textbox(
        placeholder=T["company_ph"]["zh"], show_label=False,
    )

    # ── v2: 用户信息库 ──
    with gr.Accordion(T["lib_accordion"]["zh"], open=False) as lib_accordion:
        with gr.Row():
            lib_file = gr.File(
                label=T["lib_upload"]["zh"],
                file_types=[".docx", ".pdf", ".txt", ".md"],
            )
        with gr.Row():
            lib_doc_type = gr.Dropdown(
                choices=T["lib_type_choices"]["zh"],
                value=T["lib_type_choices"]["zh"][0],
                label=T["lib_type_label"]["zh"],
                scale=2,
            )
            lib_label_input = gr.Textbox(
                label=T["lib_label_label"]["zh"],
                placeholder=T["lib_label_ph"]["zh"],
                scale=3,
            )
        with gr.Row():
            lib_add_btn_c = gr.Button(T["lib_add_btn"]["zh"], variant="secondary", size="sm")
            lib_stats_btn_c = gr.Button(T["lib_stats_btn"]["zh"], size="sm")
            lib_clear_btn_c = gr.Button(T["lib_clear_btn"]["zh"], size="sm", variant="stop")
        lib_stats_output = gr.Markdown(value=T["lib_default"]["zh"])

    with gr.Row():
        run_all_btn = gr.Button(T["run_all_btn"]["zh"], variant="primary", size="lg")
        clear_btn = gr.Button(T["clear_btn"]["zh"], size="lg")

    output_box = gr.Markdown(value=T["default_output"]["zh"])

    gr.Markdown("---")

    # ── Step-by-step ──
    step_section_md = gr.Markdown(value="### " + T["step_section"]["zh"])

    with gr.Accordion(T["acc_12"]["zh"], open=False) as acc_12:
        with gr.Row():
            step1_btn = gr.Button(T["btn_1"]["zh"])
            step2_btn = gr.Button(T["btn_2"]["zh"])

    with gr.Accordion(T["acc_34"]["zh"], open=False) as acc_34:
        with gr.Row():
            step3_btn = gr.Button(T["btn_3"]["zh"])
            step4_btn = gr.Button(T["btn_4"]["zh"])

    with gr.Accordion(T["acc_67"]["zh"], open=False) as acc_67:
        with gr.Row():
            step6_btn = gr.Button(T["btn_6"]["zh"])
            step7_btn = gr.Button(T["btn_7"]["zh"])

    # ── Usage & Privacy ──
    gr.Markdown("---")
    usage_title_md = gr.Markdown(value=T["usage_title"]["zh"])
    usage_steps_md = gr.Markdown(value=T["usage_steps"]["zh"])
    privacy_title_md = gr.Markdown(value=T["privacy_title"]["zh"])
    privacy_text_md = gr.Markdown(value=T["privacy_text"]["zh"])

    # ═════════════════════════════════════════════
    # EVENT BINDINGS
    # ═════════════════════════════════════════════

    # All components that need language updates (35 outputs)
    ui_components = [
        title_md, hero_desc_md,
        resume_label_md, resume_input, resume_file,
        jd_label_md, jd_input,
        company_label_md, company_hint,
        run_all_btn, clear_btn,
        output_box,
        step_section_md,
        acc_12, acc_34, acc_67,
        step1_btn, step2_btn, step3_btn, step4_btn, step6_btn, step7_btn,
        usage_title_md, usage_steps_md,
        privacy_title_md, privacy_text_md,
        lib_accordion, lib_file, lib_doc_type, lib_label_input,
        lib_add_btn_c, lib_stats_btn_c, lib_clear_btn_c,
        lib_stats_output,
        lang_state,
    ]

    zh_btn.click(fn=lambda: build_lang_switch("zh"), inputs=[], outputs=ui_components)
    en_btn.click(fn=lambda: build_lang_switch("en"), inputs=[], outputs=ui_components)

    # ── File Upload ──
    def handle_file_upload(file):
        if file is not None:
            from core.agent import parse_resume_file
            return parse_resume_file(file.name)
        return ""

    resume_file.change(handle_file_upload, inputs=[resume_file], outputs=[resume_input])

    # ── v2: User Library Handlers ──

    def handle_library_add(file, doc_type_str: str, label: str, lang: str):
        """向用户信息库添加文件。"""
        if file is None:
            return gr.update(value={"zh": "⚠️ 请先选择文件", "en": "⚠️ Please select a file first"}[lang])
        try:
            # Map UI selection to doc_type
            type_map_zh = {"自动检测": "", "简历": "resume", "项目文档": "project", "证书": "certificate", "其他": "other"}
            type_map_en = {"Auto-detect": "", "Resume": "resume", "Project Doc": "project", "Certificate": "certificate", "Other": "other"}
            type_map = type_map_zh if lang == "zh" else type_map_en
            override = type_map.get(doc_type_str, "")

            chunk_ids = agent.add_to_library(file.name, label=label, doc_type=override)
            return build_library_stats(lang)
        except Exception as e:
            return gr.update(value={"zh": f"❌ 添加失败: {str(e)}", "en": f"❌ Failed: {str(e)}"}[lang])

    def build_library_stats(lang: str):
        """组装信息库统计显示。"""
        try:
            stats = agent.get_library_stats()
            if stats["total_documents"] == 0:
                return gr.update(value={"zh": "📭 信息库为空。上传你的简历、项目描述、作品集等。", "en": "📭 Library is empty. Upload your resume, projects, portfolio, etc."}[lang])

            lines = [{"zh": f"## 📂 信息库状态", "en": f"## 📂 Library Status"}[lang]]
            lines.append({"zh": f"- 📄 文档数: **{stats['total_documents']}** 个", "en": f"- 📄 Documents: **{stats['total_documents']}**"}[lang])
            lines.append({"zh": f"- 🧩 分块数: **{stats['total_chunks']}** 个", "en": f"- 🧩 Chunks: **{stats['total_chunks']}**"}[lang])
            lines.append({"zh": f"- 📝 总字符数: **{stats['total_chars']:,}**", "en": f"- 📝 Total chars: **{stats['total_chars']:,}**"}[lang])
            if stats["sources"]:
                lines.append({"zh": "\n| 文档 | 类型 | 分块数 | 大小 |", "en": "\n| Document | Type | Chunks | Size |"}[lang])
                lines.append({"zh": "|------|------|--------|------|", "en": "|------|------|--------|------|"}[lang])
                for src in stats["sources"]:
                    dtype = src.get("doc_type", "?")
                    label = src.get("label", "")
                    name = f"{src['source']} ({label})" if label else src["source"]
                    lines.append(f"| {name} | {dtype} | {src['chunks']} | {src['chars']:,} |")
            return gr.update(value="\n".join(lines))
        except Exception as e:
            return gr.update(value={"zh": f"❌ 获取状态失败: {e}", "en": f"❌ Failed: {e}"}[lang])

    def handle_library_clear(lang: str):
        """清空用户信息库。"""
        count = agent.clear_library()
        if lang == "zh":
            return gr.update(value=f"✅ 已清空 {count} 个分块。信息库已重置。")
        return gr.update(value=f"✅ Cleared {count} chunks. Library reset.")

    lib_add_btn_c.click(
        handle_library_add,
        inputs=[lib_file, lib_doc_type, lib_label_input, lang_state],
        outputs=[lib_stats_output],
    )
    lib_stats_btn_c.click(
        build_library_stats,
        inputs=[lang_state],
        outputs=[lib_stats_output],
    )
    lib_clear_btn_c.click(
        handle_library_clear,
        inputs=[lang_state],
        outputs=[lib_stats_output],
    )

    # ── Run All ──
    run_all_btn.click(
        run_all_steps,
        inputs=[resume_input, jd_input, company_hint, lang_state],
        outputs=[output_box],
    )

    # ── Individual Steps ──
    step1_btn.click(step_ats_check, inputs=[resume_input, jd_input, lang_state], outputs=[output_box])
    step2_btn.click(step_match_score, inputs=[resume_input, jd_input, lang_state], outputs=[output_box])
    step3_btn.click(step_jd_analysis, inputs=[resume_input, jd_input, company_hint, lang_state], outputs=[output_box])
    step4_btn.click(step_resume_diagnosis, inputs=[resume_input, jd_input, lang_state], outputs=[output_box])
    step6_btn.click(step_learning_plan, inputs=[resume_input, jd_input, lang_state], outputs=[output_box])
    step7_btn.click(step_interview_prep, inputs=[resume_input, jd_input, company_hint, lang_state], outputs=[output_box])

    # ── Clear ──
    clear_btn.click(
        clear_all, inputs=[lang_state],
        outputs=[resume_input, jd_input, company_hint, output_box],
    )


# ═══════════════════════════════════════════════════════════
# LAUNCH
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    is_hf = os.getenv("SPACE_ID") is not None  # HuggingFace Spaces auto-sets this
    port = int(os.getenv("APP_PORT", 7860))

    print("╔══════════════════════════════════╗")
    print("║      🎯 Pleadly — Smart Job     ║")
    print("║    AI Full-Cycle Career Helper   ║")
    print("╠══════════════════════════════════╣")
    if is_hf:
        print(f"║  🌐 HF Spaces mode              ║")
    else:
        print(f"║  📡 Local: http://localhost:{port}  ║")
    print("║  🌍 中文 / English bilingual    ║")
    print("╚══════════════════════════════════╝")

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        quiet=is_hf,  # Less noisy in production
    )
