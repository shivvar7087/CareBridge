import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Professional Color Palette
NAVY_HERO = RGBColor(11, 25, 44)      # #0B192C
TEAL_PRIMARY = RGBColor(13, 148, 136)  # #0D9488
TEAL_ACCENT = RGBColor(20, 184, 166)   # #14B8A6
BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
CARD_BG = RGBColor(255, 255, 255)
TEXT_DARK = RGBColor(15, 23, 42)       # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B
WHITE = RGBColor(255, 255, 255)
ACCENT_BLUE = RGBColor(37, 99, 235)
ACCENT_RED = RGBColor(220, 38, 38)
BORDER_COLOR = RGBColor(226, 232, 240)

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, eyebrow, title, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(1.2))
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
        p_sub.font.size = Pt(12.5)
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

# =============================================================================
# SLIDE 1: Title & Vision (Hero Dark Theme)
# =============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, NAVY_HERO)

# Decorative Teal Stripe
top_bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(1.8), Inches(0.08))
top_bar.fill.solid()
top_bar.fill.fore_color.rgb = TEAL_ACCENT
top_bar.line.fill.background()

t_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(8.5), Inches(4.5))
t_tf = t_box.text_frame
t_tf.word_wrap = True

p = t_tf.paragraphs[0]
p.text = "CAREBRIDGE AI"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = WHITE

p = t_tf.add_paragraph()
p.text = "Autonomous Post-Discharge Healthcare Coordination Operating System"
p.font.size = Pt(20)
p.font.color.rgb = TEAL_ACCENT
p.space_after = Pt(20)

p = t_tf.add_paragraph()
p.text = "Bridging the critical gap between hospital discharge and healthy home recovery with multimodal document intelligence, autonomous date tracking, voice speech synthesis, and real-time family transparency."
p.font.size = Pt(13.5)
p.font.color.rgb = RGBColor(203, 213, 225)
p.space_after = Pt(36)

p = t_tf.add_paragraph()
p.text = "🏆 PITCH DECK FOR HACKATHON & INVESTOR JUDGES"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = RGBColor(148, 163, 184)

# Live Badge on Slide 1 Right Side
add_card(s1, Inches(9.4), Inches(2.3), Inches(3.1), Inches(3.8), RGBColor(15, 37, 55), TEAL_PRIMARY)
b_box = s1.shapes.add_textbox(Inches(9.6), Inches(2.5), Inches(2.7), Inches(3.4))
b_tf = b_box.text_frame
b_tf.word_wrap = True

p = b_tf.paragraphs[0]
p.text = "LIVE SYSTEM DEMO"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT
p.space_after = Pt(14)

p = b_tf.add_paragraph()
p.text = "• Fully Deployed App:\n  https://shivvar7087.github.io/CareBridge/\n\n• Backend API:\n  Render Cloud Platform\n\n• Stack:\n  React 18 + FastAPI + Gemini AI"
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(226, 232, 240)

# =============================================================================
# SLIDE 2: The Problem (With Crisis Breakdown Chart)
# =============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, BG_LIGHT)
add_header(s2, "THE REAL-WORLD CRISIS", "The Broken Post-Discharge Experience", "Patients leave the hospital with prescriptions in hand, but zero coordination at home.")

# Left Column: Problem Cards
add_card(s2, Inches(0.8), Inches(2.0), Inches(5.8), Inches(4.7))
tb2 = s2.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.3), Inches(4.3))
tf2 = tb2.text_frame
tf2.word_wrap = True

p = tf2.paragraphs[0]
p.text = "Why Patients Relapse After Hospital Discharge"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEXT_DARK
p.space_after = Pt(14)

p = tf2.add_paragraph()
p.text = "1. The $26B Readmission Drain: 1 in 5 patients (20%) are readmitted within 30 days due to completely avoidable lapses in recovery coordination."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED
p.space_after = Pt(12)

p = tf2.add_paragraph()
p.text = "2. Dense Medical Jargon: Over 65% of patients leave confused by illegible discharge papers, multi-drug dosing schedules, and dietary restrictions."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED
p.space_after = Pt(12)

p = tf2.add_paragraph()
p.text = "3. Caregiver Disconnection: Family caregivers are overwhelmed without a single shared source of truth, missing critical diagnostic reports."
p.font.size = Pt(12)
p.font.color.rgb = TEXT_MUTED

# Right Column: Chart Image
if os.path.exists("ppt_assets/chart_crisis.png"):
    s2.shapes.add_picture("ppt_assets/chart_crisis.png", Inches(6.9), Inches(2.0), width=Inches(5.6))

# =============================================================================
# SLIDE 3: The Solution (With Solution Flow Diagram)
# =============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, BG_LIGHT)
add_header(s3, "OUR INNOVATION", "CareBridge AI: The Autonomous Post-Care Operating System", "A multi-modal platform transforming dense clinical papers into an interactive, tracked recovery journey.")

# Top Half: Solution Architecture Graphic
if os.path.exists("ppt_assets/diagram_solution.png"):
    s3.shapes.add_picture("ppt_assets/diagram_solution.png", Inches(0.8), Inches(1.9), width=Inches(11.7))

# Bottom Half: Key Solution Pillars
sol_pillars = [
    ("Instant OCR & Parsing", "Extracts appointments, medications, required tests, and warnings directly from photos of clinical notes.", TEAL_PRIMARY),
    ("Autonomous Timeline", "Creates dynamic tasks with date intelligence, highlighting 'Due Today' and escalating 'Overdue' items.", ACCENT_BLUE),
    ("Caregiver Transparency", "Allows family members to coordinate care, track reports, and share tasks with full audit trail.", ACCENT_RED),
]

for idx, (head, text, color) in enumerate(sol_pillars):
    left = Inches(0.8 + idx * 4.0)
    top = Inches(4.7)
    add_card(s3, left, top, Inches(3.7), Inches(2.2))
    
    tb = s3.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), Inches(3.2), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = head
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = color
    p.space_after = Pt(6)
    
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 4: Core Product Showcase (With High-Resolution Mockup)
# =============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, BG_LIGHT)
add_header(s4, "USER EXPERIENCE EXCELLENCE", "Key Showcase Features Judges Love", "Built with high empathy, accessibility, and real-time medical utility.")

# Left Half: Feature Bullets
add_card(s4, Inches(0.8), Inches(1.9), Inches(4.8), Inches(5.0))
tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(4.4), Inches(4.6))
tf4 = tb4.text_frame
tf4.word_wrap = True

p = tf4.paragraphs[0]
p.text = "Features That Stand Out:"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEXT_DARK
p.space_after = Pt(10)

features_txt = [
    ("🤖 Voice AI Health Copilot", "Context-aware chat grounded in verified discharge data. Features one-click Audio Read-Aloud (🔊) for elderly accessibility."),
    ("💊 Daily Pill Tracker & Streak", "Interactive Morning, Afternoon, Evening pill schedule with food notes, custom dosage manager, and 🔥 5-day streak."),
    ("🚨 Digital Emergency Card (ICE)", "Triage passport displaying Blood Group, Allergies, Attending Clinician, and one-tap Caregiver SOS Broadcast."),
    ("⚡ Real-Time Relative Date Engine", "Backend auto-detects today's date, lighting up '⚡ Due Today' indicators and firing instant reminders.")
]

for title, desc in features_txt:
    p = tf4.add_paragraph()
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY
    
    p = tf4.add_paragraph()
    p.text = desc
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(6)

# Right Half: Image Mockup
if os.path.exists("ppt_assets/mockup_features.png"):
    s4.shapes.add_picture("ppt_assets/mockup_features.png", Inches(5.8), Inches(1.9), width=Inches(6.7))

# =============================================================================
# SLIDE 5: Architecture & Tech Stack (With Architecture Layer Diagram)
# =============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, BG_LIGHT)
add_header(s5, "ROBUST ENGINEERING", "Modern Full-Stack Cloud Architecture", "Designed for clinical data integrity, zero latency, and HIPAA-compliant data boundaries.")

# Left Half: Tech Details
add_card(s5, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.0))
tb5 = s5.shapes.add_textbox(Inches(1.05), Inches(2.1), Inches(5.3), Inches(4.6))
tf5 = tb5.text_frame
tf5.word_wrap = True

p = tf5.paragraphs[0]
p.text = "Production-Grade Tech Choices"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEXT_DARK
p.space_after = Pt(12)

stack_points = [
    ("Frontend Performance", "React 18 + Vite delivering a 28s lightning production build, Recharts for timeline data viz, and Web Speech API."),
    ("Backend API Reliability", "FastAPI (Python 3.11) with async routing, automatic OpenAPI validation, and SQLAlchemy 2.0 ORM."),
    ("AI & Semantic Intelligence", "Multimodal Gemini API for unstructured clinical documents with robust rule-based fallback for 100% uptime."),
    ("DevOps & CI/CD", "Automated GitHub Actions CI/CD deploying frontend to GitHub Pages and backend to Render Cloud Container.")
]

for title, desc in stack_points:
    p = tf5.add_paragraph()
    p.text = f"•  {title}:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY
    
    p = tf5.add_paragraph()
    p.text = desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(8)

# Right Half: Tech Diagram Image
if os.path.exists("ppt_assets/diagram_tech.png"):
    s5.shapes.add_picture("ppt_assets/diagram_tech.png", Inches(6.9), Inches(1.9), width=Inches(5.6))

# =============================================================================
# SLIDE 6: 4-Step User Workflow
# =============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, BG_LIGHT)
add_header(s6, "SEAMLESS USER EXPERIENCE", "The 4-Step CareBridge Patient Experience", "How a discharged patient navigates from confusion to total clarity in under 3 minutes.")

steps = [
    ("Step 1: Upload & Extract", "Patient or caregiver snaps a photo of the clinical discharge summary. AI OCR extracts diagnosis, appointments, and prescriptions in seconds."),
    ("Step 2: Timeline Generated", "Tasks are pinned to a dynamic healthcare timeline with categorized pills (Appointments, Diagnostic Scans, Medication Schedules)."),
    ("Step 3: Real-Time Execution", "On milestone days, tasks light up with '⚡ Due Today' badges, calendar alerts trigger, and caregivers receive synchronized notifications."),
    ("Step 4: Continuous Adherence", "Patient tracks daily pills, maintains their 5-day streak, uses AI Copilot for voice clarification, and accesses their ICE Emergency Card.")
]

for idx, (stitle, sdesc) in enumerate(steps):
    left = Inches(0.8 + idx * 2.95)
    top = Inches(2.0)
    add_card(s6, left, top, Inches(2.8), Inches(4.7))
    
    # Step Number Badge
    nb = s6.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.25), top + Inches(0.35), Inches(0.65), Inches(0.65))
    nb.fill.solid()
    nb.fill.fore_color.rgb = TEAL_PRIMARY
    nb.line.fill.background()
    n_tf = nb.text_frame
    n_p = n_tf.paragraphs[0]
    n_p.text = str(idx + 1)
    n_p.font.size = Pt(15)
    n_p.font.bold = True
    n_p.font.color.rgb = WHITE
    n_p.alignment = PP_ALIGN.CENTER
    
    tb = s6.shapes.add_textbox(left + Inches(0.2), top + Inches(1.2), Inches(2.4), Inches(3.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = stitle
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(10)
    
    p = tf.add_paragraph()
    p.text = sdesc
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 7: Market Opportunity & Business Model (With Graph)
# =============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, BG_LIGHT)
add_header(s7, "MARKET OPPORTUNITY & VIABILITY", "Huge Market Need, Measurable Impact & Sound Monetization", "Positioned at the high-growth intersection of HealthTech, Post-Acute Care, and Consumer Digital Health.")

# Left Half: Chart Image
if os.path.exists("ppt_assets/chart_market.png"):
    s7.shapes.add_picture("ppt_assets/chart_market.png", Inches(0.8), Inches(2.0), width=Inches(5.6))

# Right Half: Business Model Card
add_card(s7, Inches(6.7), Inches(2.0), Inches(5.8), Inches(4.8))
tb7 = s7.shapes.add_textbox(Inches(6.95), Inches(2.2), Inches(5.3), Inches(4.4))
tf7 = tb7.text_frame
tf7.word_wrap = True

p = tf7.paragraphs[0]
p.text = "Commercialization & Unit Economics"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = TEXT_DARK
p.space_after = Pt(12)

biz_points = [
    ("B2B SaaS for Hospitals", "Subscription per discharged patient ($15-$30). Directly protects hospitals from CMS 30-day readmission penalty fines (up to 3% of total Medicare revenue)."),
    ("B2B2C Premium Family Tier", "Freemium for basic care; $9.99/mo for multi-caregiver coordination, pharmacy auto-refills, and long-term health record archival."),
    ("Diagnostic & Pharmacy APIs", "Revenue sharing with lab chains (Pathology/Radiology) for direct digital report delivery and prescription fulfillment.")
]

for title, desc in biz_points:
    p = tf7.add_paragraph()
    p.text = f"•  {title}:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_PRIMARY
    
    p = tf7.add_paragraph()
    p.text = desc
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(8)

# =============================================================================
# SLIDE 8: Roadmap & Closing (Hero Dark Theme)
# =============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, NAVY_HERO)

tb_c = s8.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(6.0))
tf_c = tb_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "THE ROAD AHEAD & CONCLUSION"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT
p.space_after = Pt(4)

p = tf_c.add_paragraph()
p.text = "Why CareBridge AI Wins"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.space_after = Pt(16)

p = tf_c.add_paragraph()
p.text = "•  Unrivaled Clinical Simplicity: Built for anxious patients and caring families—not IT technicians. Zero learning curve."
p.font.size = Pt(13.5)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "•  Autonomous Date Intelligence: First platform that proactively computes relative days, triggers due-today alerts, and keeps family members in sync without manual reminders."
p.font.size = Pt(13.5)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "•  Aggressive Scale Roadmap: Upcoming FHIR / EHR integration (Epic, Cerner), automated WhatsApp reminder bots, and wearable vitals sync."
p.font.size = Pt(13.5)
p.font.color.rgb = RGBColor(226, 232, 240)
p.space_after = Pt(24)

p = tf_c.add_paragraph()
p.text = "🌐 LIVE PLATFORM: https://shivvar7087.github.io/CareBridge/"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT
p.space_after = Pt(8)

p = tf_c.add_paragraph()
p.text = "Thank you, judges! We welcome your questions."
p.font.size = Pt(19)
p.font.bold = True
p.font.color.rgb = WHITE

# Save PPTX
output_path = "CareBridge_AI_Judge_Pitch_Deck.pptx"
prs.save(output_path)
print(f"Presentation successfully updated with images at {output_path}")
