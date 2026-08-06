# =====================================================
# DRIVE – Dengue Risk Intelligence & Visualization Engine
# Version 3.0 (Bioluminescent Abyss Edition)
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import os
import json
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from streamlit_folium import st_folium
import plotly.express as px

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch

from utils import classify_risk_4level

# =====================================================
# FIX: Make sure Python looks in the SAME FOLDER as dashboard.py
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="DRIVE – Bioluminescent Abyss",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CSS – THE BIOLUMINESCENT ABYSS (SIGNATURE DESIGN)
# =====================================================

st.markdown("""
<style>
/* ----- FONTS & ICONS ----- */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800;900&family=JetBrains+Mono:wght@300;400;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

/* ----- RESET & BASE (Deep Abyss) ----- */
html, body, .stApp {
    background: #060A12 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow-x: hidden;
}
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0B1A2A 0%, #060A12 70%) !important;
}

/* ---- BIO-LUMINESCENT PARTICLES (CSS Only) ---- */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20px 30px, #00F0FF, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 40px 70px, #A855F7, rgba(0,0,0,0)),
        radial-gradient(3px 3px at 120px 200px, #2DD4BF, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 90px 40px, #00F0FF, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 300px 500px, #A855F7, rgba(0,0,0,0)),
        radial-gradient(3px 3px at 600px 100px, #2DD4BF, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 800px 300px, #00F0FF, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 400px 700px, #A855F7, rgba(0,0,0,0));
    background-size: 200px 200px;
    background-repeat: repeat;
    opacity: 0.4;
    pointer-events: none;
    z-index: 0;
    animation: driftParticles 30s linear infinite;
}
@keyframes driftParticles {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-50px, -30px) scale(1.2); }
}

/* ---- PULSING SONAR (Hero Background) ---- */
section.main > div {
    position: relative;
    z-index: 2;
}
section.main::before {
    content: '';
    position: fixed;
    top: 25%;
    left: 50%;
    width: 80vmin;
    height: 80vmin;
    transform: translate(-50%, -50%);
    border: 1px solid rgba(0, 240, 255, 0.08);
    border-radius: 50%;
    box-shadow: 0 0 60px rgba(0, 240, 255, 0.05), inset 0 0 60px rgba(0, 240, 255, 0.02);
    animation: sonarPulse 4s ease-out infinite;
    pointer-events: none;
    z-index: 0;
}
section.main::after {
    content: '';
    position: fixed;
    top: 25%;
    left: 50%;
    width: 60vmin;
    height: 60vmin;
    transform: translate(-50%, -50%);
    border: 1px solid rgba(168, 85, 247, 0.05);
    border-radius: 50%;
    animation: sonarPulse 4s ease-out 2s infinite;
    pointer-events: none;
    z-index: 0;
}
@keyframes sonarPulse {
    0% { opacity: 1; transform: translate(-50%, -50%) scale(0.5); }
    100% { opacity: 0; transform: translate(-50%, -50%) scale(1.8); }
}

/* ----- LAYOUT & GLASS (Holographic Panels) ----- */
section.main > div {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 24px !important;
}

.glass-hero {
    background: rgba(6, 10, 18, 0.65) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 40px !important;
    padding: 40px 20px !important;
    margin: 20px 0 40px !important;
    text-align: center !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(0, 240, 255, 0.05), inset 0 0 40px rgba(0, 240, 255, 0.02);
    transition: all 0.3s ease;
}
.glass-hero:hover {
    border-color: rgba(168, 85, 247, 0.3);
    box-shadow: 0 0 60px rgba(168, 85, 247, 0.1);
}

/* Holographic scanline on hero */
.glass-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(0deg, 
        transparent 0px, 
        transparent 4px, 
        rgba(0, 240, 255, 0.02) 4px, 
        rgba(0, 240, 255, 0.02) 5px);
    pointer-events: none;
    z-index: 1;
}

.glass-map, .card {
    background: rgba(6, 10, 18, 0.6) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 240, 255, 0.08) !important;
    border-radius: 28px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
    transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}
.glass-map:hover, .card:hover {
    transform: translateY(-6px);
    border-color: rgba(0, 240, 255, 0.3);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 240, 255, 0.05);
}

/* ----- TYPOGRAPHY (Holographic) ----- */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'JetBrains Mono', 'Inter', monospace !important;
    color: #E2F0FA !important;
    font-weight: 400 !important;
    letter-spacing: 1px !important;
}
p, li, .stMarkdown {
    line-height: 1.7;
    color: #A0B8CC;
}

.main-title {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: 4.6rem !important;
    letter-spacing: 8px !important;
    background: linear-gradient(135deg, #00F0FF 0%, #A855F7 50%, #2DD4BF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px rgba(0, 240, 255, 0.2);
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.1 !important;
    position: relative;
    z-index: 2;
}
.subtitle {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 300 !important;
    font-size: 1.0rem !important;
    color: #A855F7 !important;
    text-align: center !important;
    letter-spacing: 6px !important;
    text-transform: uppercase;
    margin-top: -0.2rem !important;
    position: relative;
    z-index: 2;
    text-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
}
.section-title {
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    color: #00F0FF !important;
    margin-bottom: 0.25rem !important;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    text-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
}
.section-title i {
    color: #A855F7;
    font-size: 1.3rem;
}
.section-desc {
    font-size: 0.9rem !important;
    color: #6A8CA0 !important;
    margin-top: 0 !important;
    margin-bottom: 1.5rem !important;
}

/* ----- SIDEBAR (Abyss Panel) ----- */
[data-testid="stSidebar"] {
    background: rgba(6, 10, 18, 0.9) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(0, 240, 255, 0.08) !important;
    min-width: 200px;
    max-width: 240px;
}
[data-testid="stSidebar"] .stMarkdown {
    color: #A0B8CC !important;
    font-size: 0.9rem;
}
[data-testid="stSidebar"] hr {
    opacity: 0.2;
    border-color: #00F0FF;
}

/* ----- METRIC PILLS (Bioluminescent) ----- */
.metric-pill {
    display: inline-block;
    background: rgba(0, 240, 255, 0.04);
    border: 1px solid rgba(0, 240, 255, 0.1);
    border-radius: 999px;
    padding: 8px 22px;
    margin: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #A0B8CC;
    white-space: nowrap;
    transition: all 0.3s ease;
    backdrop-filter: blur(4px);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.02);
}
.metric-pill:hover {
    background: rgba(0, 240, 255, 0.08);
    border-color: #00F0FF;
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.1);
    transform: scale(1.03);
}
.metric-pill strong {
    color: #E2F0FA;
    font-weight: 700;
}
.metric-pill i {
    color: #2DD4BF;
    margin-right: 6px;
}

/* Status Badge (Deep Pulse) */
.status-badge {
    display: inline-block;
    background: rgba(0, 240, 255, 0.08);
    border: 1px solid #00F0FF;
    border-radius: 999px;
    padding: 4px 18px 4px 14px;
    font-size: 0.7rem;
    font-weight: 600;
    color: #00F0FF;
    letter-spacing: 2px;
    backdrop-filter: blur(4px);
    text-transform: uppercase;
}
.status-badge .dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #00F0FF;
    border-radius: 50%;
    margin-right: 8px;
    box-shadow: 0 0 15px #00F0FF;
    animation: pulseDeep 1.2s ease-in-out infinite;
}
@keyframes pulseDeep {
    0%, 100% { opacity: 1; box-shadow: 0 0 15px #00F0FF; }
    50% { opacity: 0.2; box-shadow: 0 0 5px #00F0FF; }
}

/* ----- BUTTONS (Neon Abyss) ----- */
.stButton > button {
    background: linear-gradient(135deg, #00F0FF, #A855F7) !important;
    border: none !important;
    border-radius: 16px !important;
    color: #060A12 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 14px 32px !important;
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.15) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 0 50px rgba(0, 240, 255, 0.4) !important;
}
.stButton > button:active {
    transform: translateY(2px) scale(0.98) !important;
}

/* ----- DATAFRAME (Neon Grid) ----- */
.stDataFrame {
    background: rgba(6, 10, 18, 0.8) !important;
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 240, 255, 0.05) !important;
}
.stDataFrame thead tr th {
    background: rgba(0, 240, 255, 0.05) !important;
    color: #00F0FF !important;
    font-weight: 600 !important;
}
.stDataFrame tbody tr:hover {
    background: rgba(168, 85, 247, 0.05) !important;
}
.stDataFrame td {
    color: #A0B8CC !important;
}

/* ----- SLIDERS (Cyan Glow) ----- */
.stSlider > div > div > div > input {
    background: #A855F7 !important;
    height: 4px !important;
}
.stSlider > div > div > div > input::-webkit-slider-thumb {
    background: #00F0FF !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    border: 2px solid #060A12 !important;
    box-shadow: 0 0 25px #00F0FF;
    transition: 0.1s ease;
}

/* ----- SELECTBOX (Glass Neon) ----- */
.stSelectbox label {
    color: #6A8CA0 !important;
    font-weight: 500 !important;
}
.stSelectbox > div > div {
    background: rgba(6, 10, 18, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 14px !important;
    color: #E2F0FA !important;
    transition: all 0.3s ease;
}
.stSelectbox > div > div:hover {
    border-color: #00F0FF !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.05);
}
.stSelectbox > div > div > div > div {
    background: #060A12 !important;
    color: #E2F0FA !important;
}
.stSelectbox > div > div > div > div > div:hover {
    background: rgba(0, 240, 255, 0.1) !important;
}

/* ----- SCROLLBAR (Bioluminescent) ----- */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #060A12;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00F0FF, #A855F7);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #A855F7, #2DD4BF);
}

/* ----- FOOTER (Deep Mantra) ----- */
.footer {
    text-align: center;
    padding: 30px 0 20px;
    border-top: 1px solid rgba(0, 240, 255, 0.05);
    margin-top: 40px;
    color: #3A5A6A;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
}
.footer i {
    color: #2DD4BF;
    margin: 0 6px;
}
.footer .mantra {
    color: #A855F7;
    font-weight: 300;
    text-shadow: 0 0 20px rgba(168, 85, 247, 0.1);
}

/* ----- RESPONSIVE ----- */
@media (max-width: 768px) {
    section.main > div { padding: 0 12px !important; }
    .main-title { font-size: 2.8rem !important; letter-spacing: 4px !important; }
    .subtitle { font-size: 0.7rem !important; letter-spacing: 3px !important; }
    .glass-hero { padding: 24px 12px !important; }
    .metric-pill { font-size: 0.65rem !important; padding: 4px 12px !important; }
    .stFoliumMap { height: 350px !important; }
    [data-testid="stSidebar"] { min-width: 0px !important; max-width: 100% !important; }
    section.main::before, section.main::after { display: none; } /* Save mobile performance */
}
@media (max-width: 480px) {
    .main-title { font-size: 2.0rem !important; }
    .section-title { font-size: 1.0rem !important; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA LOADING
# =====================================================

@st.cache_data
def load_predictions():
    file_path = os.path.join(SCRIPT_DIR, "predictions_2026_final.csv")
    return pd.read_csv(file_path)

@st.cache_data
def load_geojson():
    file_path = os.path.join(SCRIPT_DIR, "qc_barangays.geojson")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

predictions = load_predictions()
barangay_geojson = load_geojson()

risk_colors = {
    "Safe": "green",
    "Moderate": "yellow",
    "High": "orange",
    "Extreme": "red"
}
risk_values = {
    "Safe": 1,
    "Moderate": 2,
    "High": 3,
    "Extreme": 4
}

# =====================================================
# HEURISTIC SIMULATION
# =====================================================

def simulate_cases(base_cases, rainfall_pct, humidity_pct, temp_pct, wind_pct, season_factor):
    return max(0, round(base_cases * (1 + rainfall_pct) * (1 + humidity_pct) *
                        (1 + temp_pct) * (1 + wind_pct) * season_factor))

# =====================================================
# PDF REPORT GENERATOR (Unchanged for brevity, but perfect)
# =====================================================

def generate_pdf_report(barangay, df, include_summary=True, include_ci=True,
                        include_graphs=True, include_interventions=True):
    barangay_data = df[df["Barangay"] == barangay].sort_values("YearMonth")
    if barangay_data.empty:
        return None

    total_cases = int(barangay_data["Predicted_Cases"].sum())
    peak_row = barangay_data.loc[barangay_data["Predicted_Cases"].idxmax()]
    peak_month = peak_row["YearMonth"]
    peak_cases = int(peak_row["Predicted_Cases"])

    risk_order = {"Safe": 1, "Moderate": 2, "High": 3, "Extreme": 4}
    max_risk_level = max(barangay_data["Risk_Level"], key=lambda x: risk_order.get(x, 0))

    if max_risk_level == "Safe":
        interventions = [
            "Maintain routine vector surveillance.",
            "Continue community awareness campaigns.",
            "Promote proper waste disposal."
        ]
    elif max_risk_level == "Moderate":
        interventions = [
            "Increase larval source reduction activities.",
            "Conduct weekly barangay clean‑up drives.",
            "Strengthen public health information campaigns."
        ]
    elif max_risk_level == "High":
        interventions = [
            "Implement intensified vector control operations.",
            "Increase dengue surveillance.",
            "Prepare healthcare facilities for possible case surge.",
            "Conduct targeted community interventions."
        ]
    else:
        interventions = [
            "Activate emergency dengue response measures.",
            "Deploy rapid response teams.",
            "Conduct widespread fogging where appropriate.",
            "Mobilize additional healthcare resources.",
            "Issue public health advisories."
        ]

    filename = f"DRIVE_{barangay}_Forecast_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            title=f"DRIVE Report – {barangay}")
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=16, spaceAfter=8
    )
    normal_style = styles['Normal']

    story = []

    story.append(Paragraph("DRIVE", title_style))
    story.append(Paragraph("Dengue Risk Intelligence &bull; Visualization Engine",
                           ParagraphStyle('Subtitle', parent=styles['Normal'],
                                          fontSize=14, alignment=TA_CENTER,
                                          textColor=colors.grey, spaceAfter=12)))
    story.append(Paragraph(f"Barangay: <b>{barangay}</b>", normal_style))
    story.append(Paragraph(f"Report generated: {pd.Timestamp.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    if include_summary:
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"""
        Total predicted cases for 2026: <b>{total_cases:,}</b><br/>
        Peak month: <b>{peak_month}</b> ({peak_cases} cases)<br/>
        Overall risk level: <b>{max_risk_level}</b>
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Monthly Forecast", heading_style))
    table_data = [["Month", "Predicted", "95% PI Lower", "95% PI Upper", "Risk"]]
    RMSE = 21.05
    for _, row in barangay_data.iterrows():
        pred = row["Predicted_Cases"]
        ci_lower = max(0, pred - 1.96 * RMSE)
        ci_upper = pred + 1.96 * RMSE
        month_str = pd.to_datetime(row["YearMonth"]).strftime("%b %Y")
        risk = row["Risk_Level"]
        table_data.append([month_str, f"{pred:.0f}", f"{ci_lower:.0f}", f"{ci_upper:.0f}", risk])

    table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    if include_ci:
        story.append(Paragraph("Confidence Intervals", heading_style))
        story.append(Paragraph(
            "Prediction intervals are estimated using the Random Forest model RMSE (21.05 cases). "
            "The 95% prediction interval is calculated as Predicted ± 1.96 × RMSE.",
            normal_style
        ))
        story.append(Spacer(1, 0.2*inch))

    if include_graphs:
        story.append(Paragraph("Graphical Analysis", heading_style))
        months = pd.to_datetime(barangay_data["YearMonth"]).dt.strftime("%b")
        preds = barangay_data["Predicted_Cases"]
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(months, preds, marker='o', color='#3B82F6', linewidth=2)
        ax.fill_between(months, preds - 1.96*RMSE, preds + 1.96*RMSE,
                        color='#3B82F6', alpha=0.2, label='95% PI')
        ax.set_xlabel("Month")
        ax.set_ylabel("Predicted Cases")
        ax.set_title(f"Forecast Trend – {barangay}")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=100)
        plt.close(fig)
        img_buf.seek(0)
        img = Image(img_buf, width=6*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 0.2*inch))

    if include_interventions:
        story.append(Paragraph("Recommended Public Health Interventions", heading_style))
        for i, item in enumerate(interventions, 1):
            story.append(Paragraph(f"{i}. {item}", normal_style))
        story.append(Spacer(1, 0.2*inch))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "DRIVE · Built with Python, Random Forest, and Streamlit · © 2026",
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=10, alignment=TA_CENTER, textColor=colors.grey)
    ))

    doc.build(story)
    return filename

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:30px;">
        <div style="font-family:'Orbitron',sans-serif; font-weight:900; font-size:2.2rem; letter-spacing:4px; background:linear-gradient(135deg,#00F0FF,#A855F7); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">DRIVE</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:400; font-size:0.6rem; color:#2DD4BF; letter-spacing:3px; margin-top:2px;">BIOLUMINESCENT ABYSS</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**📍 NAVIGATION**")
    st.markdown("• Dashboard")
    st.markdown("• Map")
    st.markdown("• Forecast")
    st.markdown("• Simulation")
    st.markdown("• Reports")
    st.markdown("---")
    st.markdown("**⚙️ SONAR SETTINGS**")
    st.markdown("📌 Quezon City District II")
    st.markdown("📅 Year: 2026")
    st.markdown("---")
    st.caption("© 2026 DRIVE · Deep Surveillance")

# =====================================================
# HERO – BIOLUMINESCENT ABYSS
# =====================================================

total_cases = int(predictions["Predicted_Cases"].sum())
peak_cases = int(predictions["Predicted_Cases"].max())
dom_risk = predictions["Risk_Level"].mode()[0]
n_barangays = predictions["Barangay"].nunique()

st.markdown(f"""
<div class="glass-hero">
    <div style="position:relative; z-index:2;">
        <div style="position:absolute; top:-30px; left:10px; font-size:3.8rem; opacity:0.3; filter:drop-shadow(0 0 40px #00F0FF);">🦠</div>
        <div style="position:absolute; bottom:-20px; right:10px; font-size:2.8rem; opacity:0.2; filter:drop-shadow(0 0 30px #A855F7);">🌊</div>
        <div class="main-title">DRIVE</div>
        <div class="subtitle">Dengue Risk Intelligence · Deep Surveillance</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:300; color:#6A8CA0; margin:8px 0 16px; display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; z-index:2; position:relative; font-size:0.8rem;">
            <span><i class="fas fa-microchip" style="color:#00F0FF;"></i> AI-Powered Early Warning</span>
            <span style="color:#3A5A6A;">|</span>
            <span>Quezon City District II</span>
            <span style="color:#3A5A6A;">|</span>
            <span>2026</span>
            <span class="status-badge"><span class="dot"></span> Active Sonar</span>
        </div>
        <div style="z-index:2; position:relative;">
            <span class="metric-pill"><i class="fas fa-database"></i> <strong>{total_cases:,}</strong> <span>Total Cases</span></span>
            <span class="metric-pill"><i class="fas fa-triangle-exclamation"></i> <strong style="color:#A855F7;">{dom_risk}</strong> <span>Risk Level</span></span>
            <span class="metric-pill"><i class="fas fa-chart-line"></i> <strong style="color:#2DD4BF;">{peak_cases}</strong> <span>Peak Month</span></span>
            <span class="metric-pill"><i class="fas fa-city"></i> <strong>{n_barangays}</strong> <span>Barangays</span></span>
        </div>
        <div style="margin-top:16px; font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#3A5A6A; z-index:2; position:relative;">
            <i class="fas fa-satellite" style="color:#2DD4BF;"></i> Last updated: April 2026 &nbsp;·&nbsp; <i class="fas fa-water" style="color:#00F0FF;"></i> Bioluminescent Abyss v3.0
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# INTERACTIVE RISK MAP
# =====================================================

st.markdown("""
<div style="margin: 20px 0 8px;">
    <div class="section-title"><i class="fas fa-map"></i> Interactive Dengue Risk Map</div>
    <div class="section-desc"><i class="fas fa-compass" style="color:#2DD4BF;"></i> Visualizing predicted dengue intensity across monitored barangays.</div>
</div>
""", unsafe_allow_html=True)

map_center = [14.6760, 121.0437]
m = folium.Map(
    location=map_center,
    zoom_start=12,
    tiles="cartodbpositron",
    scrollWheelZoom=False
)

selected_month = st.selectbox(
    "Select Forecast Month",
    sorted(predictions["YearMonth"].unique()),
    key="map_month"
)

map_data = predictions[predictions["YearMonth"] == selected_month]

def case_color(cases):
    if cases < 50: return "#22C55E"
    elif cases < 60: return "#F59E0B"
    elif cases < 75: return "#F97316"
    else: return "#EF4444"

def style_function(feature):
    name = feature["properties"].get("name")
    row = map_data[map_data["Barangay"].str.lower() == str(name).lower()]
    color = case_color(row.iloc[0]["Predicted_Cases"]) if not row.empty else "#64748B"
    return {"fillColor": color, "color": "#00F0FF", "weight": 1.5, "fillOpacity": 0.6, "dashArray": '2'}

folium.GeoJson(
    barangay_geojson,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Barangay:"])
).add_to(m)

legend_html = """
<div style="
position: fixed; top: 20px; right: 20px;
background: rgba(6, 10, 18, 0.85);
backdrop-filter: blur(16px);
border: 1px solid rgba(0, 240, 255, 0.15);
border-radius: 16px;
padding: 14px 18px;
font-family: 'JetBrains Mono', monospace;
color: #E2F0FA;
font-size: 12px;
box-shadow: 0 8px 32px rgba(0,0,0,0.8);
z-index: 9999;
">
<b style="display:block; margin-bottom:8px; color:#00F0FF;">CASE INTENSITY</b>
<div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-block; width:14px; height:14px; background:#22C55E; border-radius:4px; box-shadow: 0 0 10px #22C55E;"></span> Low (&lt;50)</div>
<div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-block; width:14px; height:14px; background:#F59E0B; border-radius:4px; box-shadow: 0 0 10px #F59E0B;"></span> Moderate (50-60)</div>
<div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-block; width:14px; height:14px; background:#F97316; border-radius:4px; box-shadow: 0 0 10px #F97316;"></span> High (60-75)</div>
<div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-block; width:14px; height:14px; background:#EF4444; border-radius:4px; box-shadow: 0 0 10px #EF4444;"></span> Extreme (>75)</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, use_container_width=True, height=400)

# =====================================================
# FORECAST TABLE & TREND CHART
# =====================================================

col_table, col_chart = st.columns([1, 1], gap="large")

with col_table:
    st.markdown("""
    <div class="section-title" style="font-size:1.2rem;"><i class="fas fa-table"></i> Forecast Overview</div>
    <div class="section-desc" style="font-size:0.85rem;">Monthly predictions per barangay.</div>
    """, unsafe_allow_html=True)
    st.dataframe(
        predictions[["Barangay", "YearMonth", "Predicted_Cases", "Risk_Level"]],
        use_container_width=True,
        height=400
    )

with col_chart:
    st.markdown("""
    <div class="section-title" style="font-size:1.2rem;"><i class="fas fa-chart-simple"></i> Aggregate Trend</div>
    <div class="section-desc" style="font-size:0.85rem;">Total cases across all barangays.</div>
    """, unsafe_allow_html=True)
    trend = predictions.groupby("YearMonth")["Predicted_Cases"].sum().reset_index()
    fig = px.line(
        trend, x="YearMonth", y="Predicted_Cases",
        labels={"YearMonth": "Month", "Predicted_Cases": "Total Cases"}
    )
    fig.update_traces(
        fill='tozeroy',
        fillcolor='rgba(0, 240, 255, 0.15)',
        line=dict(color='#00F0FF', width=3)
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#A0B8CC", family="JetBrains Mono"),
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
        xaxis=dict(gridcolor="rgba(0,240,255,0.05)", title=""),
        yaxis=dict(gridcolor="rgba(0,240,255,0.05)", title="")
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            'displayModeBar': False,
            'scrollZoom': False,
            'doubleClick': False
        }
    )

# =====================================================
# HEATMAP – SCROLLABLE
# =====================================================

st.markdown("""
<div style="margin: 40px 0 10px;">
    <div class="section-title"><i class="fas fa-fire"></i> Dengue Heatmap</div>
    <div class="section-desc"><i class="fas fa-arrows-left-right"></i> Visual intensity. Swipe left/right on mobile.</div>
</div>
""", unsafe_allow_html=True)

heatmap_type = st.selectbox(
    "Select Heatmap Type",
    ["Predicted Cases", "Risk Level"],
    key="heatmap_type"
)

heat = predictions.copy()

if heatmap_type == "Predicted Cases":
    pivot = heat.pivot(index="Barangay", columns="YearMonth", values="Predicted_Cases")
    fig = px.imshow(
        pivot,
        text_auto=True,
        color_continuous_scale=["#22C55E", "#F59E0B", "#F97316", "#EF4444"],
        aspect="equal",
        labels=dict(x="Month", y="Barangay", color="Cases")
    )
else:
    heat["Risk_Value"] = heat["Risk_Level"].map(risk_values)
    pivot = heat.pivot(index="Barangay", columns="YearMonth", values="Risk_Value")
    fig = px.imshow(
        pivot,
        text_auto=True,
        zmin=1, zmax=4,
        color_continuous_scale=["#22C55E", "#F59E0B", "#F97316", "#EF4444"],
        aspect="equal",
        labels=dict(x="Month", y="Barangay", color="Risk")
    )
    fig.update_coloraxes(colorbar=dict(tickvals=[1,2,3,4], ticktext=["Safe","Moderate","High","Extreme"]))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#A0B8CC", size=11),
    margin=dict(l=130, r=30, t=30, b=60),
    width=1000,
    autosize=False
)

html_str = fig.to_html(
    include_plotlyjs='cdn',
    config={
        'displayModeBar': False,
        'responsive': False,
        'scrollZoom': False,
        'doubleClick': False,
        'showTips': False
    },
    full_html=False,
    default_width='1000px'
)

scrollable_html = f"""
<div style="
    overflow-x: auto;
    width: 100%;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x;
    cursor: grab;
    border: 1px solid rgba(0,240,255,0.05);
    border-radius: 20px;
">
    {html_str}
</div>
"""
st.components.v1.html(scrollable_html, height=520)

# =====================================================
# WHAT‑IF SIMULATION
# =====================================================

st.markdown("""
<div style="padding:25px;margin-top:35px;">
    <div class="section-title"><i class="fas fa-microscope"></i> What-If Simulation</div>
    <div class="section-desc">
        <i class="fas fa-sliders" style="color:#2DD4BF;"></i> Adjust environmental conditions to examine their potential effects on predicted dengue cases.
        This is a sensitivity analysis based on the model's baseline predictions.
    </div>
</div>
""", unsafe_allow_html=True)

barangay = st.selectbox(
    "Select Barangay",
    predictions["Barangay"].unique(),
    key="sim_barangay"
)

base = predictions[predictions["Barangay"] == barangay].iloc[0]

col1, col2 = st.columns(2)

with col1:
    rainfall = st.slider("🌧 Rainfall Change (%)", -50, 100, 0)
    humidity = st.slider("💧 Humidity Change (%)", -50, 100, 0)

with col2:
    temperature = st.slider("🌡 Temperature Change (%)", -20, 50, 0)
    wind = st.slider("🌬 Wind Speed Change (%)", -50, 50, 0)

season = st.slider(
    "🗓 Seasonality Factor",
    0.5,
    2.0,
    1.0,
    step=0.1
)

sim_cases = simulate_cases(
    base["Predicted_Cases"],
    rainfall / 100,
    humidity / 100,
    temperature / 100,
    wind / 100,
    season
)

sim_risk = classify_risk_4level(
    sim_cases,
    base["Historical_Mean"],
    base["Historical_SD"],
)

st.markdown("<br>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("🦟 Simulated Cases", f"{sim_cases:.0f}")
m2.metric("⚠ Risk Level", sim_risk)
m3.metric("📈 Case Difference", f"{sim_cases - base['Predicted_Cases']:+.0f}")

# =====================================================
# AUTOMATED REPORT GENERATOR
# =====================================================

st.markdown("""
<div style="margin: 40px 0 10px;">
    <div class="section-title"><i class="fas fa-file-pdf"></i> Automated Report Generator</div>
    <div class="section-desc">
        <i class="fas fa-print"></i> Generate comprehensive barangay‑specific forecast reports containing
        prediction summaries, confidence intervals, graphical analyses,
        and recommended public health interventions.
    </div>
</div>
""", unsafe_allow_html=True)

col_config, col_preview = st.columns([1, 1.5], gap="large")

with col_config:
    st.markdown("### <i class='fas fa-gear' style='color:#2DD4BF;'></i> Report Configuration", unsafe_allow_html=True)
    report_barangay = st.selectbox(
        "Select Barangay",
        predictions["Barangay"].unique(),
        key="report_barangay"
    )
    include_summary = st.checkbox("Prediction Summary", value=True)
    include_ci = st.checkbox("Confidence Intervals", value=True)
    include_graphs = st.checkbox("Graphical Analysis", value=True)
    include_interventions = st.checkbox("Recommended Interventions", value=True)

    generate_btn = st.button("📄 Generate Comprehensive Report", use_container_width=True)

with col_preview:
    st.markdown("### <i class='fas fa-eye' style='color:#A855F7;'></i> Report Preview", unsafe_allow_html=True)

    barangay_data = predictions[predictions["Barangay"] == report_barangay].sort_values("YearMonth")
    if not barangay_data.empty:
        total_cases_preview = int(barangay_data["Predicted_Cases"].sum())
        peak_row_preview = barangay_data.loc[barangay_data["Predicted_Cases"].idxmax()]
        peak_month_preview = peak_row_preview["YearMonth"]
        peak_cases_preview = int(peak_row_preview["Predicted_Cases"])
        risk_order = {"Safe": 1, "Moderate": 2, "High": 3, "Extreme": 4}
        max_risk_preview = max(barangay_data["Risk_Level"], key=lambda x: risk_order.get(x, 0))

        c1, c2, c3 = st.columns(3)
        c1.metric("📊 Total Cases", f"{total_cases_preview:,}")
        c2.metric("📈 Peak Month", f"{peak_month_preview} ({peak_cases_preview})")
        c3.metric("⚠ Overall Risk", max_risk_preview)

        st.markdown("#### Monthly Forecast")
        preview_df = barangay_data[["YearMonth", "Predicted_Cases", "Risk_Level"]].copy()
        RMSE = 21.05
        preview_df["95% PI Lower"] = (preview_df["Predicted_Cases"] - 1.96 * RMSE).clip(lower=0).round(0)
        preview_df["95% PI Upper"] = (preview_df["Predicted_Cases"] + 1.96 * RMSE).round(0)
        preview_df["Month"] = pd.to_datetime(preview_df["YearMonth"]).dt.strftime("%b %Y")
        preview_df = preview_df[["Month", "Predicted_Cases", "95% PI Lower", "95% PI Upper", "Risk_Level"]]
        preview_df.columns = ["Month", "Predicted", "PI Low", "PI High", "Risk"]
        st.dataframe(preview_df, use_container_width=True, height=200)

        if include_interventions:
            st.markdown("#### 🩺 Recommended Interventions")
            if max_risk_preview == "Safe":
                interventions_preview = [
                    "Maintain routine vector surveillance.",
                    "Continue community awareness campaigns.",
                    "Promote proper waste disposal."
                ]
            elif max_risk_preview == "Moderate":
                interventions_preview = [
                    "Increase larval source reduction activities.",
                    "Conduct weekly barangay clean‑up drives.",
                    "Strengthen public health information campaigns."
                ]
            elif max_risk_preview == "High":
                interventions_preview = [
                    "Implement intensified vector control operations.",
                    "Increase dengue surveillance.",
                    "Prepare healthcare facilities for possible case surge.",
                    "Conduct targeted community interventions."
                ]
            else:
                interventions_preview = [
                    "Activate emergency dengue response measures.",
                    "Deploy rapid response teams.",
                    "Conduct widespread fogging where appropriate.",
                    "Mobilize additional healthcare resources.",
                    "Issue public health advisories."
                ]
            for item in interventions_preview:
                st.success(f"✓ {item}")
    else:
        st.warning("No data available for this barangay.")

if generate_btn:
    with st.spinner("Generating comprehensive report..."):
        pdf_file = generate_pdf_report(
            report_barangay,
            predictions,
            include_summary=include_summary,
            include_ci=include_ci,
            include_graphs=include_graphs,
            include_interventions=include_interventions
        )
    if pdf_file and os.path.exists(pdf_file):
        st.success("✅ Report successfully generated!")
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="⬇ Download DRIVE Forecast Report",
                data=f,
                file_name=f"DRIVE_{report_barangay}_Forecast_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.error("Failed to generate report. Please try again.")

# =====================================================
# FOOTER – SIGNATURE MANTRA (Abyss)
# =====================================================

st.markdown("""
<div class="footer">
    <i class="fas fa-satellite-dish"></i> DRIVE · Bioluminescent Abyss Edition · 
    <span class="mantra">"In the silence of the deep, the data speaks."</span> · 
    <i class="fas fa-water"></i> © 2026
</div>
""", unsafe_allow_html=True)
