import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path="CareBridge_AI_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Professional Healthcare Palette
    C_NAVY_DARK = RGBColor(15, 37, 55)     # #0F2537 Deep Healthcare Navy
    C_NAVY_MED  = RGBColor(26, 54, 76)     # #1A364C Medium Navy
    C_TEAL      = RGBColor(13, 148, 136)   # #0D9488 Vibrant Medical Teal
    C_TEAL_DARK = RGBColor(15, 118, 110)   # #0F766E Deep Teal
    C_TEAL_PALE = RGBColor(240, 253, 250)  # #F0FDFA Very Pale Teal Background
    C_TEAL_LIGHT= RGBColor(204, 251, 241)  # #CCFBF1 Teal Badge
    C_SLATE_50  = RGBColor(248, 250, 252)  # #F8FAFC Crisp Slide Background
    C_WHITE     = RGBColor(255, 255, 255)  # Card White
    C_BORDER    = RGBColor(226, 232, 240)  # #E2E8F0 Card Border
    C_BORDER_TEAL= RGBColor(153, 246, 228) # #99F6E4 Subtle Teal Border
    C_TEXT_DARK = RGBColor(15, 23, 42)     # #0F172A Primary Slate Text
    C_TEXT_MUTED= RGBColor(100, 116, 139)  # #64748B Secondary Text
    C_AMBER     = RGBColor(217, 119, 6)    # #D97706 Warning/Highlight Amber
    C_AMBER_PALE= RGBColor(254, 243, 199)  # #FEF3C7 Amber Background
    C_BLUE_PALE = RGBColor(238, 242, 255)  # #EEF2FF Indigo/Blue Pale
    C_BLUE      = RGBColor(37, 99, 235)    # #2563EB Blue Accent
    C_EMERALD   = RGBColor(16, 185, 129)   # #10B981 Green Success
    C_EMERALD_PALE = RGBColor(236, 253, 245)

    FONT_FAMILY = "Segoe UI"

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, kicker, title, subtitle=None):
        # Header Container
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Kicker / Category tag
        p_kicker = tf.paragraphs[0]
        p_kicker.text = kicker.upper()
        p_kicker.font.name = FONT_FAMILY
        p_kicker.font.size = Pt(10)
        p_kicker.font.bold = True
        p_kicker.font.color.rgb = C_TEAL
        p_kicker.space_after = Pt(2)

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = FONT_FAMILY
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_DARK
        p_title.space_after = Pt(2)

        # Subtitle
        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = FONT_FAMILY
            p_sub.font.size = Pt(11)
            p_sub.font.color.rgb = C_TEXT_MUTED

    def add_footer(slide, current_page, total_pages=9):
        # Footer dividing line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.fill.background()

        # Footer Text
        fbox = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(9.0), Inches(0.35))
        tf = fbox.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = "CAREBRIDGE AI (MEDICARE)  |  POST-DISCHARGE HEALTHCARE JOURNEY COORDINATION PLATFORM"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MUTED

        # Page Number
        pbox = slide.shapes.add_textbox(Inches(10.0), Inches(7.05), Inches(2.533), Inches(0.35))
        tf2 = pbox.text_frame
        tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.RIGHT
        p2.text = f"PAGE {current_page} OF {total_pages}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(8.5)
        p2.font.bold = True
        p2.font.color.rgb = C_TEAL

    def create_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_BORDER, radius=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: HERO / TITLE SLIDE (Dark Navy Premium Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, C_NAVY_DARK)

    # Accent decorative banner top
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_TEAL
    top_bar.line.fill.background()

    # Brand pill badge
    pill1 = create_card(s1, Inches(0.9), Inches(0.9), Inches(3.2), Inches(0.38), bg_color=RGBColor(20, 60, 85), border_color=C_TEAL)
    tf_p = pill1.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_p.paragraphs[0]
    p.text = "● HEALTH-TECH INNOVATION MVP"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(94, 234, 212) # Teal bright

    # Main Title Box
    t_box = s1.shapes.add_textbox(Inches(0.9), Inches(1.4), Inches(11.5), Inches(2.2))
    tf_title = t_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = 0

    p_h1 = tf_title.paragraphs[0]
    p_h1.text = "CareBridge AI"
    p_h1.font.name = FONT_FAMILY
    p_h1.font.size = Pt(44)
    p_h1.font.bold = True
    p_h1.font.color.rgb = C_WHITE
    p_h1.space_after = Pt(8)

    p_sub = tf_title.add_paragraph()
    p_sub.text = "Intelligent Post-Discharge Journey & Caregiver Coordination Platform"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = RGBColor(153, 246, 228)
    p_sub.space_after = Pt(10)

    p_desc = tf_title.add_paragraph()
    p_desc.text = "Bridging the critical post-hospitalization recovery gap by transforming dense clinical discharge summaries into verified, actionable task journeys, shared safely with family caregivers."
    p_desc.font.name = FONT_FAMILY
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = RGBColor(203, 213, 225)

    # 3 Feature Highlight Cards in Dark Theme
    highlights = [
        ("Structured AI Ingestion", "Securely parses discharge PDFs & images with PyMuPDF/Tesseract and extracts actionable milestones into editable drafts.", RGBColor(13, 148, 136)),
        ("Patient-in-the-Loop Safety", "Zero unverified AI actions. Strict clinical boundaries ensure every recommendation requires patient review before becoming a task.", RGBColor(37, 99, 235)),
        ("Granular Caregiver Sharing", "Caregivers accept invitations to assist on specific non-clinical tasks while keeping confidential health records private.", RGBColor(16, 185, 129))
    ]

    card_w = Inches(3.64)
    card_gap = Inches(0.39)
    for i, (htitle, hdesc, border_c) in enumerate(highlights):
        c_left = Inches(0.9) + i * (card_w + card_gap)
        c = create_card(s1, c_left, Inches(4.0), card_w, Inches(2.3), bg_color=C_NAVY_MED, border_color=border_c)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = ctf.margin_top = Inches(0.25)
        
        # Pill inside card
        cp = ctf.paragraphs[0]
        cp.text = f"FEATURE {i+1:02d}"
        cp.font.name = FONT_FAMILY
        cp.font.size = Pt(9)
        cp.font.bold = True
        cp.font.color.rgb = RGBColor(153, 246, 228)
        cp.space_after = Pt(4)

        cp2 = ctf.add_paragraph()
        cp2.text = htitle
        cp2.font.name = FONT_FAMILY
        cp2.font.size = Pt(14)
        cp2.font.bold = True
        cp2.font.color.rgb = C_WHITE
        cp2.space_after = Pt(6)

        cp3 = ctf.add_paragraph()
        cp3.text = hdesc
        cp3.font.name = FONT_FAMILY
        cp3.font.size = Pt(10.5)
        cp3.font.color.rgb = RGBColor(203, 213, 225)

    # Slide 1 Footer Info Bar
    fbar = s1.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(11.533), Inches(0.5))
    ftf = fbar.text_frame
    ftf.margin_left = ftf.margin_top = 0
    fp = ftf.paragraphs[0]
    fp.text = "STACK: FastAPI (Python 3.12)  •  React 18 & Vite  •  SQLAlchemy / PostgreSQL  •  OpenAI Structured API  •  Tailwind CSS"
    fp.font.name = FONT_FAMILY
    fp.font.size = Pt(9.5)
    fp.font.bold = True
    fp.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: THE PROBLEM STATEMENT & CLINICAL CONTEXT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, C_SLATE_50)
    add_header(s2, "01 / Clinical Context & Problem Statement", 
               "The Post-Discharge Care Gap & Coordination Breakdown",
               "Patients transition from intensive hospital care to solitary home recovery without structured guidance.")
    add_footer(s2, 2)

    # Left Column: 3 Problem Breakdown Cards
    prob_w = Inches(7.2)
    prob_items = [
        ("Dense, Overwhelming Discharge Paperwork",
         "Discharge summaries are multi-page documents filled with complex clinical jargon, nested medication regimens, and conditional instructions that confuse patients and families.",
         C_NAVY_DARK),
        ("Caregiver Isolation & Blindspot Handoffs",
         "Informal family caregivers deliver 80%+ of home recovery support but lack direct visibility into the care plan, creating miscommunication, missed doses, and caregiver burnout.",
         C_NAVY_DARK),
        ("Administrative Ambiguity Mistaken for Clinical Readiness",
         "Patients struggle to differentiate between medical clearance and administrative document readiness (e.g. pending biopsy reports, insurance clearances, and discharge summaries).",
         C_NAVY_DARK)
    ]

    card_top = Inches(1.85)
    for i, (title, desc, tc) in enumerate(prob_items):
        card = create_card(s2, Inches(0.8), card_top + i * Inches(1.58), prob_w, Inches(1.42), bg_color=C_WHITE, border_color=C_BORDER)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.18)

        cp = ctf.paragraphs[0]
        cp.text = f"CHALLENGE 0{i+1} : {title}"
        cp.font.name = FONT_FAMILY
        cp.font.size = Pt(11.5)
        cp.font.bold = True
        cp.font.color.rgb = C_NAVY_DARK
        cp.space_after = Pt(4)

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.name = FONT_FAMILY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = C_TEXT_MUTED

    # Right Column: Key Real-World Metrics / Impact
    right_left = Inches(8.3)
    right_w = Inches(4.233)
    
    stat_card = create_card(s2, right_left, Inches(1.85), right_w, Inches(4.86), bg_color=C_WHITE, border_color=C_BORDER_TEAL)
    stf = stat_card.text_frame
    stf.word_wrap = True
    stf.margin_left = stf.margin_right = Inches(0.3)
    stf.margin_top = Inches(0.25)

    sp_title = stf.paragraphs[0]
    sp_title.text = "REAL-WORLD IMPACT AT A GLANCE"
    sp_title.font.name = FONT_FAMILY
    sp_title.font.size = Pt(11)
    sp_title.font.bold = True
    sp_title.font.color.rgb = C_TEAL
    sp_title.space_after = Pt(12)

    stats = [
        ("1 in 5", "Patients experience an adverse medical event (adverse drug reaction or readmission) within 30 days of discharge."),
        ("50%+", "Of discharge instructions are forgotten or immediately misunderstood by patients without written reminders."),
        ("$26B+", "Annual cost of preventable 30-day hospital readmissions across healthcare systems due to coordination failure.")
    ]

    for num, expl in stats:
        p_num = stf.add_paragraph()
        p_num.text = num
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(24)
        p_num.font.bold = True
        p_num.font.color.rgb = C_TEAL_DARK

        p_expl = stf.add_paragraph()
        p_expl.text = expl
        p_expl.font.name = FONT_FAMILY
        p_expl.font.size = Pt(10)
        p_expl.font.color.rgb = C_TEXT_MUTED
        p_expl.space_after = Pt(10)

    # =========================================================================
    # SLIDE 3: THE CAREGIVER-CENTERED SOLUTION & CORE PRINCIPLES
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, C_SLATE_50)
    add_header(s3, "02 / The Solution & Product Philosophy", 
               "CareBridge AI: The Coordinated Recovery Bridge",
               "Empowering recovering individuals and their care circles through intelligent workflows and rigorous safety.")
    add_footer(s3, 3)

    # 3 Solution Pillar Cards
    pillars = [
        ("1. Intelligent Document Parser",
         "Ingests discharge documents (PDF/images), extracting actionable clinical instructions, follow-up appointments, and needed diagnostic tests into clear, structured draft items.",
         "PyMuPDF + Tesseract + OpenAI JSON", C_BLUE_PALE, C_BLUE),
        ("2. Patient-in-the-Loop Review",
         "AI proposes, but the patient decides. Every suggested task is linked back to its exact source context. Zero unverified actions enter the active care schedule.",
         "Defensive Human Validation Gate", C_TEAL_PALE, C_TEAL_DARK),
        ("3. Role-Isolated Caregiver Circles",
         "Patients securely invite family caregivers and delegate specific tasks (e.g. pharmacy pickup, transport) without exposing sensitive clinical notes or history.",
         "Zero-Trust Scoped Collaboration", C_EMERALD_PALE, C_EMERALD)
    ]

    col_w = Inches(3.64)
    col_gap = Inches(0.4)
    for i, (ptitle, pbody, pbadge, pbg, pbc) in enumerate(pillars):
        c_left = Inches(0.8) + i * (col_w + col_gap)
        c = create_card(s3, c_left, Inches(1.85), col_w, Inches(3.2), bg_color=C_WHITE, border_color=C_BORDER)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.25)

        # Pill badge
        p_bdg = ctf.paragraphs[0]
        p_bdg.text = f"PILLAR {i+1}"
        p_bdg.font.name = FONT_FAMILY
        p_bdg.font.size = Pt(9)
        p_bdg.font.bold = True
        p_bdg.font.color.rgb = pbc
        p_bdg.space_after = Pt(4)

        p_t = ctf.add_paragraph()
        p_t.text = ptitle
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_NAVY_DARK
        p_t.space_after = Pt(8)

        p_b = ctf.add_paragraph()
        p_b.text = pbody
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = C_TEXT_MUTED
        p_b.space_after = Pt(12)

        p_tag = ctf.add_paragraph()
        p_tag.text = f"✓ {pbadge}"
        p_tag.font.name = FONT_FAMILY
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = pbc

    # Bottom Safety & Clinical Boundary Alert Card
    alert_card = create_card(s3, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.45), bg_color=C_AMBER_PALE, border_color=C_AMBER)
    atf = alert_card.text_frame
    atf.word_wrap = True
    atf.margin_left = atf.margin_right = Inches(0.3)
    atf.margin_top = Inches(0.18)

    ap1 = atf.paragraphs[0]
    ap1.text = "⚠️ CLINICAL SAFETY PRINCIPLE & STRICT REGULATORY BOUNDARY"
    ap1.font.name = FONT_FAMILY
    ap1.font.size = Pt(11)
    ap1.font.bold = True
    ap1.font.color.rgb = C_AMBER
    ap1.space_after = Pt(4)

    ap2 = atf.add_paragraph()
    ap2.text = "CareBridge AI is exclusively a coordination, tracking, and communication workspace. It DOES NOT provide medical diagnoses, prescribe drugs, modify physician orders, or replace licensed clinicians. AI suggestions remain strictly provisional drafts until verified. When operated without an AI key, the system runs in a clearly labeled simulated demo mode that never hallucinates instructions."
    ap2.font.name = FONT_FAMILY
    ap2.font.size = Pt(10)
    ap2.font.color.rgb = RGBColor(120, 53, 15)

    # =========================================================================
    # SLIDE 4: PRODUCT CAPABILITIES & FEATURE MATRIX
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, C_SLATE_50)
    add_header(s4, "03 / Functional Ecosystem & Core Features", 
               "Comprehensive Feature Matrix for Care Delivery",
               "Every module is engineered to give patients complete oversight and caregivers actionable focus.")
    add_footer(s4, 4)

    # 6 Feature Cards (2 Rows of 3)
    features = [
        ("Smart Document Vault", "Supports PDF, JPEG, and PNG uploads with MIME/magic-byte checks and a 10MB ceiling. Previews are restricted to authenticated owners.", "SECURE VAULT"),
        ("Interactive Journey Timeline", "Chronological milestone view of medications, follow-up clinics, wound dressings, and lifestyle tasks with real-time status toggles.", "PATIENT TIMELINE"),
        ("Caregiver Circle Management", "One-click email invitation system. Caregivers receive isolated dashboard access showing only assigned tasks, with full history logs.", "ROLE-SCOPED SHARING"),
        ("Administrative Report Tracker", "Checklist tracking availability of discharge summaries, lab results, and biopsy reports. Distinguishes administrative state from medical clearance.", "REPORT READINESS"),
        ("Access Barrier Journal", "Records practical obstacles (transportation, financial hardship, pharmacy out-of-stock) with dedicated status tracking and follow-up notes.", "SDOH TRACKING"),
        ("Audit Logs & In-App Alerts", "Deduplicated in-app notification engine reminding users of upcoming tasks, accompanied by comprehensive audit logs for sensitive actions.", "COMPLIANCE & AUDIT")
    ]

    grid_w = Inches(3.64)
    grid_h = Inches(2.2)
    col_gap = Inches(0.4)
    row_gap = Inches(0.25)
    start_top = Inches(1.85)

    for idx, (ftitle, fdesc, ftag) in enumerate(features):
        r = idx // 3
        c = idx % 3
        c_left = Inches(0.8) + c * (grid_w + col_gap)
        c_top = start_top + r * (grid_h + row_gap)

        card = create_card(s4, c_left, c_top, grid_w, grid_h, bg_color=C_WHITE, border_color=C_BORDER)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.18)

        cp1 = ctf.paragraphs[0]
        cp1.text = ftag
        cp1.font.name = FONT_FAMILY
        cp1.font.size = Pt(8.5)
        cp1.font.bold = True
        cp1.font.color.rgb = C_TEAL
        cp1.space_after = Pt(2)

        cp2 = ctf.add_paragraph()
        cp2.text = ftitle
        cp2.font.name = FONT_FAMILY
        cp2.font.size = Pt(12)
        cp2.font.bold = True
        cp2.font.color.rgb = C_NAVY_DARK
        cp2.space_after = Pt(4)

        cp3 = ctf.add_paragraph()
        cp3.text = fdesc
        cp3.font.name = FONT_FAMILY
        cp3.font.size = Pt(9.5)
        cp3.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 5: USER EXPERIENCE & END-TO-END WORKFLOW
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_SLATE_50)
    add_header(s5, "04 / User Journey & Operational Workflow", 
               "5-Stage Flow: From Discharge Paper to Coordinated Action",
               "A transparent human-in-the-loop pipeline ensuring safety, clarity, and shared responsibility.")
    add_footer(s5, 5)

    # 5 Horizontal Process Steps
    steps = [
        ("01", "Upload & Consent", "Patient uploads paper summary (PDF/Image) and grants explicit AI processing consent."),
        ("02", "Extraction Draft", "Backend OCR & LLM parse medical instructions into structured, provisional task drafts."),
        ("03", "Human Review", "Patient verifies each draft against source text, confirming or discarding proposed tasks."),
        ("04", "Caregiver Sharing", "Patient invites family and delegates non-clinical tasks (e.g. Rx pickup, grocery)."),
        ("05", "Track & Recover", "Caregiver completes tasks, patient monitors timeline progress, and logs barriers if stuck.")
    ]

    step_w = Inches(2.18)
    step_gap = Inches(0.2)
    step_top = Inches(1.85)

    for i, (num, stitle, sdesc) in enumerate(steps):
        s_left = Inches(0.8) + i * (step_w + step_gap)
        scard = create_card(s5, s_left, step_top, step_w, Inches(2.85), bg_color=C_WHITE, border_color=C_BORDER_TEAL)
        stf = scard.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = Inches(0.18)
        stf.margin_top = Inches(0.2)

        p_num = stf.paragraphs[0]
        p_num.text = f"STEP {num}"
        p_num.font.name = FONT_FAMILY
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = C_TEAL
        p_num.space_after = Pt(4)

        p_st = stf.add_paragraph()
        p_st.text = stitle
        p_st.font.name = FONT_FAMILY
        p_st.font.size = Pt(12)
        p_st.font.bold = True
        p_st.font.color.rgb = C_NAVY_DARK
        p_st.space_after = Pt(6)

        p_sd = stf.add_paragraph()
        p_sd.text = sdesc
        p_sd.font.name = FONT_FAMILY
        p_sd.font.size = Pt(9.5)
        p_sd.font.color.rgb = C_TEXT_MUTED

    # Bottom Two Comparison Cards: Role Boundary Comparison
    b_top = Inches(4.9)
    b_w = Inches(5.66)

    # Left: Patient Experience
    p_card = create_card(s5, Inches(0.8), b_top, b_w, Inches(1.8), bg_color=C_TEAL_PALE, border_color=C_TEAL)
    ptf = p_card.text_frame
    ptf.word_wrap = True
    ptf.margin_left = ptf.margin_right = Inches(0.25)
    ptf.margin_top = Inches(0.15)
    
    pp1 = ptf.paragraphs[0]
    pp1.text = "👤 PATIENT ROLE EXPERIENCE (FULL MASTERY)"
    pp1.font.name = FONT_FAMILY
    pp1.font.size = Pt(11)
    pp1.font.bold = True
    pp1.font.color.rgb = C_TEAL_DARK
    pp1.space_after = Pt(4)

    pp2 = ptf.add_paragraph()
    pp2.text = "• Owns entire recovery timeline, personal profile, and uploaded medical documents.\n• Grants explicit consent for OCR / AI processing on each document.\n• Sole authority to approve draft tasks and invite caregivers to share duties."
    pp2.font.name = FONT_FAMILY
    pp2.font.size = Pt(9.5)
    pp2.font.color.rgb = C_TEXT_DARK

    # Right: Caregiver Experience
    c_card = create_card(s5, Inches(6.866), b_top, b_w, Inches(1.8), bg_color=C_BLUE_PALE, border_color=C_BLUE)
    ctf = c_card.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_right = Inches(0.25)
    ctf.margin_top = Inches(0.15)

    cp1 = ctf.paragraphs[0]
    cp1.text = "👥 CAREGIVER ROLE EXPERIENCE (RESTRICTED COLLABORATION)"
    cp1.font.name = FONT_FAMILY
    cp1.font.size = Pt(11)
    cp1.font.bold = True
    cp1.font.color.rgb = C_BLUE
    cp1.space_after = Pt(4)

    cp2 = ctf.add_paragraph()
    cp2.text = "• Accesses app only via an authenticated invitation token from the patient.\n• Sees ONLY tasks explicitly assigned to them in the shared care journey.\n• Can update completion status, but CANNOT alter clinician instruction wording or access unshared records."
    cp2.font.name = FONT_FAMILY
    cp2.font.size = Pt(9.5)
    cp2.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 6: TECHNICAL ARCHITECTURE & FULL-STACK IMPLEMENTATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_SLATE_50)
    add_header(s6, "05 / System Design & Technical Architecture", 
               "Modern, Resilient Full-Stack Architecture",
               "Engineered with modular separation of concerns, defensive security, and scalable cloud readiness.")
    add_footer(s6, 6)

    # 3 Architectural Tier Columns
    col_w = Inches(3.64)
    col_gap = Inches(0.4)

    tiers = [
        ("CLIENT TIER", "React 18 Single-Page App",
         [("React 18 + Vite", "Blazing-fast build toolchain & reactive state management"),
          ("Tailwind CSS", "Modern responsive design system with clean healthcare aesthetics"),
          ("React Router 6", "Protected role-based routing (Patient vs Caregiver views)"),
          ("Recharts Visuals", "Interactive progress donuts, recovery velocity, and status metrics"),
          ("Axios Interceptors", "Automatic JWT bearer token injection & error handling")],
         C_BLUE_PALE, C_BLUE),
        ("API TIER", "FastAPI Asynchronous Backend",
         [("FastAPI (Python 3.12)", "High-performance async REST API with auto OpenAPI docs"),
          ("Pydantic v2", "Strict schema validation and type-safe request/response contracts"),
          ("JWT Authentication", "Stateless bearer tokens with scrypt cryptographic password hashing"),
          ("Modular Routing", "Separated routes: /auth, /journey, /tasks, /documents, /reports"),
          ("Security Scoping", "Ownership enforcement on every DB query to prevent IDOR leaks")],
         C_TEAL_PALE, C_TEAL_DARK),
        ("DATA & AI TIER", "SQLAlchemy ORM & LLM Adapter",
         [("SQLAlchemy 2.0", "Database abstraction supporting local SQLite and cloud PostgreSQL"),
          ("Alembic Migrations", "Controlled, declarative schema evolution for production deployment"),
          ("PyMuPDF & Tesseract", "Text extraction for digital PDFs and optional OCR for scanned images"),
          ("OpenAI-Compatible LLM", "Server-side structured JSON schema extraction (Zero API key leak)"),
          ("Simulated Fallback", "Deterministic offline demo mode when no AI API key is configured")],
         C_EMERALD_PALE, C_EMERALD)
    ]

    for i, (thead, tsub, tbullets, tbg, tbc) in enumerate(tiers):
        c_left = Inches(0.8) + i * (col_w + col_gap)
        card = create_card(s6, c_left, Inches(1.85), col_w, Inches(4.85), bg_color=C_WHITE, border_color=C_BORDER)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.2)

        p1 = ctf.paragraphs[0]
        p1.text = thead
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = tbc
        p1.space_after = Pt(2)

        p2 = ctf.add_paragraph()
        p2.text = tsub
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = C_NAVY_DARK
        p2.space_after = Pt(10)

        for btitle, bdesc in tbullets:
            pb = ctf.add_paragraph()
            pb.text = f"• {btitle}: "
            pb.font.name = FONT_FAMILY
            pb.font.size = Pt(9.5)
            pb.font.bold = True
            pb.font.color.rgb = C_NAVY_DARK

            pb_sub = ctf.add_paragraph()
            pb_sub.text = f"   {bdesc}"
            pb_sub.font.name = FONT_FAMILY
            pb_sub.font.size = Pt(9)
            pb_sub.font.color.rgb = C_TEXT_MUTED
            pb_sub.space_after = Pt(4)

    # =========================================================================
    # SLIDE 7: SECURITY, PRIVACY & COMPLIANCE SAFEGUARDS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_SLATE_50)
    add_header(s7, "06 / Data Protection & Responsible Design", 
               "Healthcare-Grade Security & Defensive Architecture",
               "Built from the ground up prioritizing patient privacy, auditability, and clinical risk mitigation.")
    add_footer(s7, 7)

    # 4 Security Pillars (2x2 Grid)
    sec_cards = [
        ("Strict Multi-Tenant Scoping & Zero-Trust RBAC",
         "Every database query explicitly binds the authenticated user ID. Caregivers can only see and update tasks explicitly assigned to them in a shared journey. Direct object reference (IDOR) attacks are completely eliminated at the query layer.",
         "RBAC & ISOLATION", C_TEAL),
        ("Human-in-the-Loop Clinical Verification",
         "AI models are strictly treated as assistive drafting engines. Extracted instructions remain marked as 'Needs Verification' and are never added to active care schedules without explicit patient sign-off. Clinical text cannot be altered by caregivers.",
         "CLINICAL SAFETY", C_BLUE),
        ("Defensive File Upload & Storage Sanitation",
         "Uploaded discharge files undergo rigorous multi-point validation: file extension checks, declared MIME type validation, magic-byte header inspection, and a 10MB size ceiling. Uploads are stored outside public web roots with authenticated streaming.",
         "STORAGE HARDENING", C_EMERALD),
        ("Privacy Compliance & Comprehensive Audit Logging",
         "Engineered with data minimization principles aligned with India's DPDP Act and HIPAA best practices. Sensitive events—including file previews, task reassignments, and caregiver link activations—are recorded in an immutable audit log.",
         "AUDIT & PRIVACY", C_AMBER)
    ]

    sw_w = Inches(5.66)
    sw_h = Inches(2.25)
    for idx, (stitle, sbody, stag, scolor) in enumerate(sec_cards):
        r = idx // 2
        c = idx % 2
        s_left = Inches(0.8) + c * (sw_w + Inches(0.4))
        s_top = Inches(1.85) + r * (sw_h + Inches(0.25))

        scard = create_card(s7, s_left, s_top, sw_w, sw_h, bg_color=C_WHITE, border_color=C_BORDER)
        stf = scard.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = Inches(0.28)
        stf.margin_top = Inches(0.2)

        sp1 = stf.paragraphs[0]
        sp1.text = stag
        sp1.font.name = FONT_FAMILY
        sp1.font.size = Pt(9)
        sp1.font.bold = True
        sp1.font.color.rgb = scolor
        sp1.space_after = Pt(3)

        sp2 = stf.add_paragraph()
        sp2.text = stitle
        sp2.font.name = FONT_FAMILY
        sp2.font.size = Pt(12.5)
        sp2.font.bold = True
        sp2.font.color.rgb = C_NAVY_DARK
        sp2.space_after = Pt(6)

        sp3 = stf.add_paragraph()
        sp3.text = sbody
        sp3.font.name = FONT_FAMILY
        sp3.font.size = Pt(9.5)
        sp3.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 8: TESTING, VERIFICATION & DEMO READINESS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_SLATE_50)
    add_header(s8, "07 / Quality Assurance & Validation", 
               "Rigorous Test Coverage & Functional Demonstration",
               "Every layer of the platform is validated with automated testing suites and seeded demo personas.")
    add_footer(s8, 8)

    # 3 Stat Cards on top
    stat_w = Inches(3.64)
    stat_gap = Inches(0.4)
    metrics = [
        ("14 / 14", "BACKEND SUITE", "API unit & integration tests passing 100% with unittest runner."),
        ("100%", "BUILD HEALTH", "Vite production build passes with zero linting or bundling errors."),
        ("3 PERSONAS", "READY-TO-TEST DEMO", "Pre-seeded fictional patient and caregiver accounts for live evaluation.")
    ]

    for i, (mbig, mtag, msub) in enumerate(metrics):
        c_left = Inches(0.8) + i * (stat_w + stat_gap)
        c = create_card(s8, c_left, Inches(1.85), stat_w, Inches(1.4), bg_color=C_WHITE, border_color=C_BORDER_TEAL)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.18)

        p1 = ctf.paragraphs[0]
        p1.text = mtag
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = C_TEAL
        p1.space_after = Pt(2)

        p2 = ctf.add_paragraph()
        p2.text = mbig
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = C_NAVY_DARK
        p2.space_after = Pt(2)

        p3 = ctf.add_paragraph()
        p3.text = msub
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(9)
        p3.font.color.rgb = C_TEXT_MUTED

    # 2 Lower Cards: Detailed Test Scope & Seeded Demo Accounts
    low_w = Inches(5.66)
    low_h = Inches(3.2)
    low_top = Inches(3.5)

    # Left: Test Scope Details
    tc = create_card(s8, Inches(0.8), low_top, low_w, low_h, bg_color=C_WHITE, border_color=C_BORDER)
    ttf = tc.text_frame
    ttf.word_wrap = True
    ttf.margin_left = ttf.margin_right = Inches(0.28)
    ttf.margin_top = Inches(0.2)

    tp1 = ttf.paragraphs[0]
    tp1.text = "AUTOMATED TEST COVERAGE BREAKDOWN"
    tp1.font.name = FONT_FAMILY
    tp1.font.size = Pt(11)
    tp1.font.bold = True
    tp1.font.color.rgb = C_TEAL_DARK
    tp1.space_after = Pt(6)

    test_points = [
        ("Authentication & RBAC", "Verifies JWT issuance, password hashing, and role permission validation."),
        ("Tenant Isolation & Scoping", "Ensures patients cannot access or mutate records belonging to other users."),
        ("Upload Validation & Security", "Confirms rejection of oversized files, mismatched MIME types, and spoofed extensions."),
        ("Report Availability vs Clearance", "Validates that document availability checks do not trigger clinical clearance."),
        ("CORS & Schema Migration", "Tests preflight checks and backwards-compatible legacy SQLite migration paths.")
    ]

    for t_head, t_det in test_points:
        tp = ttf.add_paragraph()
        tp.text = f"✔ {t_head}: "
        tp.font.name = FONT_FAMILY
        tp.font.size = Pt(9.5)
        tp.font.bold = True
        tp.font.color.rgb = C_NAVY_DARK

        tp_det = ttf.add_paragraph()
        tp_det.text = f"   {t_det}"
        tp_det.font.name = FONT_FAMILY
        tp_det.font.size = Pt(9)
        tp_det.font.color.rgb = C_TEXT_MUTED
        tp_det.space_after = Pt(2)

    # Right: Seeded Demo Environment
    dc = create_card(s8, Inches(6.866), low_top, low_w, low_h, bg_color=C_WHITE, border_color=C_BORDER)
    dtf = dc.text_frame
    dtf.word_wrap = True
    dtf.margin_left = dtf.margin_right = Inches(0.28)
    dtf.margin_top = Inches(0.2)

    dp1 = dtf.paragraphs[0]
    dp1.text = "OUT-OF-THE-BOX SEEDED DEMO WORKSPACE"
    dp1.font.name = FONT_FAMILY
    dp1.font.size = Pt(11)
    dp1.font.bold = True
    dp1.font.color.rgb = C_BLUE
    dp1.space_after = Pt(6)

    demo_points = [
        ("Primary Patient Account", "demo@carebridge.ai (Pass: carebridge123) — Complete dashboard with active journey timeline, uploaded test summaries, and barrier records."),
        ("Linked Caregiver 1", "priya.demo@carebridge.ai (Pass: carebridge123) — Fictional family caregiver with assigned medication pickup and transportation tasks."),
        ("Linked Caregiver 2", "rohan.demo@carebridge.ai (Pass: carebridge123) — Demonstrates independent caregiver assignment view with isolated permissions."),
        ("Offline Safe Execution", "Runs completely without external API charges using deterministic simulated AI drafts and local SQLite storage.")
    ]

    for d_head, d_det in demo_points:
        dp = dtf.add_paragraph()
        dp.text = f"★ {d_head}: "
        dp.font.name = FONT_FAMILY
        dp.font.size = Pt(9.5)
        dp.font.bold = True
        dp.font.color.rgb = C_NAVY_DARK

        dp_det = dtf.add_paragraph()
        dp_det.text = f"   {d_det}"
        dp_det.font.name = FONT_FAMILY
        dp_det.font.size = Pt(9)
        dp_det.font.color.rgb = C_TEXT_MUTED
        dp_det.space_after = Pt(3)

    # =========================================================================
    # SLIDE 9: STRATEGIC ROADMAP & CONCLUSION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_SLATE_50)
    add_header(s9, "08 / Production Scaling & Future Horizon", 
               "Strategic Roadmap & Evolution Pathway",
               "Charting the transition from successful MVP to scalable enterprise healthcare infrastructure.")
    add_footer(s9, 9)

    # 4 Horizon Cards
    horizons = [
        ("PHASE 1", "Enterprise Cloud & Storage", 
         "Migrate local file storage to private AWS S3 / Cloud Object Storage with presigned time-limited URLs; deploy managed PostgreSQL on AWS RDS or Render with automatic failover.",
         C_BLUE_PALE, C_BLUE),
        ("PHASE 2", "Health Interoperability", 
         "Implement HL7 / FHIR standard export pipelines to synchronize care plans with hospital electronic health records (EHRs) and India's Ayushman Bharat Digital Mission (ABDM).",
         C_TEAL_PALE, C_TEAL_DARK),
        ("PHASE 3", "Multi-Channel Engagement", 
         "Integrate automated WhatsApp Business API and SMS nudges for medication adherence alarms, appointment reminders, and one-tap status updates for non-tech-savvy users.",
         C_EMERALD_PALE, C_EMERALD),
        ("PHASE 4", "Scanned OCR & Multilingual", 
         "Deploy robust computer-vision OCR for crumpled, low-contrast, and handwritten discharge slips; offer automated multi-language translation in regional languages (Hindi, etc.).",
         C_AMBER_PALE, C_AMBER)
    ]

    h_w = Inches(2.72)
    h_gap = Inches(0.28)
    h_top = Inches(1.85)

    for i, (hphase, htitle, hdesc, hbg, hbc) in enumerate(horizons):
        c_left = Inches(0.8) + i * (h_w + h_gap)
        c = create_card(s9, c_left, h_top, h_w, Inches(3.2), bg_color=C_WHITE, border_color=C_BORDER)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.2)
        ctf.margin_top = Inches(0.2)

        hp1 = ctf.paragraphs[0]
        hp1.text = hphase
        hp1.font.name = FONT_FAMILY
        hp1.font.size = Pt(8.5)
        hp1.font.bold = True
        hp1.font.color.rgb = hbc
        hp1.space_after = Pt(2)

        hp2 = ctf.add_paragraph()
        hp2.text = htitle
        hp2.font.name = FONT_FAMILY
        hp2.font.size = Pt(12)
        hp2.font.bold = True
        hp2.font.color.rgb = C_NAVY_DARK
        hp2.space_after = Pt(8)

        hp3 = ctf.add_paragraph()
        hp3.text = hdesc
        hp3.font.name = FONT_FAMILY
        hp3.font.size = Pt(9.5)
        hp3.font.color.rgb = C_TEXT_MUTED

    # Bottom Takeaway Card (Dark Navy Accent Banner)
    bot_card = create_card(s9, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.45), bg_color=C_NAVY_DARK, border_color=None)
    btf = bot_card.text_frame
    btf.word_wrap = True
    btf.margin_left = btf.margin_right = Inches(0.35)
    btf.margin_top = Inches(0.2)

    bp1 = btf.paragraphs[0]
    bp1.text = "CONCLUSION & CORE VALUE PROPOSITION"
    bp1.font.name = FONT_FAMILY
    bp1.font.size = Pt(10)
    bp1.font.bold = True
    bp1.font.color.rgb = RGBColor(153, 246, 228)
    bp1.space_after = Pt(4)

    bp2 = btf.add_paragraph()
    bp2.text = "CareBridge AI fundamentally bridges the vulnerable post-hospitalization discharge window. By combining AI-assisted structured extraction with mandatory human verification and privacy-scoped caregiver collaboration, CareBridge AI turns discharge confusion into clear, shared, and confident recovery."
    bp2.font.name = FONT_FAMILY
    bp2.font.size = Pt(11)
    bp2.font.color.rgb = C_WHITE

    # Save presentation
    prs.save(output_path)
    print(f"Presentation successfully created and saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    out_file = "CareBridge_AI_Presentation.pptx"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_presentation(out_file)

