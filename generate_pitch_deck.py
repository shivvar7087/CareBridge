import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Initialize 16:9 widescreen presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors
NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
TEAL_PRIMARY = RGBColor(13, 148, 136)  # #0D9488
TEAL_LIGHT = RGBColor(20, 184, 166)    # #14B8A6
TEAL_BG = RGBColor(240, 253, 250)      # #F0FDFA
CARD_BG = RGBColor(255, 255, 255)
BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
TEXT_DARK = RGBColor(15, 37, 55)
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B
WHITE = RGBColor(255, 255, 255)
ACCENT_BLUE = RGBColor(37, 99, 235)    # #2563EB
ACCENT_RED = RGBColor(220, 38, 38)     # #DC2626
BORDER_COLOR = RGBColor(226, 232, 240) # #E2E8F0

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, eyebrow, title, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.2))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_eye = tf.paragraphs[0]
    p_eye.text = eyebrow.upper()
    p_eye.font.size = Pt(11)
    p_eye.font.bold = True
    p_eye.font.color.rgb = TEAL_PRIMARY
    
    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    
    if subtitle:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
    else:
        card.line.fill.background()
    return card

# -------------------------------------------------------------
# SLIDE 1: Title & Pitch Hook
# -------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, NAVY_DARK)

# Title accent glow bar
accent_bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(1.8), Inches(0.1))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = TEAL_LIGHT
accent_bar.line.fill.background()

t_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(4.5))
t_tf = t_box.text_frame
t_tf.word_wrap = True

p = t_tf.paragraphs[0]
p.text = "CAREBRIDGE AI"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = WHITE

p = t_tf.add_paragraph()
p.text = "Intelligent Post-Discharge Recovery & Care Coordination Platform"
p.font.size = Pt(22)
p.font.color.rgb = TEAL_LIGHT
p.space_after = Pt(20)

p = t_tf.add_paragraph()
p.text = "Bridging the critical gap between hospital discharge and healthy home recovery with multimodal AI, automated date intelligence, voice synthesis, and real-time family transparency."
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(203, 213, 225)
p.space_after = Pt(36)

p = t_tf.add_paragraph()
p.text = "🏆 PITCH DECK FOR COMPETITION JUDGES  |  LIVE URL: https://shivvar7087.github.io/CareBridge/"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = RGBColor(148, 163, 184)

# -------------------------------------------------------------
# SLIDE 2: The Problem (The $26B Post-Discharge Blindspot)
# -------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, BG_LIGHT)
add_header(s2, "THE REAL-WORLD CRISIS", "The Broken Post-Discharge Experience", "Patients leave the hospital with prescriptions in hand, but zero coordination at home.")

cards_data_s2 = [
    ("1 in 5 Patients Readmitted", "20% of discharged patients suffer preventable readmissions within 30 days, costing healthcare systems over $26 Billion annually in penalties and emergency visits.", ACCENT_RED),
    ("Clinical Jargon Overload", "Discharge paperwork is dense, fragmented, and medicalized. Over 65% of patients misunderstand medication doses, dietary warnings, or critical diagnostic dates.", ACCENT_BLUE),
    ("Caregiver Isolation", "Family members and caregivers lack real-time visibility into required reports, pending scans, or appointment shifts, creating severe coordination anxiety.", TEAL_PRIMARY)
]

for idx, (title, desc, accent) in enumerate(cards_data_s2):
    left = Inches(0.8 + idx * 4.0)
    top = Inches(2.1)
    add_card(s2, left, top, Inches(3.7), Inches(4.4))
    
    # Header block
    hbar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(3.7), Inches(0.12))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = accent
    hbar.line.fill.background()
    
    tb = s2.shapes.add_textbox(left + Inches(0.25), top + Inches(0.35), Inches(3.2), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(14)
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 3: The Solution (CareBridge AI Platform)
# -------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, BG_LIGHT)
add_header(s3, "OUR INNOVATION", "CareBridge AI: The Autonomous Post-Care Operating System", "An end-to-end bridge transforming static hospital papers into an interactive, collaborative recovery roadmap.")

sol_cards = [
    ("📄 Document AI Extraction", "Instant OCR & multimodal parsing converts physical discharge papers, test receipts, and prescriptions into structured actionable clinical milestones.", "100% Clerical Integrity"),
    ("📅 Dynamic Healthcare Journey", "A chronological timeline tracking appointments, diagnostics, and care tasks, with automated due-date calculations and 'Due Today' / 'Overdue' smart badges.", "Zero Missed Milestones"),
    ("🤝 Shared Caregiver Workspace", "Family members can view journey tasks, receive real-time notifications for overdue tasks, and complete delegated responsibilities with full audit logs.", "Transparent Collaboration"),
    ("🚨 Digital Medical ID & SOS", "An In-Case-of-Emergency (ICE) passport with blood group, allergies, active prescriptions, and one-tap emergency broadcast to all family contacts.", "Immediate Hospital Triage")
]

for idx, (head, text, tag) in enumerate(sol_cards):
    row = idx // 2
    col = idx % 2
    left = Inches(0.8 + col * 6.0)
    top = Inches(2.0 + row * 2.45)
    
    add_card(s3, left, top, Inches(5.7), Inches(2.2), CARD_BG)
    tb = s3.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), Inches(5.1), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = head
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(6)
    
    p = tf.add_paragraph()
    p.text = f"✨ IMPACT: {tag}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY

# -------------------------------------------------------------
# SLIDE 4: Core Product Highlights & "Wow" Factor
# -------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, BG_LIGHT)
add_header(s4, "USER EXPERIENCE EXCELLENCE", "Key Showcase Features Judges Love", "Built with high empathy, frictionless usability, and accessibility at its heart.")

features = [
    ("🤖 AI Health Copilot + Speech Voice Read-Out", "A floating assistant grounded exclusively in the patient's verified medical records. Features native text-to-speech voice read-out (🔊) so elderly patients can listen to instructions without squinting at text.", TEAL_PRIMARY),
    ("💊 Interactive Daily Pill Tracker & Streak (🔥)", "Interactive schedule organizing doses into Morning, Afternoon, and Evening slots with dietary advice ('Take after meal'). Tracks adherence streaks and lets users customize prescriptions on the fly.", ACCENT_BLUE),
    ("⚡ Real-Time Current Date Engine", "Backend automatically synchronizes tasks at 00:00 midnight: fires 'Task Due TODAY' notifications, sets pulsing UI indicators, and escalates overdue milestones without manual triggers.", ACCENT_RED),
    ("🔒 Clinician Oversight & Safety Lock", "CareBridge strictly flags clinician instructions. Any patient edits to medications or core orders trigger a 'Needs Clinician Verification' badge to prevent accidental self-harm.", TEAL_PRIMARY)
]

for idx, (title, desc, color) in enumerate(features):
    left = Inches(0.8 + (idx % 2) * 6.0)
    top = Inches(2.0 + (idx // 2) * 2.5)
    add_card(s4, left, top, Inches(5.7), Inches(2.25))
    
    tb = s4.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), Inches(5.1), Inches(1.85))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = color
    p.space_after = Pt(6)
    
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 5: Architecture & Technical Scalability
# -------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, BG_LIGHT)
add_header(s5, "ROBUST ENGINEERING", "Modern Full-Stack Cloud Architecture", "Engineered for high performance, modular scaling, and HIPAA-compliant data segregation.")

arch_columns = [
    ("Client Layer (Frontend)", [
        "React 18 + Vite for lightning-fast 28s production builds",
        "Recharts for interactive journey & status visualizers",
        "Lucide React iconography & custom responsive design",
        "Web Speech API for native browser audio synthesis",
        "Dual-mode API adapter (Cloud backend / local proxy)"
    ]),
    ("API & Business Layer", [
        "FastAPI (Python 3.11) with async routing & auto OpenAPI",
        "SQLAlchemy 2.0 ORM with PostgreSQL & SQLite support",
        "Pydantic v2 data validation & strict schema enforcement",
        "Automated notification deduplication & date sync triggers",
        "JWT Authentication with secure RBAC (Patient/Caregiver)"
    ]),
    ("AI & Cloud Infrastructure", [
        "Multimodal Document Intelligence (Gemini AI + OCR)",
        "Grounded Semantic Q&A Copilot Engine",
        "CI/CD: GitHub Actions auto-deploying to GitHub Pages",
        "Render Cloud Container backend deployment",
        "Zero external tracker dependencies for patient privacy"
    ])
]

for idx, (col_title, items) in enumerate(arch_columns):
    left = Inches(0.8 + idx * 4.0)
    top = Inches(2.1)
    add_card(s5, left, top, Inches(3.7), Inches(4.5))
    
    tb = s5.shapes.add_textbox(left + Inches(0.25), top + Inches(0.3), Inches(3.2), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = col_title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY
    p.space_after = Pt(12)
    
    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

# -------------------------------------------------------------
# SLIDE 6: Live Walkthrough & User Workflow
# -------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, BG_LIGHT)
add_header(s6, "SEAMLESS USER EXPERIENCE", "The 4-Step CareBridge Patient Experience", "How a discharged patient navigates from confusion to total clarity in under 3 minutes.")

steps = [
    ("Step 1: Upload & Extract", "Patient or caregiver snaps a photo of the physical discharge summary. OCR extracts diagnosis, appointments, and prescriptions automatically into verified data."),
    ("Step 2: Timeline Generated", "Tasks are pinned to a dynamic healthcare timeline with categorized pills (Appointments, Diagnostic Scans, Medication Schedules) and clear instructions."),
    ("Step 3: Real-Time Execution", "On milestone days, tasks light up with '⚡ Due Today' badges, calendar alerts trigger, and caregivers receive synchronized SMS/in-app reminders."),
    ("Step 4: Continuous Adherence", "Patient checks off daily pills, tracks their 5-day streak, uses AI Copilot for voice clarification, and accesses their ICE Emergency Card anytime.")
]

for idx, (stitle, sdesc) in enumerate(steps):
    left = Inches(0.8 + idx * 2.95)
    top = Inches(2.1)
    add_card(s6, left, top, Inches(2.8), Inches(4.5))
    
    # Step Number Badge
    nb = s6.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.25), top + Inches(0.3), Inches(0.6), Inches(0.6))
    nb.fill.solid()
    nb.fill.fore_color.rgb = TEAL_PRIMARY
    nb.line.fill.background()
    n_tf = nb.text_frame
    n_p = n_tf.paragraphs[0]
    n_p.text = str(idx + 1)
    n_p.font.size = Pt(14)
    n_p.font.bold = True
    n_p.font.color.rgb = WHITE
    n_p.alignment = PP_ALIGN.CENTER
    
    tb = s6.shapes.add_textbox(left + Inches(0.2), top + Inches(1.1), Inches(2.4), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = stitle
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(10)
    
    p = tf.add_paragraph()
    p.text = sdesc
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 7: Market Impact & Business Model
# -------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, BG_LIGHT)
add_header(s7, "MARKET OPPORTUNITY & VIABILITY", "Huge Market Need, Measurable Impact & Sound Monetization", "Positioned at the high-growth intersection of HealthTech, Post-Acute Care, and Consumer Digital Health.")

mkt_metrics = [
    ("$52B+", "Global post-acute care and patient coordination market expanding at 14.8% CAGR."),
    ("35% Cut", "Projected reduction in 30-day preventable readmissions via automated milestone tracking."),
    ("88%+", "Expected medication adherence compliance compared to standard 45% paper leaflets.")
]

for idx, (val, label) in enumerate(mkt_metrics):
    left = Inches(0.8 + idx * 4.0)
    top = Inches(2.0)
    add_card(s7, left, top, Inches(3.7), Inches(1.5), TEAL_BG, TEAL_PRIMARY)
    tb = s7.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), Inches(3.3), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = val
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY
    p = tf.add_paragraph()
    p.text = label
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

# Bottom B2B / B2C model card
add_card(s7, Inches(0.8), Inches(3.8), Inches(11.7), Inches(2.8))
tb_m = s7.shapes.add_textbox(Inches(1.1), Inches(4.0), Inches(11.1), Inches(2.4))
tf_m = tb_m.text_frame
tf_m.word_wrap = True

p = tf_m.paragraphs[0]
p.text = "Business & Go-To-Market Model"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = TEXT_DARK
p.space_after = Pt(8)

p = tf_m.add_paragraph()
p.text = "1. B2B SaaS for Hospital Networks & Insurers: Subscription per discharged patient ($12-$25). Directly saves hospitals hundreds of thousands of dollars in CMS Medicare 30-day readmission penalty fees."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED
p.space_after = Pt(6)

p = tf_m.add_paragraph()
p.text = "2. B2B2C Premium Family Caregiver Tier: Freemium app for patients; premium tier for extended family coordination, multi-patient care management, and automated pharmacy refills."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED
p.space_after = Pt(6)

p = tf_m.add_paragraph()
p.text = "3. Diagnostic Center & Pharmacy API Integrations: Revenue-sharing model for verified diagnostic report uploads and prescription delivery fulfilment."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED

# -------------------------------------------------------------
# SLIDE 8: Roadmap, Competitive Edge & The Ask
# -------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, NAVY_DARK)

tb_c = s8.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(5.8))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "THE ROAD AHEAD & CONCLUSION"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = TEAL_LIGHT
p.space_after = Pt(4)

p = tf_c.add_paragraph()
p.text = "Why CareBridge AI Wins"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(16)

p = tf_c.add_paragraph()
p.text = "•  Unrivaled Clinical Simplicity: Built for real, anxious patients—not IT engineers. Zero learning curve."
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "•  Autonomous Date Intelligence: First platform that proactively computes relative days, triggers due-today alerts, and keeps family members in sync without manual reminders."
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "•  High-Impact Roadmap: Upcoming FHIR / EHR integration (Epic, Cerner), automated WhatsApp reminder bots, and wearable vitals telemetry."
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(24)

p = tf_c.add_paragraph()
p.text = "🌐 LIVE PLATFORM DEMO: https://shivvar7087.github.io/CareBridge/"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = TEAL_LIGHT
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "Thank you, judges! We are ready for your questions."
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = WHITE

# Save presentation
output_path = "CareBridge_Pitch_Deck_8_Slides.pptx"
prs.save(output_path)
print(f"Presentation successfully saved to {output_path}")

