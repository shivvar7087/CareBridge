import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

os.makedirs("ppt_assets", exist_ok=True)

# -----------------------------------------------------------------
# Graphic 1: Readmission Crisis Stats Chart (Slide 2)
# -----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4.2), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')

categories = ['30-Day\nReadmission', 'Medication\nErrors', 'Missed\nFollow-ups', 'Uninformed\nCaregivers']
percentages = [20, 65, 42, 78]
bar_colors = ['#DC2626', '#EA580C', '#D97706', '#2563EB']

bars = ax.bar(categories, percentages, color=bar_colors, width=0.55, edgecolor='none', zorder=3)
ax.set_ylim(0, 95)
ax.set_ylabel('Percentage Affected (%)', fontsize=11, fontweight='bold', color='#1E293B')
ax.set_title('The Post-Discharge Breakdown Problem', fontsize=13, fontweight='bold', color='#0F172A', pad=14)
ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#CBD5E1')
ax.spines['bottom'].set_color('#CBD5E1')
ax.tick_params(axis='both', colors='#475569', labelsize=10)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f"{int(yval)}%", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#0F172A')

plt.tight_layout()
plt.savefig("ppt_assets/chart_crisis.png", bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

# -----------------------------------------------------------------
# Graphic 2: Solution Architecture Flow (Slide 3)
# -----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 3.8), dpi=200)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')
ax.axis('off')

# Draw 4 sequential flow blocks
steps = [
    ("1. CLINICAL INPUT", "Paper Discharge\nSummary / Prescriptions", "#0F2537", "#38BDF8"),
    ("2. MULTIMODAL AI", "OCR Parsing &\nClinical Validation", "#0D9488", "#5EEAD4"),
    ("3. TIMELINE ENGINE", "Automated Actionable\nJourney Milestones", "#2563EB", "#93C5FD"),
    ("4. SYNC & ALERTS", "Caregiver Sharing,\nPill Adherence & SOS", "#059669", "#A7F3D0")
]

for i, (title, desc, bg, accent) in enumerate(steps):
    x = 0.05 + i * 0.24
    rect = plt.Rectangle((x, 0.2), 0.20, 0.6, transform=ax.transAxes, facecolor=bg, edgecolor=accent, linewidth=2, zorder=2)
    ax.add_patch(rect)
    ax.text(x + 0.10, 0.66, title, transform=ax.transAxes, ha='center', va='center', fontsize=8.5, fontweight='bold', color=accent)
    ax.text(x + 0.10, 0.44, desc, transform=ax.transAxes, ha='center', va='center', fontsize=8, color='#FFFFFF', multialignment='center')
    
    if i < 3:
        ax.annotate('', xy=(x + 0.235, 0.5), xytext=(x + 0.205, 0.5), xycoords='axes fraction',
                    arrowprops=dict(arrowstyle="->", color='#0D9488', lw=2.5))

plt.tight_layout()
plt.savefig("ppt_assets/diagram_solution.png", bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

# -----------------------------------------------------------------
# Graphic 3: Features Showcase Mockup (Slide 4)
# -----------------------------------------------------------------
img = Image.new('RGB', (1200, 700), color='#F8FAFC')
draw = ImageDraw.Draw(img)

# Card 1: AI Copilot
draw.rounded_rectangle([40, 40, 580, 320], radius=16, fill='#FFFFFF', outline='#E2E8F0', width=2)
draw.rounded_rectangle([60, 60, 260, 95], radius=8, fill='#0D9488')
draw.text((75, 70), "CAREBRIDGE AI COPILOT", fill='#FFFFFF')
draw.text((60, 115), "Question: When is my cardiology follow-up?", fill='#0F2537')
draw.rounded_rectangle([60, 145, 560, 240], radius=10, fill='#F0FDFA', outline='#CCFBF1', width=1)
draw.text((75, 160), "AI Answer: In 7 days (Harborview Medical Centre).\nVoice Synthesis: Active [Audio Read-Aloud 🔊]\nConfidence: Grounded in discharge summary", fill='#0F766E')
draw.rounded_rectangle([60, 260, 200, 295], radius=20, fill='#0D9488')
draw.text((80, 270), "Read Aloud 🔊", fill='#FFFFFF')

# Card 2: Medication Adherence & Streak
draw.rounded_rectangle([620, 40, 1160, 320], radius=16, fill='#FFFFFF', outline='#E2E8F0', width=2)
draw.rounded_rectangle([640, 60, 840, 95], radius=8, fill='#EA580C')
draw.text((655, 70), "DAILY PILL TRACKER", fill='#FFFFFF')
draw.rounded_rectangle([1000, 60, 1140, 95], radius=20, fill='#FFF7ED', outline='#FFEDD5', width=1)
draw.text((1015, 70), "🔥 5-DAY STREAK", fill='#EA580C')
draw.text((640, 120), "• Aspirin 75mg - Morning (08:00 AM)  [✓ TAKEN]", fill='#059669')
draw.text((640, 160), "• Metformin 500mg - Afternoon (01:30 PM)  [✓ TAKEN]", fill='#059669')
draw.text((640, 200), "• Atorvastatin 20mg - Evening (08:00 PM)  [PENDING]", fill='#D97706')
draw.rounded_rectangle([640, 250, 1140, 270], radius=6, fill='#E2E8F0')
draw.rounded_rectangle([640, 250, 990, 270], radius=6, fill='#0D9488')
draw.text((640, 280), "Today's Adherence: 67% (2 of 3 doses completed)", fill='#64748B')

# Card 3: Emergency Passport
draw.rounded_rectangle([40, 360, 1160, 660], radius=16, fill='#FFFFFF', outline='#EF4444', width=2)
draw.rounded_rectangle([60, 380, 320, 415], radius=8, fill='#EF4444')
draw.text((75, 390), "IN-CASE-OF-EMERGENCY (ICE)", fill='#FFFFFF')
draw.rounded_rectangle([960, 380, 1140, 415], radius=10, fill='#FEF2F2', outline='#FECACA', width=1)
draw.text((980, 390), "BLOOD: B+ POSITIVE", fill='#DC2626')
draw.text((60, 435), "Patient: Aarav Mehta  |  DOB: 15 Jun 1988  |  Phone: +91 98100 23456", fill='#0F2537')
draw.text((60, 470), "Known Allergies: Penicillin (Moderate rash), NSAIDs", fill='#DC2626')
draw.text((60, 505), "Hospital: Harborview Medical Centre  |  Emergency Helpline: +91 11 2658 8500", fill='#0F766E')
draw.text((60, 540), "Connected Caregivers: Priya Mehta (+91 98765 43210), Rohan Mehta", fill='#2563EB')
draw.rounded_rectangle([60, 580, 360, 625], radius=10, fill='#DC2626')
draw.text((85, 595), "🚨 ONE-TOUCH SOS BROADCAST", fill='#FFFFFF')

img.save("ppt_assets/mockup_features.png")

# -------------------------------------------------------------
# Graphic 4: Tech Stack Layer (Slide 5)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')
ax.axis('off')

layers = [
    ("USER EXPERIENCE", "React 18  ·  Vite  ·  Recharts  ·  Web Speech Audio API", "#0D9488"),
    ("APPLICATION SERVICES", "FastAPI (Python 3.11)  ·  SQLAlchemy  ·  Pydantic v2", "#0F2537"),
    ("INTELLIGENCE & OCR", "Multimodal Gemini API  ·  Contextual Copilot  ·  Audit Engine", "#2563EB"),
    ("SECURITY & CLOUD", "Role-Based Access (RBAC)  ·  GitHub Actions CI/CD  ·  Render", "#475569")
]

for i, (l_title, l_desc, color) in enumerate(layers):
    y = 0.76 - i * 0.22
    rect = plt.Rectangle((0.05, y), 0.9, 0.18, transform=ax.transAxes, facecolor='#FFFFFF', edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(0.10, y + 0.11, l_title, transform=ax.transAxes, fontsize=10, fontweight='bold', color=color)
    ax.text(0.10, y + 0.04, l_desc, transform=ax.transAxes, fontsize=8.5, color='#334155')

plt.tight_layout()
plt.savefig("ppt_assets/diagram_tech.png", bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

# -------------------------------------------------------------
# Graphic 5: Market & Clinical Impact Graph (Slide 7)
# -------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(6.2, 4.0), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax1.set_facecolor('#F8FAFC')

years = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
market_size = [12, 18, 27, 39, 52]   # $B
adherence = [50, 65, 78, 85, 92]     # %

color = '#0D9488'
ax1.set_xlabel('Commercial Horizon', fontsize=11, fontweight='bold', color='#1E293B')
ax1.set_ylabel('Target Market Size ($B)', color=color, fontsize=11, fontweight='bold')
bars = ax1.bar(years, market_size, color=color, alpha=0.7, width=0.45, label='Market Expansion ($B)')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = '#2563EB'
ax2.set_ylabel('Medication Adherence (%)', color=color, fontsize=11, fontweight='bold')
line = ax2.plot(years, adherence, color=color, marker='o', linewidth=3, label='Adherence Rate (%)')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(40, 100)

plt.title('Market Growth & Projected Clinical Adherence', fontsize=12, fontweight='bold', color='#0F172A', pad=12)
plt.tight_layout()
plt.savefig("ppt_assets/chart_market.png", bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

print("All visual assets created successfully in ppt_assets/")

