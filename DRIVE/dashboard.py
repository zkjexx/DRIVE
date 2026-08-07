# =====================================================
# DRIVE – Dengue Risk Intelligence & Visualization Engine
# Version 1.0 (Final Release)
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
    page_title="DRIVE – Dengue Risk Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CSS – DEEP CYBER-GLASS (Polished)
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800;900&family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

html, body, .stApp {
    background: #060A12 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow-x: hidden;
}
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0B1A2A 0%, #060A12 70%) !important;
}

section.main > div {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 24px !important;
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'JetBrains Mono', 'Inter', monospace !important;
    color: #E2F0FA !important;
    font-weight: 400 !important;
    letter-spacing: 1px !important;
}
p, li, .stMarkdown, .stSelectbox, .stSlider {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    line-height: 1.7;
    color: #E2F0FA !important;
}
.section-desc {
    font-size: 0.9rem !important;
    color: #94A3B8 !important;
    margin-top: 0 !important;
    margin-bottom: 1.5rem !important;
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
    font-family: 'JetBrains Mono', monospace !important;
}
.section-title i {
    color: #A855F7;
    font-size: 1.3rem;
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
}
.glass-map, .card {
    background: rgba(6, 10, 18, 0.6) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 240, 255, 0.08) !important;
    border-radius: 28px !important;
    padding: 20px !important;
    margin: 20px 0 !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

[data-testid="stSidebar"] {
    background: rgba(6, 10, 18, 0.9) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(0, 240, 255, 0.08) !important;
    min-width: 200px;
    max-width: 240px;
}
[data-testid="stSidebar"] .stMarkdown {
    color: #E2F0FA !important;
    font-size: 0.9rem;
}

.metric-pill {
    display: inline-block;
    background: rgba(0, 240, 255, 0.04);
    border: 1px solid rgba(0, 240, 255, 0.1);
    border-radius: 999px;
    padding: 8px 22px;
    margin: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #E2F0FA;
    white-space: nowrap;
    transition: all 0.3s ease;
    backdrop-filter: blur(4px);
}
.metric-pill:hover {
    background: rgba(0, 240, 255, 0.08);
    border-color: #00F0FF;
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.1);
    transform: scale(1.03);
}
.metric-pill strong {
    color: #F8FAFC;
    font-weight: 700;
}
.metric-pill i {
    color: #2DD4BF;
    margin-right: 6px;
}

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

.stDataFrame {
    background: rgba(6, 10, 18, 0.8) !important;
    border-radius: 18px !important;
    border: 1px solid rgba(0, 240, 255, 0.05) !important;
}
.stDataFrame thead tr th {
    background: rgba(0, 240, 255, 0.05) !important;
    color: #00F0FF !important;
    font-weight: 600 !important;
}
.stDataFrame td {
    color: #E2F0FA !important;
}

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
}

.stSelectbox label {
    color: #94A3B8 !important;
    font-weight: 500 !important;
}
.stSelectbox > div > div {
    background: rgba(6, 10, 18, 0.8) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important;
    border-radius: 14px !important;
    color: #E2F0FA !important;
}
.stSelectbox > div > div:hover {
    border-color: #00F0FF !important;
}
.stSelectbox > div > div > div > div {
    background: #060A12 !important;
    color: #E2F0FA !important;
}

.stMetric {
    background: rgba(6, 10, 18, 0.5) !important;
    border: 1px solid rgba(0, 240, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 12px !important;
    backdrop-filter: blur(8px) !important;
}
.stMetric label {
    color: #94A3B8 !important;
    font-weight: 400 !important;
}
.stMetric .stMetricValue {
    color: #00F0FF !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
}
.stMetric .stMetricDelta {
    color: #2DD4BF !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #060A12; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #00F0FF, #A855F7); border-radius: 10px; }

.footer {
    text-align: center;
    padding: 30px 0 20px;
    border-top: 1px solid rgba(0, 240, 255, 0.05);
    margin-top: 40px;
    color: #64748B;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
}
.footer i { color: #2DD4BF; margin: 0 6px; }
.footer .mantra { color: #A855F7; font-weight: 300; text-shadow: 0 0 20px rgba(168, 85, 247, 0.1); }

@media (max-width: 768px) {
    section.main > div { padding: 0 12px !important; }
    .main-title { font-size: 2.8rem !important; letter-spacing: 4px !important; }
    .subtitle { font-size: 0.7rem !important; letter-spacing: 3px !important; }
    .glass-hero { padding: 24px 12px !important; }
    .metric-pill { font-size: 0.65rem !important; padding: 4px 12px !important; }
    .stFoliumMap { height: 350px !important; }
    [data-testid="stSidebar"] { min-width: 0px !important; max-width: 100% !important; }
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

# Signature Risk Palette
risk_colors = {
    "Safe": "#00F0FF",
    "Moderate": "#2DD4BF",
    "High": "#A855F7",
    "Extreme": "#FF006E"
}
risk_values = {
    "Safe": 1,
    "Moderate": 2,
    "High": 3,
    "Extreme": 4
}

# =====================================================
# PDF REPORT GENERATOR
# =====================================================

def generate_pdf_report(barangay, df, include_summary=True, include_ci=True,
                        include_graphs=True, include_interventions=True):
    barangay_data = df[df["Barangay"] == barangay].sort_values("YearMonth")
    if barangay_data.empty:
        return None

    total_cases = int(barangay_data["Predicted_Cases"].sum())
    peak_row = barangay_data.loc[barangay_data["Predicted_Cases"].idxmax()]
    peak_month = pd.to_datetime(peak_row["YearMonth"]).strftime("%B %Y")
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
# SIDEBAR – with Help/FAQ section
# =====================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:30px;">
        <div style="font-family:'Orbitron',sans-serif; font-weight:900; font-size:2.4rem; letter-spacing:4px; background:linear-gradient(135deg,#00F0FF,#A855F7); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">DRIVE</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:400; font-size:0.6rem; color:#2DD4BF; letter-spacing:3px; margin-top:2px;">v1.0 · Final</div>
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
    st.markdown("**⚙️ SYSTEM SETTINGS**")
    st.markdown("📌 Quezon City District II")
    st.markdown("📅 Year: 2026")
    st.markdown("---")
    st.markdown("**📊 MODEL ACCURACY**")
    st.markdown(f"""
    <div style="background:rgba(6,10,18,0.5); border:1px solid rgba(0,240,255,0.08); border-radius:12px; padding:12px; font-size:0.8rem;">
        <div><span style="color:#94A3B8;">MAE:</span> <strong style="color:#00F0FF;">15.39</strong> <span style="color:#64748B;">cases/month</span></div>
        <div><span style="color:#94A3B8;">RMSE:</span> <strong style="color:#00F0FF;">21.05</strong> <span style="color:#64748B;">cases/month</span></div>
        <div><span style="color:#94A3B8;">Improvement:</span> <strong style="color:#2DD4BF;">51.5%</strong> <span style="color:#64748B;">vs baseline</span></div>
        <div><span style="color:#94A3B8;">p-value:</span> <strong style="color:#A855F7;">&lt;0.01</strong></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("ℹ️ Help & About", expanded=False):
        st.markdown("""
        **What is DRIVE?**  
        An AI-powered early warning system that predicts dengue cases for each barangay.

        **How to use:**
        1. Select a month on the map to see predicted cases.
        2. Hover over a barangay to see its case count.
        3. Use the **What-If Simulation** to test how weather changes affect risk.
        4. Generate **PDF reports** for any barangay.

        **Data:** Trained on 2023–2024 cases, validated on 2025.  
        **Accuracy:** MAE = ±15.39 cases.

        *For questions, contact your barangay health center.*
        """)
    st.caption("© 2026 DRIVE · All rights reserved.")

# =====================================================
# HERO
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
        <div class="subtitle">Dengue Risk Intelligence · Visualization Engine</div>
        <div style="font-family:'JetBrains Mono',monospace; font-weight:300; color:#94A3B8; margin:8px 0 16px; display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; z-index:2; position:relative; font-size:0.8rem;">
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
            <i class="fas fa-satellite" style="color:#2DD4BF;"></i> Last updated: April 2026 &nbsp;·&nbsp; <i class="fas fa-crown" style="color:#A855F7;"></i> Final Release v1.0
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

month_options = sorted(predictions["YearMonth"].astype(str).unique())
selected_month = st.selectbox(
    "Select Forecast Month",
    month_options,
    index=0,
    key="map_month"
)

map_center = [14.6760, 121.0437]
m = folium.Map(
    location=map_center,
    zoom_start=12,
    tiles="cartodbpositron",
    scrollWheelZoom=False
)

folium.plugins.Fullscreen().add_to(m)

map_data = predictions[predictions["YearMonth"].astype(str) == selected_month]

def case_color(cases):
    if cases < 50: return "#00F0FF"
    elif cases < 60: return "#2DD4BF"
    elif cases < 75: return "#A855F7"
    else: return "#FF006E"

def style_function(feature):
    name = feature["properties"].get("name")
    if not name:
        return {"fillColor": "#64748B", "color": "#A855F7", "weight": 1.0, "fillOpacity": 0.5, "dashArray": '2'}
    barangay_name = str(name).strip().lower()
    row = map_data[map_data["Barangay"].str.strip().str.lower() == barangay_name]
    color = case_color(row.iloc[0]["Predicted_Cases"]) if not row.empty else "#64748B"
    return {
        "fillColor": color,
        "color": "#A855F7",
        "weight": 1.0,
        "fillOpacity": 0.5,
        "dashArray": '2'
    }

geojson_with_cases = barangay_geojson.copy()
for feature in geojson_with_cases['features']:
    name = feature['properties'].get('name')
    if name:
        barangay_name = str(name).strip().lower()
        row = map_data[map_data["Barangay"].str.strip().str.lower() == barangay_name]
        if not row.empty:
            feature['properties']['cases'] = int(row.iloc[0]['Predicted_Cases'])
        else:
            feature['properties']['cases'] = None

folium.GeoJson(
    geojson_with_cases,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["name", "cases"],
        aliases=["Barangay:", "Predicted Cases:"],
        localize=True
    )
).add_to(m)

legend_html = """
<style>
.legend-container {
    position: fixed;
    top: 20px;
    right: 20px;
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
    max-width: 200px;
}
.legend-container b { display: block; margin-bottom: 8px; color: #00F0FF; }
.legend-item { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.legend-color { display: inline-block; width: 14px; height: 14px; border-radius: 4px; flex-shrink: 0; }
@media (max-width: 768px) {
    .legend-container { top: auto; bottom: 20px; right: 10px; padding: 10px 12px; font-size: 10px; max-width: 150px; border-radius: 12px; }
    .legend-container b { font-size: 11px; margin-bottom: 4px; }
    .legend-color { width: 10px; height: 10px; }
}
</style>
<div class="legend-container">
    <b>CASE INTENSITY</b>
    <div class="legend-item"><span class="legend-color" style="background:#00F0FF; box-shadow: 0 0 10px #00F0FF;"></span> Low (&lt;50)</div>
    <div class="legend-item"><span class="legend-color" style="background:#2DD4BF; box-shadow: 0 0 10px #2DD4BF;"></span> Moderate (50-60)</div>
    <div class="legend-item"><span class="legend-color" style="background:#A855F7; box-shadow: 0 0 10px #A855F7;"></span> High (60-75)</div>
    <div class="legend-item"><span class="legend-color" style="background:#FF006E; box-shadow: 0 0 10px #FF006E;"></span> Extreme (>75)</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, use_container_width=True, height=400, key=f"dengue_map_{selected_month}", returned_objects=[])

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
        font=dict(color="#E2F0FA", family="Inter"),
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
# HEATMAP – SIGNATURE CYBER PALETTE
# =====================================================

st.markdown("""
<div style="margin: 40px 0 10px;">
    <div class="section-title"><i class="fas fa-fire"></i> Dengue Heatmap</div>
    <div class="section-desc">Visual intensity of predicted cases. <i class="fas fa-arrows-left-right" style="color:#2DD4BF;"></i> Swipe left/right on mobile.</div>
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
        color_continuous_scale=["#00F0FF", "#2DD4BF", "#A855F7", "#FF006E"],
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
        color_continuous_scale=["#00F0FF", "#2DD4BF", "#A855F7", "#FF006E"],
        aspect="equal",
        labels=dict(x="Month", y="Barangay", color="Risk")
    )
    fig.update_coloraxes(colorbar=dict(tickvals=[1,2,3,4], ticktext=["Safe","Moderate","High","Extreme"]))

fig.update_traces(
    textfont=dict(color="white", size=12, family="Inter", weight="bold"),
    selector=dict(type="heatmap")
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC", size=12),
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
<div style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; touch-action: pan-x; cursor: grab;">
    {html_str}
</div>
"""

st.components.v1.html(scrollable_html, height=520)

# =====================================================
# WHAT‑IF SIMULATION
# =====================================================

st.markdown("""
<div style="padding:25px;margin-top:35px;">
    <div class="section-title">🔮 What-If Simulation</div>
    <div class="section-desc">
        Explore how changes in environmental factors affect dengue risk.
        Adjust the sliders below to see how predictions change in real-time.
    </div>
</div>
""", unsafe_allow_html=True)

barangay = st.selectbox(
    "Select Barangay for Simulation",
    predictions["Barangay"].unique(),
    key="sim_barangay_select"
)

base = predictions[predictions["Barangay"] == barangay].iloc[0]

col_base1, col_base2, col_base3 = st.columns(3)
with col_base1:
    st.metric("📊 Baseline Cases", f"{base['Predicted_Cases']:.0f}")
with col_base2:
    st.metric("📈 Risk Level", base['Risk_Level'])
with col_base3:
    st.metric("📅 Peak Month", base['YearMonth'])

st.markdown("---")
st.markdown("#### 🌡️ Adjust Environmental Factors")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    rainfall = st.slider("🌧️ Rainfall Change (%)", -50, 100, 0, key="rainfall_sim")
    humidity = st.slider("💧 Humidity Change (%)", -50, 100, 0, key="humidity_sim")

with col_s2:
    temperature = st.slider("🌡️ Temperature Change (%)", -20, 50, 0, key="temp_sim")
    wind = st.slider("🌬️ Wind Speed Change (%)", -50, 50, 0, key="wind_sim")

with col_s3:
    season = st.slider("📅 Seasonality Factor", 0.5, 2.0, 1.0, 0.1, key="season_sim")

st.caption("Adjust sliders to see how each factor changes the prediction.")

def simulate_cases(base_cases, rainfall_pct, humidity_pct, temp_pct, wind_pct, season_factor):
    multiplier = 1.0
    if rainfall_pct > 0:
        rainfall_effect = 1 + (rainfall_pct / 100) * 1.2
    else:
        rainfall_effect = 1 + (rainfall_pct / 100) * 0.8
    multiplier *= rainfall_effect
    humidity_effect = 1 + (humidity_pct / 100) * 0.7
    multiplier *= humidity_effect
    if rainfall_pct > 20 and humidity_pct > 20:
        synergy = 1 + ((rainfall_pct + humidity_pct) / 200) * 0.3
        multiplier *= synergy
    temp_effect = 1 + (temp_pct / 100) * 0.5
    multiplier *= temp_effect
    wind_effect = 1 - (wind_pct / 100) * 0.3
    wind_effect = max(0.7, wind_effect)
    multiplier *= wind_effect
    multiplier *= season_factor
    simulated = base_cases * multiplier
    return max(0, round(simulated)), multiplier

sim_cases, total_multiplier = simulate_cases(
    base["Predicted_Cases"],
    rainfall,
    humidity,
    temperature,
    wind,
    season
)

sim_risk = classify_risk_4level(
    sim_cases,
    base["Historical_Mean"],
    base["Historical_SD"],
)

st.markdown("---")
st.markdown("#### 📊 Simulation Results")

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    st.metric("🦟 Simulated Cases", f"{sim_cases:.0f}", delta=f"{sim_cases - base['Predicted_Cases']:+.0f}", delta_color="normal")
with col_r2:
    st.metric("⚠️ Risk Level", sim_risk)
with col_r3:
    st.metric("📈 Change (%)", f"{((sim_cases - base['Predicted_Cases']) / base['Predicted_Cases'] * 100):+.1f}%")
with col_r4:
    st.metric("🔢 Multiplier", f"{total_multiplier:.2f}x")

st.markdown("#### 🔍 Factor Breakdown")

col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown("**📈 Factors That Increased Risk**")
    factors_up = []
    if rainfall > 0: factors_up.append(f"🌧️ Rainfall +{rainfall}%")
    if humidity > 0: factors_up.append(f"💧 Humidity +{humidity}%")
    if temperature > 0: factors_up.append(f"🌡️ Temperature +{temperature}%")
    if season > 1.0: factors_up.append(f"📅 Seasonality +{int((season-1)*100)}%")
    if rainfall > 20 and humidity > 20: factors_up.append(f"🤝 Synergy Bonus Applied")
    if factors_up:
        for f in factors_up:
            st.success(f"✓ {f}")
    else:
        st.info("No increases applied")

with col_b2:
    st.markdown("**📉 Factors That Decreased Risk**")
    factors_down = []
    if rainfall < 0: factors_down.append(f"🌧️ Rainfall {rainfall}%")
    if humidity < 0: factors_down.append(f"💧 Humidity {humidity}%")
    if temperature < 0: factors_down.append(f"🌡️ Temperature {temperature}%")
    if wind > 0: factors_down.append(f"🌬️ Wind +{wind}% (dampener)")
    if wind < 0: factors_down.append(f"🌬️ Wind {wind}% (less dampening)")
    if season < 1.0: factors_down.append(f"📅 Seasonality -{int((1-season)*100)}%")
    if factors_down:
        for f in factors_down:
            st.warning(f"⬇ {f}")
    else:
        st.info("No decreases applied")

st.markdown("#### 📈 Impact Across All Months")
barangay_data = predictions[predictions["Barangay"] == barangay].sort_values("YearMonth")
simulated_months = barangay_data.copy()
simulated_months["Simulated_Cases"] = simulated_months["Predicted_Cases"] * total_multiplier
simulated_months["Simulated_Cases"] = simulated_months["Simulated_Cases"].round(0).astype(int)

fig_sim = px.line(
    simulated_months,
    x="YearMonth",
    y=["Predicted_Cases", "Simulated_Cases"],
    labels={"value": "Cases", "YearMonth": "Month", "variable": "Scenario"},
    title=f"Baseline vs. Simulated – {barangay}",
    color_discrete_map={"Predicted_Cases": "#3B82F6", "Simulated_Cases": "#F59E0B"}
)
fig_sim.update_traces(mode='lines+markers', line=dict(width=2.5), marker=dict(size=8))
fig_sim.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#CBD5E1"),
    margin=dict(l=20, r=20, t=40, b=20),
    height=350,
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
)
st.plotly_chart(fig_sim, use_container_width=True)

with st.expander("📐 How the Simulation Works"):
    st.markdown("""
    **This simulation applies heuristic multipliers to the baseline Random Forest predictions.**
    
    ### Equations
    **Rainfall Effect**  
    $E_{rain} = 1 + \\frac{R}{100} \\times 1.2$ (if R > 0)  
    $E_{rain} = 1 + \\frac{R}{100} \\times 0.8$ (if R ≤ 0)
    
    **Humidity Effect**  
    $E_{hum} = 1 + \\frac{H}{100} \\times 0.7$
    
    **Rainfall-Humidity Synergy**  
    $E_{syn} = 1 + \\frac{R + H}{200} \\times 0.3$ (if R > 20% and H > 20%)
    
    **Temperature Effect**  
    $E_{temp} = 1 + \\frac{T}{100} \\times 0.5$
    
    **Wind Speed Effect**  
    $E_{wind} = 1 - \\frac{W}{100} \\times 0.3$ (minimum 0.7)
    
    **Seasonality Effect**  
    $E_{season} = S$
    
    **Final Multiplier**  
    $M_{total} = E_{rain} \\times E_{hum} \\times E_{syn} \\times E_{temp} \\times E_{wind} \\times E_{season}$
    
    **Simulated Cases**  
    $C_{sim} = \\max(0, \\text{round}(C_{base} \\times M_{total}))$
    
    ### Limitations
    The simulation is heuristic and intended for scenario planning rather than precise prediction.
    """)

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
        peak_month_preview = pd.to_datetime(peak_row_preview["YearMonth"]).strftime("%B %Y")
        peak_cases_preview = int(peak_row_preview["Predicted_Cases"])
        risk_order = {"Safe": 1, "Moderate": 2, "High": 3, "Extreme": 4}
        max_risk_preview = max(barangay_data["Risk_Level"], key=lambda x: risk_order.get(x, 0))

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📊 Total Cases", f"{total_cases_preview:,}")
        with c2:
            st.markdown(f"""
            <div style="background: rgba(6, 10, 18, 0.5); border: 1px solid rgba(0, 240, 255, 0.08); border-radius: 16px; padding: 16px 12px; backdrop-filter: blur(8px); box-shadow: 0 8px 32px rgba(0,0,0,0.6); text-align: center;">
                <div style="color: #94A3B8; font-weight: 400; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 6px;">
                    <i class="fas fa-chart-line" style="color:#2DD4BF;"></i> Peak Month
                </div>
                <div style="color: #00F0FF; font-family: 'Orbitron', sans-serif; font-weight: 800; font-size: 1.8rem; line-height: 1.2; word-break: break-word; white-space: normal;">
                    {peak_month_preview}
                </div>
                <div style="color: #2DD4BF; font-size: 0.9rem; font-weight: 600;">
                    {peak_cases_preview} cases
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.metric("⚠ Overall Risk", max_risk_preview)

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
# AMBIENT PARTICLES
# =====================================================

st.markdown("""
<canvas id="driveCanvas" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; opacity:0.6;"></canvas>
<script>
(function() {
    const canvas = document.getElementById('driveCanvas');
    const ctx = canvas.getContext('2d');
    let w, h;
    const particles = [];
    const numParticles = 60;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() { this.reset(); }
        reset() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.size = Math.random() * 2.5 + 1;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3 - 0.1;
            this.life = Math.random() * 200 + 100;
            this.opacity = Math.random() * 0.5 + 0.2;
            this.color = ['#00F0FF', '#A855F7', '#2DD4BF', '#FF006E'][Math.floor(Math.random() * 4)];
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.life -= 0.2;
            if (this.x < 0) this.x = w;
            if (this.x > w) this.x = 0;
            if (this.y < 0) this.y = h;
            if (this.y > h) this.y = 0;
            if (this.life < 0) this.reset();
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 2);
            gradient.addColorStop(0, this.color);
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.shadowColor = this.color;
            ctx.shadowBlur = 20;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    for (let i = 0; i < numParticles; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, w, h);
        for (let p of particles) {
            p.update();
            p.draw();
        }
        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
""", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer">
    <i class="fas fa-satellite-dish"></i> DRIVE · Final Release v1.0 ·
    <span class="mantra">"Data is the compass – but action is the voyage."</span> ·
    <i class="fas fa-shield-halved"></i> © 2026
</div>
""", unsafe_allow_html=True)
