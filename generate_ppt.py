import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_finsight_presentation(output_path="FinSight_AI_Major_Project_Review_1.pptx"):
    prs = Presentation()
    # Set slide dimensions to 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette Constants
    NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
    NAVY_BLUE = RGBColor(30, 58, 138)     # #1E3A8A
    ACCENT_TEAL = RGBColor(13, 148, 136)  # #0D9488
    GOLD_AMBER = RGBColor(217, 119, 6)   # #D97706
    LIGHT_BG = RGBColor(248, 250, 252)    # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)     # #FFFFFF
    TEXT_DARK = RGBColor(30, 41, 59)      # #1E293B
    TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
    BORDER_COLOR = RGBColor(226, 232, 240) # #E2E8F0

    def add_background(slide, color=LIGHT_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="MAJOR PROJECT REVIEW-1"):
        # Header background banner
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = NAVY_DARK
        banner.line.fill.background()

        # Category text (small top)
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(10), Inches(0.3))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = GOLD_AMBER

        # Main title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(255, 255, 255)

        # Subtle bottom line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.1), Inches(13.333), Inches(0.05))
        line.fill.solid()
        line.fill.fore_color.rgb = GOLD_AMBER
        line.line.fill.background()

    # ----------------------------------------------------
    # SLIDE 1: Title Slide
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    add_background(slide1, color=NAVY_DARK)

    # Decorative top header box
    hdr_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.5))
    hdr_box.fill.solid()
    hdr_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    hdr_box.line.color.rgb = GOLD_AMBER
    hdr_box.line.width = Pt(1.5)

    tf = hdr_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Sri Vasavi Engineering College (Autonomous)"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Department of Artificial Intelligence & Machine Learning"
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = GOLD_AMBER
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "MAJOR PROJECT REVIEW-1"
    p3.font.size = Pt(15)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.alignment = PP_ALIGN.CENTER

    # Title Card
    title_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(11.733), Inches(1.6))
    title_card.fill.solid()
    title_card.fill.fore_color.rgb = NAVY_BLUE
    title_card.line.color.rgb = ACCENT_TEAL
    title_card.line.width = Pt(2)

    tf_tc = title_card.text_frame
    tf_tc.word_wrap = True
    p_b = tf_tc.paragraphs[0]
    p_b.text = "BATCH NO: 10"
    p_b.font.size = Pt(14)
    p_b.font.bold = True
    p_b.font.color.rgb = GOLD_AMBER
    p_b.alignment = PP_ALIGN.CENTER

    p_t = tf_tc.add_paragraph()
    p_t.text = "FinSight AI: Personalized Expense Forecasting and Financial Intelligence Using Machine Learning and Generative AI"
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = RGBColor(255, 255, 255)
    p_t.alignment = PP_ALIGN.CENTER

    # Team Table Box
    team_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.0), Inches(7.5), Inches(2.9))
    team_box.fill.solid()
    team_box.fill.fore_color.rgb = CARD_BG
    team_box.line.color.rgb = BORDER_COLOR

    tf_tb = team_box.text_frame
    tf_tb.word_wrap = True
    p_th = tf_tb.paragraphs[0]
    p_th.text = "STUDENT DETAILS"
    p_th.font.size = Pt(14)
    p_th.font.bold = True
    p_th.font.color.rgb = NAVY_DARK

    students = [
        ("1", "23A81A6134", "KUNA JYOTHI SRI LAKSHMI"),
        ("2", "23A81A6151", "PILLA JESSI DORAI RAJ"),
        ("3", "23A81A6156", "SATTI SAI RAMA KRISHNA REDDY"),
        ("4", "23A81A6138", "MATTAPARTHI KRISHNA SRI")
    ]
    for s_no, reg, name in students:
        p_s = tf_tb.add_paragraph()
        p_s.text = f"• {reg}  —  {name}"
        p_s.font.size = Pt(13)
        p_s.font.color.rgb = TEXT_DARK

    # Guide Box
    guide_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.533), Inches(4.0), Inches(4.0), Inches(2.9))
    guide_box.fill.solid()
    guide_box.fill.fore_color.rgb = CARD_BG
    guide_box.line.color.rgb = ACCENT_TEAL
    guide_box.line.width = Pt(1.5)

    tf_gb = guide_box.text_frame
    tf_gb.word_wrap = True
    p_gh = tf_gb.paragraphs[0]
    p_gh.text = "PROJECT GUIDE"
    p_gh.font.size = Pt(14)
    p_gh.font.bold = True
    p_gh.font.color.rgb = ACCENT_TEAL
    p_gh.alignment = PP_ALIGN.CENTER

    p_gn = tf_gb.add_paragraph()
    p_gn.text = "\nMr. M S N Murthy"
    p_gn.font.size = Pt(18)
    p_gn.font.bold = True
    p_gn.font.color.rgb = NAVY_DARK
    p_gn.alignment = PP_ALIGN.CENTER

    p_gd = tf_gb.add_paragraph()
    p_gd.text = "Department of AIML"
    p_gd.font.size = Pt(13)
    p_gd.font.color.rgb = TEXT_MUTED
    p_gd.alignment = PP_ALIGN.CENTER


    # ----------------------------------------------------
    # SLIDE 2: Contents
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_background(slide2)
    add_header(slide2, "TABLE OF CONTENTS")

    contents_items = [
        ("01", "Abstract", "Executive summary of FinSight AI platform"),
        ("02", "Introduction", "Background, motivation & domain overview"),
        ("03", "Literature Survey", "Comparative analysis of 5 existing research works"),
        ("04", "Problem Statement", "Key gaps & limitations in traditional systems"),
        ("05", "Objectives", "Primary goal & specific technical targets"),
        ("06", "Scope of the Project", "Core modules, features & future expansions"),
        ("07", "System Design", "Architecture pipeline, components & tech stack"),
        ("08", "Methodology", "13-step end-to-end technical implementation workflow")
    ]

    for idx, (num, title, desc) in enumerate(contents_items):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.5 + row * 1.35)

        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.15))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_n = tf_c.paragraphs[0]
        p_n.text = f"{num}. {title}"
        p_n.font.size = Pt(16)
        p_n.font.bold = True
        p_n.font.color.rgb = NAVY_BLUE

        p_d = tf_c.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED


    # ----------------------------------------------------
    # SLIDE 3: Abstract
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_background(slide3)
    add_header(slide3, "ABSTRACT")

    abstract_points = [
        ("Intelligent Personal Finance System", "FinSight AI transforms raw financial transactions into actionable, personalized financial insights for users."),
        ("Multi-Source Data Ingestion", "Accepts financial data through manual expense entries and CSV/Excel transaction file imports for centralized analysis."),
        ("Machine Learning Analytics", "Employs ML algorithms for expense categorization, anomaly detection, recurring payment detection, and predictive expense forecasting."),
        ("Pattern Recognition & Anomaly Detection", "Identifies unusual spending behavior and recurring commitments (e.g., subscriptions) relative to user spending baselines."),
        ("Financial Planning & What-If Analysis", "Provides real-time budget monitoring, savings goal tracking, and scenario-based what-if simulations for proactive planning."),
        ("Generative AI Assistant", "Integrates Llama 3.1 via Ollama to explain complex financial trends in natural language and deliver grounded financial guidance."),
        ("High Utility & Efficiency", "Dramatically reduces time and cognitive effort needed to manage personal finances, enabling an intelligent financial management experience.")
    ]

    for idx, (heading, detail) in enumerate(abstract_points):
        y = Inches(1.4 + idx * 0.8)
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(0.72))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR

        # Accent border bar on left
        bar = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.12), Inches(0.72))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT_TEAL if idx % 2 == 0 else NAVY_BLUE
        bar.line.fill.background()

        tf_ap = card.text_frame
        tf_ap.word_wrap = True
        p_ap = tf_ap.paragraphs[0]
        p_ap.text = f"{heading}: "
        p_ap.font.bold = True
        p_ap.font.size = Pt(13)
        p_ap.font.color.rgb = NAVY_DARK

        run = p_ap.add_run()
        run.text = detail
        run.font.bold = False
        run.font.size = Pt(12)
        run.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 4: Introduction
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_background(slide4)
    add_header(slide4, "INTRODUCTION")

    intro_points = [
        "Personal finance management involves tracking income, expenses, savings, budgets, and long-term financial goals.",
        "Users traditionally examine transaction records manually to understand spending habits and identify unnecessary expenditure.",
        "Existing personal finance applications mainly offer static historical reports and rigid budgeting features without predictive capabilities.",
        "FinSight AI leverages AI, Machine Learning, and financial analytics to automatically uncover actionable spending patterns.",
        "Provides automated expense classification, anomaly detection, recurring expense identification, and personalized expense forecasting.",
        "Offers interactive budget monitoring, savings goal progress analysis, and dynamic what-if simulation scenarios.",
        "Generative AI translates complex numerical analytics into concise, natural-language explanations and interactive assistant chats.",
        "Transforms conventional passive expense tracking into an active, predictive, explainable, and personalized financial intelligence platform."
    ]

    # Left Column: Key Highlight Cards
    card_left = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(3.6), Inches(5.6))
    card_left.fill.solid()
    card_left.fill.fore_color.rgb = NAVY_DARK
    card_left.line.color.rgb = GOLD_AMBER

    tf_l = card_left.text_frame
    tf_l.word_wrap = True
    p_lh = tf_l.paragraphs[0]
    p_lh.text = "CORE PILLARS"
    p_lh.font.size = Pt(16)
    p_lh.font.bold = True
    p_lh.font.color.rgb = GOLD_AMBER
    p_lh.alignment = PP_ALIGN.CENTER

    pillars = [
        ("📊 Predictive Analytics", "Machine Learning models (Random Forest, Linear Regression, LSTM) forecast future expenses."),
        ("⚠️ Anomaly Detection", "Flags unusual spending deviations from historical baseline metrics."),
        ("🤖 Generative AI", "Llama 3.1 natural language summaries & context-aware assistant.")
    ]
    for p_title, p_desc in pillars:
        p_pt = tf_l.add_paragraph()
        p_pt.text = f"\n{p_title}"
        p_pt.font.size = Pt(13)
        p_pt.font.bold = True
        p_pt.font.color.rgb = RGBColor(255, 255, 255)

        p_pd = tf_l.add_paragraph()
        p_pd.text = p_desc
        p_pd.font.size = Pt(11)
        p_pd.font.color.rgb = RGBColor(203, 213, 225)

    # Right Column: Overview Bullet Points
    for idx, point in enumerate(intro_points):
        y = Inches(1.4 + idx * 0.68)
        c_r = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), y, Inches(7.833), Inches(0.6))
        c_r.fill.solid()
        c_r.fill.fore_color.rgb = CARD_BG
        c_r.line.color.rgb = BORDER_COLOR

        tf_r = c_r.text_frame
        tf_r.word_wrap = True
        p_r = tf_r.paragraphs[0]
        p_r.text = f"• {point}"
        p_r.font.size = Pt(12)
        p_r.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 5: Literature Survey
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_background(slide5)
    add_header(slide5, "LITERATURE SURVEY")

    # Table creation
    rows = 6
    cols = 5
    left = Inches(0.6)
    top = Inches(1.35)
    width = Inches(12.133)
    height = Inches(5.7)

    table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(2.1)
    table.columns[1].width = Inches(2.7)
    table.columns[2].width = Inches(2.4)
    table.columns[3].width = Inches(2.5)
    table.columns[4].width = Inches(2.433)

    headers = ["AUTHOR & YEAR", "IMPLEMENTATION SUMMARY", "TOOL / METHOD USED", "KEY ADVANTAGES", "LIMITATION / GAPS"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = GOLD_AMBER
        p.alignment = PP_ALIGN.CENTER

    lit_data = [
        ("M. Suganya et al.",
         "AI-powered personal finance consultant for financial recommendations & literacy.",
         "Machine Learning, Llama GenAI, GAN, Investment Prediction, Ollama",
         "Combines predictive analytics with natural language explanations & recommendations.",
         "Mainly investment-focused; limited expense tracking, recurring-expense analysis & forecasting."),

        ("Niharika Shailendra et al.",
         "Personal finance tracker analyzing spending patterns and budget forecasting.",
         "Machine Learning, Spending Analysis, Budget Forecasting, Data Visualization",
         "Supports expense tracking, budgeting, spending analysis & financial awareness.",
         "Less emphasis on advanced anomaly detection, recurring-expense intelligence & granular forecasting."),

        ("Rener S. Menezes & Raimir H. Filho",
         "Studies financial transaction models under temporal data drift for changing patterns.",
         "GCN, GAT, GraphSAGE, Graph Neural Networks, Data Drift Detection",
         "Addresses dynamic transaction patterns & model robustness for financial anomaly detection.",
         "Focused primarily on fraud detection & data drift rather than personal finance management."),

        ("Wei Wang & Bo Li",
         "Financial time-series prediction using synthetic data and decomposition learning.",
         "TimeGAN, SSA, Self-Attention, Time-Series Forecasting",
         "Improves data augmentation and captures complex financial time-series patterns.",
         "Designed mainly for stock market prediction; does not cover personal expenses or budgets."),

        ("K. Ramya et al.",
         "GenAI + LSTM platform for expense tracking, investment prediction & literacy.",
         "Generative AI, LSTM, Expense Tracking, Investment Prediction",
         "Combines financial tracking, prediction, financial literacy & AI interaction.",
         "Broader investment focus; lacks personalized transaction-level expense intelligence & what-if analysis.")
    ]

    for row_idx, row_data in enumerate(lit_data, start=1):
        bg_color = CARD_BG if row_idx % 2 != 0 else RGBColor(241, 245, 249)
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_DARK
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = NAVY_BLUE


    # ----------------------------------------------------
    # SLIDE 6 & 7: Problem Statement
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_background(slide6)
    add_header(slide6, "PROBLEM STATEMENT IN EXISTING SYSTEMS")

    problems = [
        ("1. Limited Expense Understanding", "Users record expenses but traditional systems fail to explain changing spending habits. Identifying unnecessary expenses requires tedious manual effort."),
        ("2. Manual Financial Analysis", "Users must examine individual transaction records and categories manually, increasing time and effort required to extract financial insights."),
        ("3. Lack of Automatic Anomaly Detection", "Unusual transactions or sudden spending spikes are not automatically detected, leaving abnormal financial activity unnoticed."),
        ("4. Limited Recurring Expense Intelligence", "Recurring commitments (subscriptions, utility bills) are recorded as isolated transactions without systematic detection or projection."),
        ("5. Limited Expense Forecasting", "Existing software provides backward-looking historical reports with minimal support for predicting future personal expenses."),
        ("6. Limited Personalized Financial Insights", "Generic spending reports fail to adapt deeply to individual spending behaviors, income levels, or specific user financial goals."),
        ("7. Lack of Context-Aware AI Assistance", "Traditional tools lack intelligent, conversational AI assistants capable of reasoning over the user's specific transaction history."),
        ("8. Disconnected Financial Insights", "Budgets, forecasts, anomalies, and goal tracking exist in silos, forcing users to manually correlate fragmented financial data.")
    ]

    for idx, (title, desc) in enumerate(problems):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.4 + row * 1.3)

        p_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.15))
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = CARD_BG
        p_box.line.color.rgb = BORDER_COLOR

        tf_pb = p_box.text_frame
        tf_pb.word_wrap = True
        p_pt = tf_pb.paragraphs[0]
        p_pt.text = title
        p_pt.font.size = Pt(13)
        p_pt.font.bold = True
        p_pt.font.color.rgb = NAVY_BLUE

        p_pd = tf_pb.add_paragraph()
        p_pd.text = desc
        p_pd.font.size = Pt(11)
        p_pd.font.color.rgb = TEXT_DARK

    # Overall Problem Summary Box at Bottom
    op_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.8))
    op_box.fill.solid()
    op_box.fill.fore_color.rgb = NAVY_DARK
    op_box.line.color.rgb = GOLD_AMBER

    tf_op = op_box.text_frame
    tf_op.word_wrap = True
    p_oph = tf_op.paragraphs[0]
    p_oph.text = "OVERALL CORE PROBLEM: "
    p_oph.font.bold = True
    p_oph.font.size = Pt(13)
    p_oph.font.color.rgb = GOLD_AMBER

    run_op = p_oph.add_run()
    run_op.text = "Existing personal finance tools act as passive transaction trackers and static loggers. They fail to transform raw financial data into an integrated, predictive, explainable, and personalized financial intelligence experience."
    run_op.font.bold = False
    run_op.font.size = Pt(12)
    run_op.font.color.rgb = RGBColor(255, 255, 255)


    # ----------------------------------------------------
    # SLIDE 8: Objectives
    # ----------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_background(slide8)
    add_header(slide8, "PROJECT OBJECTIVES")

    # Main Objective Banner
    mo_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(1.1))
    mo_box.fill.solid()
    mo_box.fill.fore_color.rgb = NAVY_BLUE
    mo_box.line.color.rgb = ACCENT_TEAL
    mo_box.line.width = Pt(1.5)

    tf_mo = mo_box.text_frame
    tf_mo.word_wrap = True
    p_moh = tf_mo.paragraphs[0]
    p_moh.text = "MAIN OBJECTIVE"
    p_moh.font.size = Pt(13)
    p_moh.font.bold = True
    p_moh.font.color.rgb = GOLD_AMBER

    p_mot = tf_mo.add_paragraph()
    p_mot.text = "To develop an AI-powered personal finance intelligence system (FinSight AI) that converts raw financial transaction data into structured, predictive, explainable, and personalized financial insights."
    p_mot.font.size = Pt(14)
    p_mot.font.bold = True
    p_mot.font.color.rgb = RGBColor(255, 255, 255)

    # Specific Objectives Grid (6 Cards)
    spec_objs = [
        ("📥 Data Collection & Ingestion", "Collect and structure transactions via manual user entry and automated CSV/Excel file imports."),
        ("🏷️ Automated Categorization", "Classify transactions into financial categories and establish baseline spending patterns using Machine Learning."),
        ("⚠️ Anomaly & Recurring Detection", "Detect unusual spending spikes using z-scores and systematically identify recurring financial commitments."),
        ("🔮 Predictive Expense Forecasting", "Forecast upcoming expenses using historical patterns and a multi-model ML suite (Random Forest, Linear Regression, LSTM)."),
        ("📊 Budget & Goal Tracking", "Monitor active budgets against spending and evaluate feasibility of user savings goals."),
        ("🤖 Generative AI Financial Assistant", "Integrate Llama 3.1 via Ollama to provide natural-language explanations, what-if scenarios, and personalized advice.")
    ]

    for idx, (title, desc) in enumerate(spec_objs):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(2.6 + row * 1.5)

        so_card = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.35))
        so_card.fill.solid()
        so_card.fill.fore_color.rgb = CARD_BG
        so_card.line.color.rgb = BORDER_COLOR

        tf_so = so_card.text_frame
        tf_so.word_wrap = True
        p_sot = tf_so.paragraphs[0]
        p_sot.text = title
        p_sot.font.size = Pt(13)
        p_sot.font.bold = True
        p_sot.font.color.rgb = NAVY_DARK

        p_sod = tf_so.add_paragraph()
        p_sod.text = desc
        p_sod.font.size = Pt(11)
        p_sod.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 8B: Project Domain
    # ----------------------------------------------------
    slide_domain = prs.slides.add_slide(blank_layout)
    add_background(slide_domain)
    add_header(slide_domain, "PROJECT DOMAIN & MAPPING")

    # Left Column: Primary Domain Banner Box
    dom_left = slide_domain.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.4), Inches(3.6), Inches(5.6))
    dom_left.fill.solid()
    dom_left.fill.fore_color.rgb = NAVY_DARK
    dom_left.line.color.rgb = GOLD_AMBER
    dom_left.line.width = Pt(1.5)

    tf_dl = dom_left.text_frame
    tf_dl.word_wrap = True
    p_dlh = tf_dl.paragraphs[0]
    p_dlh.text = "PRIMARY DOMAIN"
    p_dlh.font.size = Pt(14)
    p_dlh.font.bold = True
    p_dlh.font.color.rgb = GOLD_AMBER
    p_dlh.alignment = PP_ALIGN.CENTER

    p_dlt = tf_dl.add_paragraph()
    p_dlt.text = "\nArtificial Intelligence\n&\nMachine Learning"
    p_dlt.font.size = Pt(20)
    p_dlt.font.bold = True
    p_dlt.font.color.rgb = RGBColor(255, 255, 255)
    p_dlt.alignment = PP_ALIGN.CENTER

    p_dls = tf_dl.add_paragraph()
    p_dls.text = "\n[ Applied FinTech & Intelligence ]"
    p_dls.font.size = Pt(12)
    p_dls.font.bold = True
    p_dls.font.color.rgb = ACCENT_TEAL
    p_dls.alignment = PP_ALIGN.CENTER

    p_dld = tf_dl.add_paragraph()
    p_dld.text = "\nIntegrates machine learning predictive analytics, statistical anomaly scoring, and context-grounded Large Language Models for automated personal finance intelligence."
    p_dld.font.size = Pt(11)
    p_dld.font.color.rgb = RGBColor(203, 213, 225)
    p_dld.alignment = PP_ALIGN.CENTER

    # Right Column: 6 Specialized Sub-domain Grid Cards
    sub_domains = [
        ("🤖 Artificial Intelligence & ML", "Predictive algorithms (Random Forest, Linear Regression, LSTM) for categorization & time-series forecasting."),
        ("💳 Personal Finance & FinTech", "Expense tracking, budget monitoring, recurring subscription detection & savings goal feasibility analysis."),
        ("📊 Financial & Baseline Analytics", "Calculates spending velocity, category distributions & statistical spending baselines for user accounts."),
        ("⚠️ Predictive & Anomaly Analytics", "Future expenditure estimation and Z-score outlier detection relative to historical spending patterns."),
        ("💬 Natural Language Processing", "Transaction description text cleaning, normalization, merchant recognition & vectorization."),
        ("🧠 Generative AI Layer", "Context-grounded natural language explanations, dynamic what-if simulation & assistant chat via Llama 3.1.")
    ]

    for idx, (d_title, d_desc) in enumerate(sub_domains):
        col = idx % 2
        row = idx // 2
        x = Inches(4.7 + col * 4.0)
        y = Inches(1.4 + row * 1.85)

        d_card = slide_domain.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.833), Inches(1.7))
        d_card.fill.solid()
        d_card.fill.fore_color.rgb = CARD_BG
        d_card.line.color.rgb = BORDER_COLOR

        tf_dc = d_card.text_frame
        tf_dc.word_wrap = True

        p_dct = tf_dc.paragraphs[0]
        p_dct.text = d_title
        p_dct.font.size = Pt(13)
        p_dct.font.bold = True
        p_dct.font.color.rgb = NAVY_BLUE

        p_dcd = tf_dc.add_paragraph()
        p_dcd.text = d_desc
        p_dcd.font.size = Pt(11)
        p_dcd.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 9: Scope of the Project
    # ----------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_background(slide9)
    add_header(slide9, "SCOPE OF THE PROJECT")


    scope_items = [
        ("Transaction Management", "Record expenses manually and import batch financial transaction records seamlessly via CSV/Excel formats.", "📥 Ingestion"),
        ("Expense Categorization & Analytics", "Automatically categorize expenses, track income vs. expenditure, and analyze category-wise spending distributions.", "📊 Analytics"),
        ("Anomaly & Recurring Intelligence", "Detect statistical anomalies relative to user baselines and identify repeated merchants & subscription commitments.", "⚠️ Detection"),
        ("Expense Forecasting & Budgeting", "Predict future month expenditure using trained ML models, track monthly budget limits, and highlight risk of overspending.", "🔮 Forecasting"),
        ("Financial Goals & What-If Analysis", "Set savings targets, evaluate goal feasibility, and simulate impact of changing recurring expenses or savings contributions.", "🎯 Planning"),
        ("Generative AI & Future Expansions", "Provide plain-language financial insights & assistant chat; extensible to receipt OCR processing and open banking API integration.", "🚀 GenAI & Future")
    ]

    for idx, (title, desc, badge) in enumerate(scope_items):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.4 + row * 1.8)

        sc_card = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.65))
        sc_card.fill.solid()
        sc_card.fill.fore_color.rgb = CARD_BG
        sc_card.line.color.rgb = BORDER_COLOR

        # Top badge line inside card
        tf_sc = sc_card.text_frame
        tf_sc.word_wrap = True

        p_b = tf_sc.paragraphs[0]
        p_b.text = badge.upper()
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = ACCENT_TEAL

        p_t = tf_sc.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY_BLUE

        p_d = tf_sc.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 9B: Functional Requirements
    # ----------------------------------------------------
    slide_func = prs.slides.add_slide(blank_layout)
    add_background(slide_func)
    add_header(slide_func, "FUNCTIONAL REQUIREMENTS")

    func_reqs = [
        ("📥 Ingestion & Preprocessing", "Accept manual expense entry & CSV/Excel file uploads; clean, validate date/amount fields, and normalize merchant names."),
        ("🏷️ ML Categorization Engine", "Classify uncategorized transactions into standard financial categories using trained TF-IDF + Random Forest models."),
        ("⚠️ Baseline & Anomaly Detection", "Calculate user spending baselines and flag statistical spending anomalies using Z-scores (Z > 2.5) and IQR metrics."),
        ("🔮 Multi-Model Forecasting", "Predict future month expenditure time-series using Random Forest, Linear Regression, and LSTM sequential models."),
        ("📊 Budgets, Goals & What-If", "Monitor category budget limits, evaluate savings goal timelines, and dynamically simulate spending/saving changes."),
        ("🤖 Grounded GenAI Assistant", "Integrate Llama 3.1 via Ollama to generate natural language explanations & conversational advisory grounded in verified metrics.")
    ]

    for idx, (title, desc) in enumerate(func_reqs):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.4 + row * 1.8)

        fr_card = slide_func.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.65))
        fr_card.fill.solid()
        fr_card.fill.fore_color.rgb = CARD_BG
        fr_card.line.color.rgb = ACCENT_TEAL
        fr_card.line.width = Pt(1.2)

        tf_fr = fr_card.text_frame
        tf_fr.word_wrap = True

        p_frt = tf_fr.paragraphs[0]
        p_frt.text = title
        p_frt.font.size = Pt(14)
        p_frt.font.bold = True
        p_frt.font.color.rgb = NAVY_BLUE

        p_frd = tf_fr.add_paragraph()
        p_frd.text = desc
        p_frd.font.size = Pt(11)
        p_frd.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 9C: Non-Functional Requirements
    # ----------------------------------------------------
    slide_nfunc = prs.slides.add_slide(blank_layout)
    add_background(slide_nfunc)
    add_header(slide_nfunc, "NON-FUNCTIONAL REQUIREMENTS")

    nfunc_reqs = [
        ("⚡ Performance & Latency", "Sub-second UI response time for dashboard charts; ML predictions & baseline calculations complete under 1.5 seconds."),
        ("🎯 Accuracy & Evaluation", "High precision and low RMSE/MAE in expense forecasting; zero false positives in baseline Z-score anomaly bounds."),
        ("🔒 Privacy & Security", "Local data storage using SQLite; no private financial transaction records transmitted to external third-party cloud servers."),
        ("🛡️ Grounding & Reliability", "Strict prompt grounding prevents GenAI hallucinations; graceful error handling for missing values and invalid file uploads."),
        ("🧩 Scalability & Usability", "Modular architecture supporting increasing user transaction logs; intuitive, responsive Streamlit dashboard interface."),
        ("🔧 Maintainability & Extensibility", "Decoupled backend API endpoints and independent ML pipelines enabling seamless future updates (OCR / Open Banking).")
    ]

    for idx, (title, desc) in enumerate(nfunc_reqs):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 5.9)
        y = Inches(1.4 + row * 1.8)

        nfr_card = slide_nfunc.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.65))
        nfr_card.fill.solid()
        nfr_card.fill.fore_color.rgb = CARD_BG
        nfr_card.line.color.rgb = GOLD_AMBER
        nfr_card.line.width = Pt(1.2)

        tf_nfr = nfr_card.text_frame
        tf_nfr.word_wrap = True

        p_nfrt = tf_nfr.paragraphs[0]
        p_nfrt.text = title
        p_nfrt.font.size = Pt(14)
        p_nfrt.font.bold = True
        p_nfrt.font.color.rgb = NAVY_DARK

        p_nfrd = tf_nfr.add_paragraph()
        p_nfrd.text = desc
        p_nfrd.font.size = Pt(11)
        p_nfrd.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 10: System Design Architecture
    # ----------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_background(slide10)
    add_header(slide10, "SYSTEM DESIGN & ARCHITECTURE")


    # Flow Stages (Horizontal 4-stage pipeline)
    stages = [
        ("1. USER INPUT", ["Manual Expense Entry", "CSV / Excel File Import", "Planned Receipt / OCR"], NAVY_DARK),
        ("2. DATA INGESTION & PROCESSING", ["Import & Format Validation", "Data Cleaning & Normalization", "Feature Engineering & Baselines"], NAVY_BLUE),
        ("3. FINANCIAL INTELLIGENCE ENGINE", ["Expense Categorization (ML)", "Anomaly Detection (Z-Score)", "Multi-Model Forecasting (RF, LR, LSTM)", "Recurring Commitment Detection"], ACCENT_TEAL),
        ("4. GENAI & INSIGHT LAYER", ["Llama 3.1 Natural Language Insights", "What-If Scenario Simulation", "Budget Monitoring & Goal Feasibility", "Context-Grounded Financial Q&A"], GOLD_AMBER)
    ]

    for idx, (stg_title, stg_bullets, stg_color) in enumerate(stages):
        x = Inches(0.6 + idx * 3.05)
        y = Inches(1.4)

        box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.95), Inches(3.6))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = stg_color
        box.line.width = Pt(1.5)

        # Header banner inside stage box
        hdr = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(2.95), Inches(0.6))
        hdr.fill.solid()
        hdr.fill.fore_color.rgb = stg_color
        hdr.line.fill.background()

        tf_h = hdr.text_frame
        tf_h.word_wrap = True
        p_h = tf_h.paragraphs[0]
        p_h.text = stg_title
        p_h.font.size = Pt(10)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(255, 255, 255)
        p_h.alignment = PP_ALIGN.CENTER

        tf_b = box.text_frame
        tf_b.word_wrap = True
        # Spacer
        tf_b.paragraphs[0].text = "\n"

        for bullet in stg_bullets:
            p_bullet = tf_b.add_paragraph()
            p_bullet.text = f"• {bullet}"
            p_bullet.font.size = Pt(10)
            p_bullet.font.color.rgb = TEXT_DARK

    # Bottom Tech Stack Bar
    tech_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.2), Inches(12.133), Inches(1.8))
    tech_box.fill.solid()
    tech_box.fill.fore_color.rgb = NAVY_DARK
    tech_box.line.color.rgb = GOLD_AMBER

    tf_tb = tech_box.text_frame
    tf_tb.word_wrap = True
    p_tbh = tf_tb.paragraphs[0]
    p_tbh.text = "TECHNOLOGY STACK ARCHITECTURE"
    p_tbh.font.size = Pt(13)
    p_tbh.font.bold = True
    p_tbh.font.color.rgb = GOLD_AMBER
    p_tbh.alignment = PP_ALIGN.CENTER

    tech_items = [
        ("Frontend & Dashboard", "Streamlit, Plotly, HTML/CSS"),
        ("Backend & REST API", "Python 3.13, FastAPI"),
        ("Machine Learning", "Scikit-learn, TensorFlow (LSTM), Joblib"),
        ("Generative AI Layer", "Ollama API, Llama 3.1 LLM"),
        ("Database & Files", "SQLite3 Database, Pandas, OpenPyXL")
    ]
    for idx, (t_name, t_detail) in enumerate(tech_items):
        col_x = Inches(0.8 + idx * 2.38)
        t_card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_x, Inches(5.7), Inches(2.25), Inches(1.1))
        t_card.fill.solid()
        t_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        t_card.line.color.rgb = BORDER_COLOR

        tf_tc = t_card.text_frame
        tf_tc.word_wrap = True
        p_tcn = tf_tc.paragraphs[0]
        p_tcn.text = t_name
        p_tcn.font.size = Pt(10)
        p_tcn.font.bold = True
        p_tcn.font.color.rgb = ACCENT_TEAL
        p_tcn.alignment = PP_ALIGN.CENTER

        p_tcd = tf_tc.add_paragraph()
        p_tcd.text = t_detail
        p_tcd.font.size = Pt(9)
        p_tcd.font.color.rgb = RGBColor(226, 232, 240)
        p_tcd.alignment = PP_ALIGN.CENTER


    # ----------------------------------------------------
    # SLIDE 11: Methodology (Part 1 - Steps 1 to 7)
    # ----------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_background(slide11)
    add_header(slide11, "METHODOLOGY (STEPS 1 TO 7)")

    m_steps_part1 = [
        ("1. Input Collection", "Accept manual transaction entries and bulk CSV/Excel financial data imports."),
        ("2. Data Preprocessing", "Clean raw data, handle missing values, standardize dates, currencies & formats."),
        ("3. Feature Engineering", "Engineered category totals, rolling averages, spending frequencies & baselines."),
        ("4. Expense Categorization", "Classify transactions into appropriate spending categories using ML classifiers."),
        ("5. Anomaly Detection", "Detect unusual transactions & sudden spikes using Z-Score statistical analysis."),
        ("6. Recurring Expense Detection", "Identify subscription payments & repeated merchants across time intervals."),
        ("7. Expense Forecasting", "Train Random Forest, Linear Regression & LSTM models to predict future expenses.")
    ]

    for idx, (title, desc) in enumerate(m_steps_part1):
        y = Inches(1.4 + idx * 0.78)
        card = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(0.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR

        num_box = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.5), Inches(0.7))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = NAVY_BLUE
        num_box.line.fill.background()

        tf_nb = num_box.text_frame
        p_nb = tf_nb.paragraphs[0]
        p_nb.text = str(idx + 1)
        p_nb.font.size = Pt(14)
        p_nb.font.bold = True
        p_nb.font.color.rgb = RGBColor(255, 255, 255)
        p_nb.alignment = PP_ALIGN.CENTER

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = f"        {title}: "
        p_ct.font.size = Pt(13)
        p_ct.font.bold = True
        p_ct.font.color.rgb = NAVY_DARK

        run = p_ct.add_run()
        run.text = desc
        run.font.size = Pt(12)
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 12: Methodology (Part 2 - Steps 8 to 13)
    # ----------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    add_background(slide12)
    add_header(slide12, "METHODOLOGY (STEPS 8 TO 13)")

    m_steps_part2 = [
        ("8. Budget & Goal Analysis", "Compare predicted expenses against budgets & evaluate goal feasibility."),
        ("9. What-If Analysis", "Simulate changes in expenses, savings, or recurring commitments to view impact."),
        ("10. Generative AI Integration", "Provide analytical context to Llama 3.1 for natural language financial explanations."),
        ("11. Backend Integration", "FastAPI / Python service connects ML models, SQLite DB & Streamlit frontend."),
        ("12. Dashboard Visualization", "Interactive Plotly visual charts for KPIs, spending trends, forecasts & alerts."),
        ("13. Model Evaluation", "Assess ML forecasting performance using RMSE, MAE, R² score & user feedback.")
    ]

    for idx, (title, desc) in enumerate(m_steps_part2, start=8):
        y = Inches(1.4 + (idx - 8) * 0.9)
        card = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(0.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR

        num_box = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.5), Inches(0.8))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = ACCENT_TEAL
        num_box.line.fill.background()

        tf_nb = num_box.text_frame
        p_nb = tf_nb.paragraphs[0]
        p_nb.text = str(idx)
        p_nb.font.size = Pt(14)
        p_nb.font.bold = True
        p_nb.font.color.rgb = RGBColor(255, 255, 255)
        p_nb.alignment = PP_ALIGN.CENTER

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = f"        {title}: "
        p_ct.font.size = Pt(13)
        p_ct.font.bold = True
        p_ct.font.color.rgb = NAVY_DARK

        run = p_ct.add_run()
        run.text = desc
        run.font.size = Pt(12)
        run.font.bold = False
        run.font.color.rgb = TEXT_DARK


    # ----------------------------------------------------
    # SLIDE 13: Questions Slide
    # ----------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    add_background(slide13, color=NAVY_DARK)

    q_card = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5))
    q_card.fill.solid()
    q_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
    q_card.line.color.rgb = GOLD_AMBER
    q_card.line.width = Pt(2)

    tf_q = q_card.text_frame
    tf_q.word_wrap = True
    p_q1 = tf_q.paragraphs[0]
    p_q1.text = "ANY QUESTIONS?"
    p_q1.font.size = Pt(36)
    p_q1.font.bold = True
    p_q1.font.color.rgb = GOLD_AMBER
    p_q1.alignment = PP_ALIGN.CENTER

    p_q2 = tf_q.add_paragraph()
    p_q2.text = "\nThank you for your time & valuable attention!\nWe welcome questions, feedback, and suggestions."
    p_q2.font.size = Pt(18)
    p_q2.font.color.rgb = RGBColor(255, 255, 255)
    p_q2.alignment = PP_ALIGN.CENTER

    p_q3 = tf_q.add_paragraph()
    p_q3.text = "\nFinSight AI — Major Project Review 1"
    p_q3.font.size = Pt(14)
    p_q3.font.color.rgb = ACCENT_TEAL
    p_q3.alignment = PP_ALIGN.CENTER


    # ----------------------------------------------------
    # SLIDE 14: Thank You
    # ----------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    add_background(slide14, color=NAVY_DARK)

    ty_card = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5))
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = NAVY_BLUE
    ty_card.line.color.rgb = ACCENT_TEAL
    ty_card.line.width = Pt(2)

    tf_ty = ty_card.text_frame
    tf_ty.word_wrap = True
    p_t1 = tf_ty.paragraphs[0]
    p_t1.text = "THANK YOU!"
    p_t1.font.size = Pt(40)
    p_t1.font.bold = True
    p_t1.font.color.rgb = RGBColor(255, 255, 255)
    p_t1.alignment = PP_ALIGN.CENTER

    p_t2 = tf_ty.add_paragraph()
    p_t2.text = "\nDepartment of Artificial Intelligence & Machine Learning\nSri Vasavi Engineering College (Autonomous)"
    p_t2.font.size = Pt(18)
    p_t2.font.bold = True
    p_t2.font.color.rgb = GOLD_AMBER
    p_t2.alignment = PP_ALIGN.CENTER

    p_t3 = tf_ty.add_paragraph()
    p_t3.text = "\nBatch No: 10 | Project Guide: Mr. M S N Murthy"
    p_t3.font.size = Pt(14)
    p_t3.font.color.rgb = RGBColor(203, 213, 225)
    p_t3.alignment = PP_ALIGN.CENTER

    # Save presentation
    try:
        prs.save(output_path)
        print(f"Presentation saved successfully to {os.path.abspath(output_path)}")
    except PermissionError:
        fallback_path = "FinSight_AI_Major_Project_Review_1_Updated.pptx"
        prs.save(fallback_path)
        print(f"Primary file was locked. Presentation saved successfully to {os.path.abspath(fallback_path)}")

if __name__ == "__main__":
    create_finsight_presentation()

