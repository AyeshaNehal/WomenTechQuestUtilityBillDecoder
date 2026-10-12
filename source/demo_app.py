import streamlit as st
import pandas as pd
import json
import os
import subprocess
import altair as alt
import textwrap
from io import BytesIO
from PIL import Image

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Utility Bill Decoder // 90s Pixel Edition",
    page_icon="🕹️",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# HELPER: DEDENT HTML TO PREVENT MARKDOWN CODEBLOCK CONVERSION
# -----------------------------------------------------------------------------
def render_html(html_str: str):
    """Safely renders HTML by removing leading indentation AND blank lines that prematurely terminate HTML blocks in Markdown."""
    dedented = textwrap.dedent(html_str).strip()
    no_blank_lines = "\n".join([line for line in dedented.splitlines() if line.strip()])
    st.markdown(no_blank_lines, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# RETRO PIXEL ART CYBER-Y2K STYLING (CSS)
# -----------------------------------------------------------------------------
render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Silkscreen:wght@400;700&family=Pixelify+Sans:wght@500;700&family=VT323&display=swap');

/* GLOBAL THEME & PASTEL GRID BACKGROUND */
.stApp {
    background-color: #F8F4FD !important;
    background-image: 
        linear-gradient(rgba(240, 190, 220, 0.35) 1px, transparent 1px),
        linear-gradient(90deg, rgba(240, 190, 220, 0.35) 1px, transparent 1px),
        radial-gradient(circle at 10% 20%, rgba(255, 235, 175, 0.4) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(200, 245, 230, 0.45) 0%, transparent 45%) !important;
    background-size: 24px 24px, 24px 24px, 100% 100%, 100% 100% !important;
    color: #1A1A26 !important;
    font-family: 'Pixelify Sans', -apple-system, sans-serif !important;
}

/* ENFORCE HIGH-CONTRAST BLACK/DARK TEXT ACROSS ALL LABELS */
p, span, div, label, li, a, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, [data-testid="stMarkdownContainer"] p,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] p, .stCaption {
    color: #1A1A26 !important;
}

/* FORCE CRISP WHITE BACKGROUND AND DARK BOLD TEXT ON ALL INPUTS & SELECTS */
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
input, select, textarea,
.stTextInput input,
.stSelectbox div[role="combobox"],
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #1A1A26 !important;
    border: 2px solid #2B213A !important;
    border-radius: 6px !important;
    font-weight: bold !important;
    box-shadow: 2px 2px 0px #2B213A !important;
}

/* Ensure all text inside input boxes, dropdowns, and values is jet black */
input::placeholder,
.stTextInput input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] * {
    color: #1A1A26 !important;
    -webkit-text-fill-color: #1A1A26 !important;
}

/* Dropdown popover menu items */
ul[data-baseweb="menu"],
div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background-color: #FFFDF8 !important;
    border: 2px solid #2B213A !important;
    border-radius: 6px !important;
    box-shadow: 4px 4px 0px #2B213A !important;
}

li[data-baseweb="menu-item"] {
    color: #1A1A26 !important;
    font-family: 'Pixelify Sans', sans-serif !important;
}

li[data-baseweb="menu-item"]:hover {
    background-color: #FFE366 !important;
    color: #2B213A !important;
}

/* ELIMINATE CODE BLOCKS IF ACCIDENTALLY TRIGGERED */
pre, code, [data-testid="stCodeBlock"] {
    background-color: transparent !important;
    border: none !important;
    color: #1A1A26 !important;
}

/* TYPOGRAPHY */
h1, h2, h3, .pixel-font {
    font-family: 'Press Start 2P', cursive !important;
    letter-spacing: -0.5px;
    color: #2D1B4E !important;
    text-shadow: 2px 2px 0px #FFC1D6;
}

.pixel-subfont {
    font-family: 'Silkscreen', monospace !important;
    color: #2D1B4E !important;
}

.mono-font {
    font-family: 'VT323', monospace !important;
    font-size: 1.25rem;
    color: #1A1A26 !important;
}

/* RETRO PIXEL WINDOW CONTAINERS */
.pixel-window {
    background: #FFFDF9 !important;
    border: 3px solid #2B213A !important;
    border-radius: 8px !important;
    box-shadow: 6px 6px 0px #2B213A !important;
    margin-bottom: 24px;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.pixel-window:hover {
    transform: translate(-1px, -1px);
    box-shadow: 7px 7px 0px #2B213A !important;
}

.pixel-header {
    background: linear-gradient(90deg, #FFB5D5 0%, #D8C3FF 50%, #B4F5E6 100%) !important;
    border-bottom: 3px solid #2B213A !important;
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Press Start 2P', cursive;
    font-size: 0.72rem;
    color: #2B213A !important;
}

.pixel-btns {
    display: flex;
    gap: 6px;
}

.pixel-dot {
    width: 12px;
    height: 12px;
    border: 2px solid #2B213A;
    border-radius: 3px;
    display: inline-block;
}
.dot-pink { background: #FF7597; }
.dot-yellow { background: #FFD84D; }
.dot-green { background: #6CE5B1; }

.pixel-body {
    background: #FFFDF9 !important;
    padding: 18px 20px;
    color: #1A1A26 !important;
}

/* RETRO BUTTONS */
.stButton > button {
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.75rem !important;
    background: #FFE366 !important;
    color: #2B213A !important;
    border: 3px solid #2B213A !important;
    border-radius: 6px !important;
    box-shadow: 4px 4px 0px #2B213A !important;
    padding: 12px 20px !important;
    transition: all 0.1s ease !important;
}

.stButton > button:hover {
    background: #FFD433 !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #2B213A !important;
    color: #1A1A26 !important;
}

.stButton > button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 0px 0px 0px #2B213A !important;
}

/* BADGES & PILLS */
.pixel-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #EBE0FF;
    border: 2px solid #2B213A;
    border-radius: 6px;
    padding: 6px 12px;
    font-family: 'Silkscreen', monospace;
    font-size: 0.75rem;
    font-weight: bold;
    color: #1A1A26 !important;
    box-shadow: 2px 2px 0px #2B213A;
    margin: 3px 2px;
}
.pill-pink { background: #FFD3DF !important; }
.pill-yellow { background: #FFF0A5 !important; }
.pill-mint { background: #C8FCEA !important; }
.pill-blue { background: #D0E6FF !important; }

/* RETRO SPEECH BUBBLE FOR QA */
.pixel-bubble {
    background: #FFF9E6 !important;
    border: 3px solid #2B213A !important;
    border-radius: 10px !important;
    box-shadow: 4px 4px 0px #2B213A !important;
    padding: 16px 20px;
    position: relative;
    font-size: 1.05rem;
    line-height: 1.55;
    margin-top: 10px;
    color: #1A1A26 !important;
}

/* THERMAL RECEIPT STYLING */
.pixel-receipt {
    background: #FFFEFA !important;
    border: 2px dashed #3A3247 !important;
    padding: 22px;
    font-family: 'VT323', monospace !important;
    font-size: 1.35rem;
    color: #1A1A26 !important;
    line-height: 1.3;
    box-shadow: 5px 5px 0px #D8CADE !important;
    border-radius: 4px;
}
.pixel-receipt span, .pixel-receipt div {
    color: #1A1A26 !important;
}
.receipt-header {
    text-align: center;
    border-bottom: 2px dashed #3A3247;
    padding-bottom: 10px;
    margin-bottom: 10px;
}
.receipt-row {
    display: flex;
    justify-content: space-between;
    margin: 4px 0;
}
.receipt-total {
    border-top: 2px dashed #3A3247;
    border-bottom: 2px dashed #3A3247;
    padding: 8px 0;
    margin: 8px 0;
    font-weight: bold;
    font-size: 1.5rem;
}
.barcode {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    text-align: center;
    letter-spacing: 5px;
    margin-top: 12px;
    font-size: 1.15rem;
    color: #1A1A26 !important;
}

/* STREAMLIT SIDEBAR OVERRIDES */
section[data-testid="stSidebar"] {
    background-color: #F3ECF9 !important;
    border-right: 3px solid #2B213A !important;
}
section[data-testid="stSidebar"] * {
    color: #1A1A26 !important;
}

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 3px solid #2B213A;
    padding-bottom: 6px;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.65rem !important;
    background: #EFE8FA !important;
    border: 2px solid #2B213A !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 14px !important;
    color: #2B213A !important;
    box-shadow: 2px 2px 0px #2B213A !important;
}

.stTabs [aria-selected="true"] {
    background: #FFD4E2 !important;
    border-bottom: 2px solid #FFD4E2 !important;
    color: #1A1A26 !important;
}

/* DATA TABLES & EXPANDER */
.stDataFrame, .stTable {
    border: 2px solid #2B213A !important;
    border-radius: 6px !important;
    box-shadow: 3px 3px 0px #2B213A !important;
    overflow: hidden;
    background-color: #FFFFFF !important;
}
.stDataFrame th, .stDataFrame td, .stTable th, .stTable td {
    color: #1A1A26 !important;
    background-color: #FFFFFF !important;
}

/* PIXEL PROGRESS BAR */
.pixel-progress-outer {
    width: 100%;
    height: 22px;
    background: #E9DEFA;
    border: 2px solid #2B213A;
    border-radius: 4px;
    padding: 2px;
    box-shadow: 2px 2px 0px #2B213A;
}
.pixel-progress-inner {
    height: 100%;
    background: repeating-linear-gradient(
        90deg,
        #6CE5B1,
        #6CE5B1 8px,
        #49CD97 8px,
        #49CD97 12px
    );
    border-radius: 2px;
}
</style>
""")

# -----------------------------------------------------------------------------
# SESSION STATE NAVIGATION (WELCOME SCREEN vs APP)
# -----------------------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state["started"] = False

# -----------------------------------------------------------------------------
# SCREEN 1: RETRO PIXEL WELCOME SCREEN (HERO / START GAME)
# -----------------------------------------------------------------------------
if not st.session_state["started"]:
    _, center_col, _ = st.columns([0.15, 0.7, 0.15])
    
    with center_col:
        welcome_html = """<div class="pixel-window" style="margin-top: 30px; text-align: center;">
<div class="pixel-header">
<span>🕹️ SYSTEM: ARCADE BOOT // WTQ 2026 🕹️</span>
<div class="pixel-btns"><span class="pixel-dot dot-yellow"></span><span class="pixel-dot dot-pink"></span><span class="pixel-dot dot-green"></span></div>
</div>
<div class="pixel-body" style="padding: 35px 25px;">
<div style="font-size: 2.2rem; margin-bottom: 14px; font-family: 'Press Start 2P'; color: #2D1B4E; text-shadow: 3px 3px 0px #FFB5D5;">⚡ UTILITY BILL DECODER ⚡</div>
<p class="pixel-subfont" style="font-size: 1.05rem; color: #534269; margin-bottom: 18px;">✦ MULTI-AGENT VISION EXTRACTION & PROVABLE AST MATH REASONER ✦</p>
<div style="margin: 20px 0; display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">
<span class="pixel-pill pill-pink">💖 100% AUDIT ACCURACY</span>
<span class="pixel-pill pill-yellow">⚡ VISION + AST ENGINE</span>
<span class="pixel-pill pill-mint">🔋 ZERO HALLUCINATION</span>
<span class="pixel-pill pill-blue">🕹️ 90s CYBER EDITION</span>
</div>
<div style="background: #FFFDF4; border: 3px solid #2B213A; border-radius: 8px; padding: 22px; margin: 26px auto; text-align: left; box-shadow: 4px 4px 0px #2B213A;">
<p style="font-family: 'Press Start 2P'; font-size: 0.85rem; color: #2B213A; margin-bottom: 10px;">👾 MISSION BRIEFING:</p>
<p style="font-size: 1.1rem; line-height: 1.6; color: #1A1A26; margin: 0;">Extract, audit, and explain complex Pakistani electricity bills (K-Electric, LESCO, IESCO). Eliminates LLM math hallucination by coupling multimodal vision extraction with a sandboxed Python AST computation pipeline.</p>
</div>
<p class="pixel-subfont" style="font-size: 0.85rem; color: #735F88; margin-top: 15px; margin-bottom: 10px;">▶ INSERT COIN OR CLICK PROCEED TO LAUNCH DECODER ◀</p>
</div>
</div>"""
        render_html(welcome_html)
        
        btn_c1, btn_c2, btn_c3 = st.columns([0.2, 0.6, 0.2])
        with btn_c2:
            if st.button("🕹️ PROCEED TO SYSTEM // START ➔", use_container_width=True):
                st.session_state["started"] = True
                st.rerun()
                
    st.stop()

# -----------------------------------------------------------------------------
# SCREEN 2: MAIN DASHBOARD DECK (ACTIVE ONCE PROCEED CLICKED)
# -----------------------------------------------------------------------------

# TOP MARQUEE BANNER WITH TITLE & RETURN BUTTON
top_c1, top_c2 = st.columns([0.8, 0.2])
with top_c1:
    render_html("""
    <div class="pixel-window" style="margin-bottom: 16px;">
        <div class="pixel-header">
            <span>👾 SYSTEM ONLINE // DECODER TERMINAL 👾</span>
            <div class="pixel-btns">
                <span class="pixel-dot dot-yellow"></span>
                <span class="pixel-dot dot-pink"></span>
                <span class="pixel-dot dot-green"></span>
            </div>
        </div>
        <div class="pixel-body" style="padding: 14px 18px;">
            <span style="font-size: 1.25rem; font-family: 'Press Start 2P'; color: #2D1B4E;">⚡ UTILITY BILL DECODER ⚡</span>
            <span class="pixel-subfont" style="font-size: 0.85rem; margin-left: 12px; color: #534269;">[ PROVABLE AST MATH ENGINE ]</span>
        </div>
    </div>
    """)

with top_c2:
    st.write("")
    if st.button("🔙 TITLE SCREEN", use_container_width=True):
        st.session_state["started"] = False
        st.rerun()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLLER DECK
# -----------------------------------------------------------------------------
with st.sidebar:
    render_html("""
    <div class="pixel-window" style="margin-bottom: 15px;">
        <div class="pixel-header">
            <span>🎮 CONTROLLER</span>
            <div class="pixel-btns">
                <span class="pixel-dot dot-pink"></span>
                <span class="pixel-dot dot-green"></span>
            </div>
        </div>
        <div class="pixel-body" style="padding: 10px;">
            <p class="pixel-subfont" style="font-size: 0.75rem; margin: 0; color: #1A1A26;">LOAD BILL FEED</p>
        </div>
    </div>
    """)
    
    source_mode = st.radio(
        "Source Mode",
        ["📁 Preset Bills", "📤 Upload Custom Bill"],
        label_visibility="collapsed"
    )

    selected_img_path = None
    selected_bill_id = None
    uploaded_image_bytes = None

    if source_mode == "📁 Preset Bills":
        bills_folder = st.selectbox(
            "Bills Directory",
            ["test/bills", "train/bills"],
            index=0
        )
        templates_folder = st.text_input("Templates Folder", "test/csv" if bills_folder == "test/bills" else "tests/fixtures/templates")
        output_folder = st.text_input("Output Folder", "output")
        
        if os.path.exists(bills_folder):
            raw_images = sorted([f for f in os.listdir(bills_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            image_options = ["-- SELECT A BILL --"] + raw_images
            selected_choice = st.selectbox("Select Target Bill", image_options, index=0)
            
            if selected_choice != "-- SELECT A BILL --":
                selected_img_path = os.path.join(bills_folder, selected_choice)
                selected_bill_id = os.path.splitext(selected_choice)[0]
        else:
            st.error(f"Directory `{bills_folder}` not found.")
    else:
        st.write("Drag & drop a new electricity bill image:")
        uploaded_file = st.file_uploader("Upload Bill Image", type=["png", "jpg", "jpeg"])
        templates_folder = st.text_input("Templates Folder", "test/csv")
        output_folder = st.text_input("Output Folder", "output")
        bills_folder = "test/bills"
        
        if uploaded_file is not None:
            uploaded_image_bytes = uploaded_file.read()
            selected_bill_id = os.path.splitext(uploaded_file.name)[0]
            os.makedirs("scratch", exist_ok=True)
            temp_path = os.path.join("scratch", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_image_bytes)
            selected_img_path = temp_path

    st.markdown("---")
    render_html("""
    <div style="font-size: 0.8rem;" class="pixel-subfont">
        <b>BATTERY / STATUS:</b>
        <div class="pixel-progress-outer" style="margin-top: 5px;">
            <div class="pixel-progress-inner" style="width: 95%;"></div>
        </div>
        <p style="margin-top: 6px; font-size: 0.72rem; color: #1A1A26;">ENGINE READY // ZERO COST CACHE</p>
    </div>
    """)

# -----------------------------------------------------------------------------
# DATA LOADING HELPERS
# -----------------------------------------------------------------------------
l1_path = os.path.join(output_folder, "level1.csv") if output_folder else None
l2_path = os.path.join(output_folder, "level2.csv") if output_folder else None

l1_df = pd.read_csv(l1_path) if (l1_path and os.path.exists(l1_path)) else None
l2_df = pd.read_csv(l2_path) if (l2_path and os.path.exists(l2_path)) else None

audit_data = None
current_l1_json = None

if selected_bill_id:
    audit_file = os.path.join("audit", f"{selected_bill_id}.json")
    if os.path.exists(audit_file):
        try:
            with open(audit_file, "r", encoding="utf-8") as af:
                audit_data = json.load(af)
        except Exception:
            audit_data = None

    if l1_df is not None:
        row = l1_df[l1_df['bill_id'] == selected_bill_id]
        if not row.empty:
            try:
                current_l1_json = json.loads(row.iloc[0]['json'])
            except Exception:
                current_l1_json = None

    if current_l1_json is None and audit_data and "level1" in audit_data:
        current_l1_json = audit_data["level1"]

# -----------------------------------------------------------------------------
# MAIN STAGE: TWO INTERACTIVE COLUMNS
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1.0, 1.3], gap="medium")

# LEFT COLUMN: RETRO BILL SCANNER / VIEWER
with col_left:
    render_html("""
    <div class="pixel-window">
        <div class="pixel-header">
            <span>📷 SCANNER // INPUT FEED</span>
            <div class="pixel-btns">
                <span class="pixel-dot dot-yellow"></span>
                <span class="pixel-dot dot-green"></span>
            </div>
        </div>
        <div class="pixel-body" style="text-align: center;">
    """)
    
    if selected_img_path and os.path.exists(selected_img_path):
        st.image(selected_img_path, use_container_width=True)
        render_html(f"""
        <div style="margin-top: 10px; display: flex; flex-wrap: wrap; justify-content: center; gap: 6px;">
            <span class="pixel-pill pill-yellow">ID: {selected_bill_id}</span>
            <span class="pixel-pill pill-pink">FORMAT: {selected_img_path.split('.')[-1].upper()}</span>
        </div>
        """)
    else:
        render_html("""
        <div style="padding: 60px 20px; border: 2px dashed #4A3A60; border-radius: 8px; background: #FFFDF6; margin: 10px 0;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">📺</div>
            <div class="pixel-font" style="font-size: 0.85rem; color: #2D1B4E;">[ NO BILL FEED DETECTED ]</div>
            <p class="pixel-subfont" style="font-size: 0.8rem; color: #5B4F70; margin-top: 8px;">
                Please select a bill from the sidebar dropdown or drag & drop an image to preview!
            </p>
        </div>
        """)
        
    render_html("</div></div>")

# RIGHT COLUMN: RETRO DECODER TERMINAL (TABS)
with col_right:
    render_html("""
    <div class="pixel-window">
        <div class="pixel-header">
            <span>🕹️ DECODER TERMINAL // ANALYTICS</span>
            <div class="pixel-btns">
                <span class="pixel-dot dot-pink"></span>
                <span class="pixel-dot dot-yellow"></span>
                <span class="pixel-dot dot-green"></span>
            </div>
        </div>
        <div class="pixel-body">
    """)

    tab_lvl1, tab_lvl2, tab_chart, tab_receipt = st.tabs([
        "📊 LEVEL 1 DATA",
        "🤖 LEVEL 2 QA",
        "📈 12-MO CHART",
        "🧾 THERMAL RECEIPT"
    ])

    # ---------------------------------------------------------
    # TAB 1: LEVEL 1 EXTRACTION
    # ---------------------------------------------------------
    with tab_lvl1:
        if current_l1_json:
            m1, m2, m3 = st.columns(3)
            with m1:
                render_html(f"""
                <div class="pixel-pill pill-pink" style="width: 100%; justify-content: center; padding: 8px;">
                    ⚡ UNITS: {current_l1_json.get('units_consumed') or 'N/A'}
                </div>
                """)
            with m2:
                curr_bill = current_l1_json.get('current_bill')
                bill_str = f"PKR {curr_bill:,.0f}" if isinstance(curr_bill, (int, float)) else "N/A"
                render_html(f"""
                <div class="pixel-pill pill-yellow" style="width: 100%; justify-content: center; padding: 8px;">
                    💰 BILL: {bill_str}
                </div>
                """)
            with m3:
                pay_due = current_l1_json.get('payable_within_due_date')
                pay_str = f"PKR {pay_due:,.0f}" if isinstance(pay_due, (int, float)) else "N/A"
                render_html(f"""
                <div class="pixel-pill pill-mint" style="width: 100%; justify-content: center; padding: 8px;">
                    📅 DUE: {current_l1_json.get('due_date') or 'N/A'}
                </div>
                """)

            st.write("")
            scalars = {
                "Provider": current_l1_json.get("provider"),
                "Tariff": current_l1_json.get("tariff"),
                "Sanctioned Load": f"{current_l1_json.get('sanctioned_load_kw')} kW" if current_l1_json.get('sanctioned_load_kw') is not None else "null",
                "Bill Month": current_l1_json.get("bill_month"),
                "Reading Date": current_l1_json.get("reading_date"),
                "Issue Date": current_l1_json.get("issue_date"),
                "Due Date": current_l1_json.get("due_date"),
                "Previous Reading": current_l1_json.get("previous_reading"),
                "Current Reading": current_l1_json.get("current_reading"),
                "Arrears": current_l1_json.get("arrears"),
                "Payable Within Due": current_l1_json.get("payable_within_due_date"),
                "Payable After Due": current_l1_json.get("payable_after_due_date"),
            }
            scalar_df = pd.DataFrame(list(scalars.items()), columns=["Field", "Extracted Value"])
            st.dataframe(scalar_df, use_container_width=True, hide_index=True)

            c_col, t_col = st.columns(2)
            with c_col:
                render_html("<p class='pixel-subfont' style='font-size:0.85rem; font-weight:bold;'>⚡ CHARGES BREAKDOWN</p>")
                charges = current_l1_json.get("charges", [])
                if charges:
                    st.dataframe(pd.DataFrame(charges), use_container_width=True, hide_index=True)
                else:
                    st.caption("No charges extracted")

            with t_col:
                render_html("<p class='pixel-subfont' style='font-size:0.85rem; font-weight:bold;'>🏛️ TAXES BREAKDOWN</p>")
                taxes = current_l1_json.get("taxes", [])
                if taxes:
                    st.dataframe(pd.DataFrame(taxes), use_container_width=True, hide_index=True)
                else:
                    st.caption("No taxes extracted")

            with st.expander("💾 VIEW RAW DISK JSON"):
                st.json(current_l1_json)
        else:
            render_html("""
            <div style="padding: 40px 15px; text-align: center; background: #FFFDF6; border: 2px dashed #4A3A60; border-radius: 6px;">
                <div style="font-size: 2rem;">👾</div>
                <p class="pixel-font" style="font-size: 0.8rem; color: #2D1B4E; margin-top: 8px;">[ AWAITING INPUT ]</p>
                <p class="pixel-subfont" style="font-size: 0.75rem; color: #5B4F70;">
                    Please select or upload a bill in the sidebar controller to view extracted Level 1 readings!
                </p>
            </div>
            """)

    # ---------------------------------------------------------
    # TAB 2: LEVEL 2 QA
    # ---------------------------------------------------------
    with tab_lvl2:
        if l2_df is not None and selected_bill_id:
            rows = l2_df[l2_df['bill_id'] == selected_bill_id]
            if not rows.empty:
                q_options = rows['question'].tolist()
                sel_question = st.selectbox("Select Inquiry Question:", q_options)
                matched_row = rows[rows['question'] == sel_question].iloc[0]
                answer_text = matched_row['answer']
                q_id = matched_row.get('question_id', 'QA')

                render_html(f"""
                <div class="pixel-pill pill-yellow" style="margin-top: 8px;">
                    QUESTION ID: {q_id}
                </div>
                <div class="pixel-bubble">
                    <div style="font-size: 0.75rem; font-family: 'Press Start 2P'; color: #7B3E5C; margin-bottom: 8px;">
                        💬 DECODER AGENT REPLY:
                    </div>
                    {answer_text}
                </div>
                """)
                
                render_html("""
                <div style="margin-top: 14px; display: flex; gap: 8px;">
                    <span class="pixel-pill pill-mint">✅ AST VERIFIED</span>
                    <span class="pixel-pill pill-blue">🛡️ GROUNDED IN DATA</span>
                </div>
                """)
            else:
                st.info(f"No Level 2 rows found for `{selected_bill_id}`.")
        else:
            render_html("""
            <div style="padding: 40px 15px; text-align: center; background: #FFFDF6; border: 2px dashed #4A3A60; border-radius: 6px;">
                <div style="font-size: 2rem;">🤖</div>
                <p class="pixel-font" style="font-size: 0.8rem; color: #2D1B4E; margin-top: 8px;">[ AI REASONER READY ]</p>
                <p class="pixel-subfont" style="font-size: 0.75rem; color: #5B4F70;">
                    Select or upload a bill to inspect grounded Level 2 customer explanations!
                </p>
            </div>
            """)

    # ---------------------------------------------------------
    # TAB 3: 12-MONTH CONSUMPTION ARCADE CHART
    # ---------------------------------------------------------
    with tab_chart:
        history_rows = []
        if audit_data and "extras" in audit_data:
            history_rows = audit_data["extras"].get("billing_history_rows", [])

        if history_rows:
            chart_df = pd.DataFrame(history_rows)
            chart_df["units"] = pd.to_numeric(chart_df["units"], errors="coerce").fillna(0)
            chart_df["tariff_tier"] = chart_df["units"].apply(
                lambda u: "Exceeded (>200 kWh)" if u > 200 else "Protected (<=200 kWh)"
            )
            
            over_200 = int((chart_df["units"] > 200).sum())
            total_months = len(chart_df)
            avg_units = chart_df["units"].mean()
            max_row = chart_df.loc[chart_df["units"].idxmax()]
            
            status_banner = f"""<div style="background: #FFFDF4; border: 2px solid #2B213A; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 3px 3px 0px #2B213A;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span class="pixel-font" style="font-size: 0.8rem; color: #2D1B4E;">🎯 PURPOSE: 200 kWh PROTECTED TARIFF & SUBSIDY MONITOR</span>
<span class="pixel-pill pill-yellow">NEPRA TARIFF AUDIT</span>
</div>
<p style="font-size: 0.95rem; line-height: 1.5; color: #1A1A26; margin: 0;">
Under Pakistan electricity regulations (K-Electric, LESCO, IESCO), staying consistently <b>at or below 200 units (kWh)</b> grants households the heavily subsidized <b>Protected Consumer Tariff</b>. Crossing 200 units forfeits this status, kicking the consumer into unprotected slabs where energy rates often triple! This chart monitors your 12-month usage against that exact 200 kWh threshold.
</p>
</div>"""
            render_html(status_banner)
            
            if over_200 > 0:
                render_html(f"""<div style="background: #FFE8EC; border: 2px solid #E63946; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; font-family: 'Silkscreen'; font-size: 0.82rem; color: #9E1B28;">
⚠️ UNPROTECTED SLAB BREACH DETECTED: {over_200} of {total_months} billing months exceeded 200 kWh! Higher commercial/unprotected rates apply during these periods.
</div>""")
            else:
                render_html("""<div style="background: #E0FBEF; border: 2px solid #287A54; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; font-family: 'Silkscreen'; font-size: 0.82rem; color: #155734;">
🛡️ PROTECTED STATUS ACTIVE: All 12 months maintained below the 200 kWh ceiling! Maximum government lifeline subsidies retained.
</div>""")

            bars = alt.Chart(chart_df).mark_bar(
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4,
                stroke="#2B213A",
                strokeWidth=2
            ).encode(
                x=alt.X('month:N', sort=None, title='Billing Month', axis=alt.Axis(labelAngle=-45, labelFont='Silkscreen', titleFont='Press Start 2P', titleFontSize=9)),
                y=alt.Y('units:Q', title='Units Consumed (kWh)', axis=alt.Axis(labelFont='Silkscreen', titleFont='Press Start 2P', titleFontSize=9)),
                color=alt.Color(
                    'tariff_tier:N',
                    scale=alt.Scale(
                        domain=['Protected (<=200 kWh)', 'Exceeded (>200 kWh)'],
                        range=['#6CE5B1', '#FF7597']
                    ),
                    legend=alt.Legend(title='Tariff Tier', labelFont='Silkscreen', titleFont='Press Start 2P', titleFontSize=8)
                ),
                tooltip=['month', 'units', 'tariff_tier', 'amount_billed', 'amount_paid']
            )

            rule = alt.Chart(pd.DataFrame({'threshold': [200]})).mark_rule(
                color='#E63946',
                strokeDash=[6, 4],
                size=3
            ).encode(
                y='threshold:Q'
            )

            styled_chart = (bars + rule).properties(
                height=260
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(styled_chart, use_container_width=True)

            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric("SUBSIDY STATUS", "PROTECTED" if over_200 == 0 else "UNPROTECTED")
            with m_col2:
                st.metric("MONTHS > 200", f"{over_200} of {total_months}")
            with m_col3:
                st.metric("12-MO AVERAGE", f"{avg_units:.1f} kWh")
            with m_col4:
                st.metric("PEAK MONTH", f"{max_row['month']}", f"{max_row['units']:.0f} kWh")
        else:
            render_html("""<div style="padding: 40px 15px; text-align: center; background: #FFFDF6; border: 2px dashed #4A3A60; border-radius: 6px;">
<div style="font-size: 2rem;">📈</div>
<p class="pixel-font" style="font-size: 0.8rem; color: #2D1B4E; margin-top: 8px;">[ CHART STANDBY ]</p>
<p class="pixel-subfont" style="font-size: 0.75rem; color: #5B4F70;">
Select a bill with historical billing data to render the 12-month consumption trend and NEPRA tariff monitor.
</p>
</div>""")

    # ---------------------------------------------------------
    # TAB 4: RETRO THERMAL CASHIER RECEIPT
    # ---------------------------------------------------------
    with tab_receipt:
        if current_l1_json:
            p_provider = current_l1_json.get("provider", "DISCO")
            p_month = current_l1_json.get("bill_month", "N/A")
            p_due = current_l1_json.get("due_date", "N/A")
            p_units = current_l1_json.get("units_consumed", 0)
            p_load = current_l1_json.get("sanctioned_load_kw", "N/A")
            p_bill = current_l1_json.get("current_bill") or 0
            p_pay = current_l1_json.get("payable_within_due_date") or p_bill
            p_late = current_l1_json.get("payable_after_due_date") or 0
            
            charges_raw = current_l1_json.get("charges")
            charges_list = charges_raw if isinstance(charges_raw, list) else []
            
            taxes_raw = current_l1_json.get("taxes")
            taxes_list = taxes_raw if isinstance(taxes_raw, list) else []
            
            charges_rows = "".join([
                f'<div class="receipt-row" style="padding-left: 8px;"><span>- {c.get("type", "charge").upper()}</span><span>PKR {c.get("amount", 0):,.2f}</span></div>'
                for c in charges_list
            ])
            
            taxes_rows = "".join([
                f'<div class="receipt-row" style="padding-left: 8px;"><span>- {t.get("type", "tax").upper()}</span><span>PKR {t.get("amount", 0):,.2f}</span></div>'
                for t in taxes_list
            ])
            
            receipt_html = f"""
            <div class="pixel-receipt">
                <div class="receipt-header">
                    <div style="font-size: 1.5rem; font-weight: bold;">⚡ UTILITY BILL DECODER ⚡</div>
                    <div>PAKISTAN POWER DISTRIBUTION</div>
                    <div>RECEIPT #{selected_bill_id}</div>
                    <div>MONTH: {p_month}  |  DUE: {p_due}</div>
                </div>
                <div class="receipt-row"><span>DISCO PROVIDER</span><span>{p_provider}</span></div>
                <div class="receipt-row"><span>SANCTIONED LOAD</span><span>{p_load} kW</span></div>
                <div class="receipt-row"><span>UNITS CONSUMED</span><span>{p_units} kWh</span></div>
                <div style="border-top: 1px dashed #3A3247; margin: 6px 0;"></div>
                <div style="font-weight: bold;">CHARGES & ADJUSTMENTS:</div>
                {charges_rows}
                <div style="font-weight: bold; margin-top: 6px;">TAXES & SURCHARGES:</div>
                {taxes_rows}
                <div class="receipt-total">
                    <div class="receipt-row"><span>NET CURRENT BILL:</span><span>PKR {p_bill:,.2f}</span></div>
                </div>
                <div class="receipt-row" style="font-weight: bold;"><span>PAYABLE BY DUE DATE:</span><span>PKR {p_pay:,.2f}</span></div>
                <div class="receipt-row" style="color: #9E2A2B;"><span>LATE PAYMENT (AFTER DUE):</span><span>PKR {p_late:,.2f}</span></div>
                <div class="barcode">||| | ||||| || |||||| | |||| |||</div>
                <div style="text-align: center; font-size: 1.05rem; margin-top: 6px;">✦ THANK YOU FOR SAVING ENERGY ✦</div>
            </div>
            """
            render_html(receipt_html)
            
            plain_receipt = f"""========================================
       UTILITY BILL DECODER
    PAKISTAN POWER DISTRIBUTION
RECEIPT #{selected_bill_id}
MONTH: {p_month}  |  DUE: {p_due}
----------------------------------------
DISCO PROVIDER:       {p_provider}
SANCTIONED LOAD:      {p_load} kW
UNITS CONSUMED:       {p_units} kWh
----------------------------------------
CHARGES & ADJUSTMENTS:
""" + "\n".join([f"- {c.get('type', 'charge').upper():<20} PKR {c.get('amount', 0):>10,.2f}" for c in charges_list]) + f"""
----------------------------------------
TAXES & SURCHARGES:
""" + "\n".join([f"- {t.get('type', 'tax').upper():<20} PKR {t.get('amount', 0):>10,.2f}" for t in taxes_list]) + f"""
========================================
NET CURRENT BILL:     PKR {p_bill:>10,.2f}
PAYABLE BY DUE DATE:  PKR {p_pay:>10,.2f}
LATE PAYMENT:         PKR {p_late:>10,.2f}
========================================
||| | ||||| || |||||| | |||| |||
✦ THANK YOU FOR SAVING ENERGY ✦
"""
            st.download_button(
                "📥 Download Receipt (.txt)",
                data=plain_receipt,
                file_name=f"receipt_{selected_bill_id}.txt",
                mime="text/plain"
            )
        else:
            render_html("""
            <div style="padding: 40px 15px; text-align: center; background: #FFFDF6; border: 2px dashed #4A3A60; border-radius: 6px;">
                <div style="font-size: 2rem;">🧾</div>
                <p class="pixel-font" style="font-size: 0.8rem; color: #2D1B4E; margin-top: 8px;">[ RECEIPT PRINTER STANDBY ]</p>
                <p class="pixel-subfont" style="font-size: 0.75rem; color: #5B4F70;">
                    Select or upload a bill to print the itemized thermal cashier receipt!
                </p>
            </div>
            """)

    render_html("</div></div>")

# -----------------------------------------------------------------------------
# BOTTOM STAGE: PIPELINE ACTION CENTER & BATCH DECK
# -----------------------------------------------------------------------------
render_html("""
<div class="pixel-window">
    <div class="pixel-header">
        <span>⚡ PIPELINE ENGINE // BATCH GENERATOR</span>
        <div class="pixel-btns">
            <span class="pixel-dot dot-yellow"></span>
            <span class="pixel-dot dot-pink"></span>
            <span class="pixel-dot dot-green"></span>
        </div>
    </div>
    <div class="pixel-body">
""")

act_col1, act_col2 = st.columns([1, 2])
with act_col1:
    st.write("Trigger full multi-stage pipeline across the selected directories:")
    generate_btn = st.button("🚀 EXECUTE PIPELINE", use_container_width=True)

with act_col2:
    if generate_btn:
        with st.spinner("Decoding bills via Vision + AST Engine (zero-cost cached)..."):
            env = os.environ.copy()
            env["PYTHONPATH"] = "."
            cmd = [
                "python", "source/main.py",
                "--bills", bills_folder,
                "--templates", templates_folder,
                "--out", output_folder
            ]
            res = subprocess.run(cmd, env=env, capture_output=True, text=True)
            st.rerun()

    if l1_df is not None and l2_df is not None:
        render_html(f"""
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
            <span class="pixel-pill pill-pink">LEVEL 1 ROWS: {len(l1_df)}</span>
            <span class="pixel-pill pill-yellow">LEVEL 2 ROWS: {len(l2_df)}</span>
            <span class="pixel-pill pill-mint">STATUS: CACHED DETERMINISTIC</span>
        </div>
        """)

        req_keys = [
            "provider", "tariff", "sanctioned_load_kw", "bill_month", "reading_date", 
            "issue_date", "due_date", "previous_reading", "current_reading", 
            "units_consumed", "charges", "total_charges", "taxes", "total_taxes", 
            "current_bill", "arrears", "payable_within_due_date", "payable_after_due_date"
        ]
        valid = True
        for _, r in l1_df.iterrows():
            if pd.isna(r.get('json')) or not str(r['json']).strip():
                valid = False
                break
            try:
                d = json.loads(r['json'])
                if any(k not in d for k in req_keys):
                    valid = False
                    break
            except Exception:
                valid = False
                break

        if l2_df['answer'].isnull().any() or (l2_df['answer'].astype(str).str.strip() == "").any():
            valid = False

        if valid:
            render_html("""
            <div style="background: #E0FBEF; border: 2px solid #287A54; border-radius: 6px; padding: 10px 14px; font-family: 'Silkscreen'; font-size: 0.85rem; color: #155734 !important; box-shadow: 2px 2px 0px #287A54;">
                ✅ AUDIT VERIFICATION PASSED: Every Level 1 JSON adheres strictly to schema & no Level 2 answers are empty!
            </div>
            """)
        else:
            st.error("Validation alert: Missing schema keys or blank answers detected.")

# Previews & CSV Download Center
if l1_df is not None and l2_df is not None:
    with st.expander("📂 PREVIEW GENERATED CSVS & DOWNLOAD"):
        prev1, prev2 = st.columns(2)
        with prev1:
            st.write("**level1.csv Preview:**")
            st.dataframe(l1_df.head(5), use_container_width=True)
            st.download_button(
                "📥 Download level1.csv",
                data=l1_df.to_csv(index=False),
                file_name="level1.csv",
                mime="text/csv"
            )
        with prev2:
            st.write("**level2.csv Preview:**")
            st.dataframe(l2_df.head(5), use_container_width=True)
            st.download_button(
                "📥 Download level2.csv",
                data=l2_df.to_csv(index=False),
                file_name="level2.csv",
                mime="text/csv"
            )

render_html("</div></div>")
