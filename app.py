import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
import json
import uuid
from datetime import date
import google.generativeai as genai

st.set_page_config(page_title="Real Estate Pro | מתן משלוף", layout="wide", page_icon="🏠")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ════════════════════════════════════════════════════════════
   GLOBAL
════════════════════════════════════════════════════════════ */
.stApp { background-color: #040c19 !important; }
.main .block-container { padding-top: 1.5rem; }

/* ════════════════════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #040d1e 0%, #071525 50%, #040c19 100%) !important;
    border-right: 1px solid #0d2040 !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] .stRadio div[role="radio"][aria-checked="true"] ~ span {
    color: #60a5fa !important; font-weight: 700 !important;
}

/* ════════════════════════════════════════════════════════════
   TYPOGRAPHY
════════════════════════════════════════════════════════════ */
h1 {
    font-size: 2rem !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #60a5fa 0%, #c084fc 45%, #22d3ee 100%);
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    background-clip: text !important; padding-bottom: 4px;
}
h2 { color: #93c5fd !important; font-weight: 700 !important; }
h3 { color: #a5f3fc !important; font-weight: 600 !important; }
p, li { color: #cbd5e1; }
label { color: #94a3b8 !important; }

/* ════════════════════════════════════════════════════════════
   METRIC CARDS
════════════════════════════════════════════════════════════ */
.metric-card {
    background: linear-gradient(145deg, #0c1b32 0%, #091422 100%);
    border: 1px solid #152d4a;
    border-radius: 18px;
    padding: 24px 18px 20px;
    text-align: center;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(59,130,246,0.12), 0 4px 16px rgba(0,0,0,0.6);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #3b82f6, #a78bfa, #22d3ee);
    border-radius: 18px 18px 0 0;
}
.metric-card .label {
    font-size: 10px; color: #3d5878; margin-bottom: 10px;
    text-transform: uppercase; letter-spacing: 1.4px; font-weight: 700;
}
.metric-card .value {
    font-size: 26px; font-weight: 800; color: #60a5fa; letter-spacing: -0.5px; line-height: 1.1;
}
.metric-card .sub { font-size: 11px; color: #2d4560; margin-top: 7px; font-weight: 500; }

/* ════════════════════════════════════════════════════════════
   SECTION TITLES
════════════════════════════════════════════════════════════ */
.section-title {
    font-size: 13.5px; font-weight: 700; color: #93c5fd;
    letter-spacing: 0.5px; margin: 24px 0 14px 0;
    padding: 10px 16px;
    background: linear-gradient(90deg, rgba(59,130,246,0.10), rgba(59,130,246,0.02));
    border-left: 3px solid #3b82f6;
    border-radius: 0 10px 10px 0;
}

/* ════════════════════════════════════════════════════════════
   ALERTS
════════════════════════════════════════════════════════════ */
.alert-green {
    background: linear-gradient(135deg, rgba(5,46,28,0.85), rgba(6,60,36,0.65));
    border: 1px solid rgba(16,185,129,0.35); border-left: 4px solid #10b981;
    border-radius: 14px; padding: 16px 20px; color: #a7f3d0; margin: 10px 0;
    box-shadow: 0 2px 16px rgba(16,185,129,0.08);
}
.alert-yellow {
    background: linear-gradient(135deg, rgba(45,28,0,0.85), rgba(58,38,0,0.65));
    border: 1px solid rgba(245,158,11,0.35); border-left: 4px solid #f59e0b;
    border-radius: 14px; padding: 16px 20px; color: #fde68a; margin: 10px 0;
    box-shadow: 0 2px 16px rgba(245,158,11,0.08);
}
.alert-red {
    background: linear-gradient(135deg, rgba(45,8,8,0.85), rgba(58,10,10,0.65));
    border: 1px solid rgba(239,68,68,0.35); border-left: 4px solid #ef4444;
    border-radius: 14px; padding: 16px 20px; color: #fecaca; margin: 10px 0;
    box-shadow: 0 2px 16px rgba(239,68,68,0.08);
}

/* ════════════════════════════════════════════════════════════
   COMING SOON
════════════════════════════════════════════════════════════ */
.coming-soon { text-align: center; padding: 80px 20px; color: #1e3050; font-size: 18px; }

/* ════════════════════════════════════════════════════════════
   BUTTONS
════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #1e3fa8, #3b7ef6) !important;
    color: #fff !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 2px 10px rgba(59,130,246,0.2) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #60a5fa) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.4) !important;
    transform: translateY(-1px) !important;
    border-color: rgba(96,165,250,0.4) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #5521c7, #3b82f6) !important;
    border-color: rgba(139,92,246,0.35) !important;
    box-shadow: 0 2px 10px rgba(109,40,217,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9, #60a5fa) !important;
    box-shadow: 0 4px 20px rgba(109,40,217,0.45) !important;
}
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #0d1e36, #152d4a) !important;
    border-color: #1e3a5f !important;
    color: #93c5fd !important;
}

/* ════════════════════════════════════════════════════════════
   INPUTS & SELECTS
════════════════════════════════════════════════════════════ */
input[type="text"], input[type="number"], input[type="password"], textarea {
    background: #061018 !important;
    border: 1px solid #122034 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
input:focus, textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
[data-baseweb="select"] > div {
    background: #061018 !important;
    border-color: #122034 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ════════════════════════════════════════════════════════════
   TABS
════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: #061018 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1px solid #0d2038 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #3d5878 !important;
    font-weight: 600 !important;
    transition: all 0.18s !important;
    padding: 8px 18px !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(59,130,246,0.08) !important;
    color: #93c5fd !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1e3fa8, #3b82f6) !important;
    color: #fff !important;
    box-shadow: 0 2px 10px rgba(59,130,246,0.3) !important;
}

/* ════════════════════════════════════════════════════════════
   EXPANDERS
════════════════════════════════════════════════════════════ */
.stExpander {
    background: #071525 !important;
    border: 1px solid #0d2038 !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
.stExpander:hover { border-color: #1e3a5f !important; }

/* ════════════════════════════════════════════════════════════
   PROGRESS BARS
════════════════════════════════════════════════════════════ */
.stProgress > div > div {
    background: #0a1628 !important;
    border-radius: 8px !important;
    height: 9px !important;
    overflow: hidden !important;
}
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b82f6, #a78bfa, #22d3ee) !important;
    border-radius: 8px !important;
}

/* ════════════════════════════════════════════════════════════
   NATIVE ST.METRIC
════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0b1a30, #091422) !important;
    border: 1px solid #152d4a !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
}
[data-testid="stMetricValue"] { color: #60a5fa !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #3d5878 !important; }
[data-testid="stMetricDelta"] svg { fill: #34d399 !important; }

/* ════════════════════════════════════════════════════════════
   DATAFRAME
════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid #152d4a !important;
}

/* ════════════════════════════════════════════════════════════
   CHAT
════════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: #071525 !important;
    border: 1px solid #0d2038 !important;
    border-radius: 14px !important;
    margin: 4px 0 !important;
}

/* ════════════════════════════════════════════════════════════
   FORMS
════════════════════════════════════════════════════════════ */
[data-testid="stForm"] {
    background: rgba(6,16,32,0.6) !important;
    border: 1px solid #0d2038 !important;
    border-radius: 16px !important;
    padding: 18px !important;
}

/* ════════════════════════════════════════════════════════════
   DIVIDERS & MISC
════════════════════════════════════════════════════════════ */
hr { border-color: #0d2038 !important; margin: 18px 0 !important; }
.stCaption, [data-testid="caption"] { color: #2d4560 !important; }
.stCheckbox label, .stRadio label { color: #94a3b8 !important; }
.stToggle label { color: #94a3b8 !important; }
[data-testid="stAlert"] { border-radius: 12px !important; }

/* ════════════════════════════════════════════════════════════
   SIDEBAR BRAND CARD
════════════════════════════════════════════════════════════ */
.sidebar-brand {
    text-align: center;
    padding: 20px 12px 24px;
    border-bottom: 1px solid #0d2038;
    margin-bottom: 8px;
}
.sidebar-brand .icon { font-size: 40px; line-height: 1; margin-bottom: 10px; }
.sidebar-brand .title {
    font-size: 17px; font-weight: 800;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-brand .sub { font-size: 11px; color: #2d4560 !important; margin-top: 4px; }

/* ════════════════════════════════════════════════════════════
   NAV SECTION HEADERS IN SIDEBAR
════════════════════════════════════════════════════════════ */
.nav-section {
    font-size: 9px; font-weight: 700; letter-spacing: 1.8px;
    color: #1e3a5f !important;
    text-transform: uppercase;
    padding: 14px 12px 4px;
}

/* ════════════════════════════════════════════════════════════
   STAT BADGE CHIPS
════════════════════════════════════════════════════════════ */
.chip {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 700;
    letter-spacing: 0.4px;
}
.chip-blue  { background: rgba(59,130,246,0.15); color: #60a5fa;  border: 1px solid rgba(59,130,246,0.25); }
.chip-green { background: rgba(52,211,153,0.15); color: #34d399;  border: 1px solid rgba(52,211,153,0.25); }
.chip-purple{ background: rgba(167,139,250,0.15);color: #a78bfa;  border: 1px solid rgba(167,139,250,0.25);}
.chip-amber { background: rgba(251,191,36,0.15); color: #fbbf24;  border: 1px solid rgba(251,191,36,0.25); }
.chip-cyan  { background: rgba(34,211,238,0.15); color: #22d3ee;  border: 1px solid rgba(34,211,238,0.25); }
.chip-red   { background: rgba(239,68,68,0.15);  color: #f87171;  border: 1px solid rgba(239,68,68,0.25);  }
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR NAVIGATION ───────────────────────────────────────────────────────
TOOLS = {
    "🏦 מחשבון יכולת רכישה": "calc_power",
    "🔧 מימון מתוחכם": "advanced_financing",
    "📊 ניתוח עסקה": "deal_analysis",
    "⚖️ חוקים ומיסים": "laws_taxes",
    "🎓 מערכת למידה": "learning",
    "🤖 צ'אט AI": "ai_chat",
    "📄 ניתוח חוזים": "contract_analysis",
    "🏛️ רשות המיסים": "tax_authority",
    "👥 מאגר אנשי מקצוע": "professionals",
    "🗄️ מאגר נדל\"ן": "property_db",
    "📁 מאגר חוזים": "contract_library",
    "📋 ניהול עסקה": "deal_mgmt",
}

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="icon">🏠</div>
        <div class="title">Real Estate Pro</div>
        <div class="sub">מתן משלוף · פלטפורמת נדל"ן</div>
    </div>
    <div class="nav-section">כלי חישוב</div>
    """, unsafe_allow_html=True)
    selected_label = st.radio("בחר כלי:", list(TOOLS.keys()), label_visibility="collapsed")
    selected_tool = TOOLS[selected_label]
    st.markdown("""
    <div style="position:absolute;bottom:16px;left:0;right:0;text-align:center;
                font-size:10px;color:#1a2d45;padding:0 12px;">
        © 2026 Real Estate Pro · v2.0
    </div>
    """, unsafe_allow_html=True)


# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def calc_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """החזר חודשי — נוסחת שפיצר"""
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def max_mortgage_from_income(monthly_income: float, annual_rate: float, years: int) -> float:
    """מקסימום משכנתא לפי כושר ההחזר (40% מהכנסה)"""
    max_payment = monthly_income * 0.40
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return max_payment * n
    return max_payment * ((1 + r) ** n - 1) / (r * (1 + r) ** n)


def calc_purchase_tax(price: float, is_first: bool) -> float:
    """מס רכישה לפי מדרגות 2026"""
    if is_first:
        brackets = [
            (1_978_745, 0.00),
            (2_347_040, 0.035),
            (6_055_070, 0.05),
            (20_183_565, 0.08),
            (float("inf"), 0.10),
        ]
    else:
        brackets = [
            (6_055_070, 0.08),
            (float("inf"), 0.10),
        ]
    tax = 0.0
    prev = 0.0
    for ceiling, rate in brackets:
        if price <= prev:
            break
        taxable = min(price, ceiling) - prev
        tax += taxable * rate
        prev = ceiling
    return tax


def fmt(n: float) -> str:
    return f"₪{n:,.0f}"


# ─── TOOL: PURCHASE POWER CALCULATOR ─────────────────────────────────────────

def tool_purchase_power():
    st.title("🏦 מחשבון יכולת רכישה")
    st.caption("חישוב מקסימום רכישה לפי הון עצמי, הכנסה, וערבים — כולל מדרגות מס 2026")

    extended = st.toggle("מצב מורחב", value=False)
    st.divider()

    # ── INPUTS ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        equity = st.number_input("הון עצמי (₪)", min_value=0, step=10_000, value=500_000,
                                 help="כספים נזילים שיש לך — חיסכון, ירושה, מכירת נכס וכו׳")
        income = st.number_input("הכנסה חודשית נטו (₪)", min_value=0, step=500, value=20_000)

    with col2:
        apt_type = st.selectbox("סוג רכישה", ["דירה ראשונה", "דירה נוספת / משקיע"])
        is_first = apt_type == "דירה ראשונה"
        ltv = 0.75 if is_first else 0.50

        has_broker = st.checkbox("יש תיווך (2%)?", value=False)

    # ── EXTENDED INPUTS ───────────────────────────────────────────────────────
    guarantor_income = 0.0
    monthly_expenses = 0.0
    age = 35
    renovation = 0.0
    complementary_mode = "בדוק אוטומטית"

    if extended:
        st.markdown('<div class="section-title">פרטים נוספים</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            age = st.slider("גיל הלווה הראשי", 20, 65, 35)
            monthly_expenses = st.number_input("הוצאות חודשיות קבועות (ללא שכירות/משכנתא) (₪)",
                                               min_value=0, step=500, value=5_000)
        with c2:
            has_guarantor = st.checkbox("האם יש ערבים?")
            if has_guarantor:
                guarantor_income = st.number_input("הכנסת הערבים ברוטו (₪)", min_value=0, step=500, value=15_000)
            renovation = st.number_input("תקציב שיפוץ משוער (₪)", min_value=0, step=5_000, value=0)
            complementary_mode = st.selectbox("הלוואה משלימה", ["בדוק אוטומטית", "כן — כלול בחישוב", "לא"])

    # ── CALCULATIONS ──────────────────────────────────────────────────────────
    INTEREST = 5.5  # ריבית ממוצעת 2026
    max_years = max(10, min(30, 75 - age))  # לא יותר מגיל 75

    effective_income = income + guarantor_income * 0.50  # 50% הכנסת ערב
    available_for_mortgage = effective_income - monthly_expenses

    # משכנתא לפי כושר החזר
    mortgage_by_income = max_mortgage_from_income(available_for_mortgage, INTEREST, max_years)

    # מחיר לפי הון עצמי בלבד (ללא הלוואה משלימה)
    equity_for_purchase = equity - renovation
    price_by_equity = equity_for_purchase / (1 - ltv)
    mortgage_by_equity = price_by_equity * ltv

    # ממשב: לוקחים את המינימום
    max_mortgage = min(mortgage_by_income, mortgage_by_equity)
    max_price_base = equity_for_purchase + max_mortgage

    # בדיקת הלוואה משלימה
    monthly_payment_base = calc_mortgage_payment(max_mortgage, INTEREST, max_years)
    monthly_surplus = available_for_mortgage - monthly_payment_base - monthly_expenses

    suggest_complementary = False
    complementary_amount = 0.0
    max_price_with_comp = max_price_base

    if complementary_mode in ("בדוק אוטומטית", "כן — כלול בחישוב"):
        surplus_after = effective_income - monthly_payment_base - monthly_expenses
        if surplus_after > 2_000 or complementary_mode == "כן — כלול בחישוב":
            suggest_complementary = True
            # הלוואה משלימה: עד 5 שנים, ריבית 6%
            comp_max_payment = max(0, surplus_after - 2_000)
            complementary_amount = max_mortgage_from_income(comp_max_payment, 6.0, 5)
            complementary_amount = min(complementary_amount, equity * 0.30)  # עד 30% מהון
            max_price_with_comp = equity_for_purchase + max_mortgage + complementary_amount

    # עלויות נלוות
    final_price = max_price_with_comp if suggest_complementary else max_price_base
    purchase_tax = calc_purchase_tax(final_price, is_first)
    lawyer_fee = final_price * 0.005
    broker_fee = final_price * 0.02 if has_broker else 0
    total_additional = purchase_tax + lawyer_fee + broker_fee + renovation
    equity_needed = final_price * (1 - ltv) + total_additional

    # ── OUTPUT ────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("## 📊 תוצאות החישוב")

    # כרטיסי מדד ראשיים
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">מחיר מקסימלי לרכישה</div>
            <div class="value">{fmt(final_price)}</div>
            <div class="sub">לפי {'הלוואה משלימה' if suggest_complementary else 'הון עצמי + משכנתא'}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">גובה משכנתא</div>
            <div class="value">{fmt(max_mortgage)}</div>
            <div class="sub">LTV {ltv*100:.0f}% · {max_years} שנה</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        monthly_total = calc_mortgage_payment(max_mortgage, INTEREST, max_years)
        if suggest_complementary and complementary_amount > 0:
            monthly_total += calc_mortgage_payment(complementary_amount, 6.0, 5)
        st.markdown(f"""<div class="metric-card">
            <div class="label">החזר חודשי כולל</div>
            <div class="value">{fmt(monthly_total)}</div>
            <div class="sub">{monthly_total / effective_income * 100:.0f}% מההכנסה הפנויה</div>
        </div>""", unsafe_allow_html=True)

    # הלוואה משלימה
    if suggest_complementary and complementary_amount > 0:
        st.markdown(f"""<div class="alert-green">
            💡 <strong>המלצה: הלוואה משלימה</strong><br>
            לפי חישוב, ביכולתך לקחת הלוואה משלימה של <strong>{fmt(complementary_amount)}</strong> (5 שנים, ריבית ~6%)<br>
            זה מגדיל את כוח הקנייה שלך ב-{fmt(complementary_amount)} — סה"כ <strong>{fmt(final_price)}</strong>
        </div>""", unsafe_allow_html=True)

    # מד בריאות פיננסית
    if extended:
        ratio = monthly_total / effective_income
        health = 1 - min(ratio / 0.50, 1.0)
        st.divider()
        st.markdown("**מד בריאות פיננסית**")
        st.progress(health)
        level = "🟢 מצוין" if ratio < 0.30 else "🟡 סביר" if ratio < 0.40 else "🔴 גבוה — מומלץ להוריד"
        st.caption(f"יחס החזר להכנסה: {ratio*100:.1f}% — {level}")

    # פירוט עלויות
    st.divider()
    st.markdown('<div class="section-title">פירוט עלויות נלוות</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**מס רכישה ({apt_type})**")
        if extended:
            # פירוט מדרגות
            brackets_first = [
                (1_978_745, 2_347_040, 0.035),
                (2_347_040, 6_055_070, 0.05),
                (6_055_070, 20_183_565, 0.08),
                (20_183_565, float("inf"), 0.10),
            ]
            brackets_investor = [
                (0, 6_055_070, 0.08),
                (6_055_070, float("inf"), 0.10),
            ]
            if is_first:
                st.caption("0% עד 1,978,745 | 3.5% עד 2,347,040 | 5% עד 6,055,070 | 8%+ מעלה")
            else:
                st.caption("8% עד 6,055,070 | 10% מעלה")
        st.metric("", fmt(purchase_tax))

    with col_b:
        rows = {"שכ\"ט עו\"ד (~0.5%)": fmt(lawyer_fee)}
        if has_broker:
            rows["תיווך (2%)"] = fmt(broker_fee)
        if renovation > 0:
            rows["שיפוץ"] = fmt(renovation)
        rows["**סה\"כ נלוות**"] = fmt(total_additional)
        for k, v in rows.items():
            c1b, c2b = st.columns([3, 1])
            c1b.markdown(k)
            c2b.markdown(f"**{v}**")

    # הון עצמי נדרש vs. זמין
    st.divider()
    deficit = equity_needed - equity
    if deficit > 0:
        st.markdown(f"""<div class="alert-red">
            ⚠️ <strong>חסר {fmt(deficit)} בהון העצמי</strong><br>
            נדרש {fmt(equity_needed)} אך יש {fmt(equity)}.<br>
            שקול: הפחתת מחיר היעד / הלוואת משפחה / ערבים נוספים.
        </div>""", unsafe_allow_html=True)
    else:
        leftover = equity - equity_needed
        st.markdown(f"""<div class="alert-green">
            ✅ <strong>ההון העצמי מספיק</strong> — נשאר ביד {fmt(leftover)} אחרי כל ההוצאות
        </div>""", unsafe_allow_html=True)

    if extended and guarantor_income > 0:
        st.divider()
        st.markdown('<div class="section-title">פירוט חישוב הכנסה</div>', unsafe_allow_html=True)
        rows2 = {
            "הכנסה עצמית": fmt(income),
            f"50% הכנסת ערב ({fmt(guarantor_income)})": fmt(guarantor_income * 0.50),
            "הכנסה פנויה לחישוב": fmt(effective_income),
            f"פחות הוצאות חודשיות": f"- {fmt(monthly_expenses)}",
            "**בסיס לחישוב משכנתא**": fmt(available_for_mortgage),
        }
        for k, v in rows2.items():
            ca, cb = st.columns([3, 1])
            ca.markdown(k)
            cb.markdown(f"**{v}**")

    st.caption("⚠️ החישוב הוא אינדיקטיבי בלבד. יש להתייעץ עם יועץ משכנתאות מוסמך.")


# ─── TOOL: ADVANCED FINANCING ────────────────────────────────────────────────

TRACK_TYPES = [
    "קבועה לא צמודה (קל\"צ)",
    "קבועה צמודה למדד (קצ\"מ)",
    "פריים",
    "משתנה כל 5 שנים",
]
TRACK_COLORS = ["#60a5fa", "#34d399", "#fbbf24"]
TRACK_NAMES  = ["מסלול א׳", "מסלול ב׳", "מסלול ג׳"]


def build_amortization_schedule(
    principal: float,
    annual_rate_pct: float,
    years: int,
    cpi_annual_pct: float = 0.0,
    variable_changes: list = None,
) -> list:
    """
    Build full monthly amortization schedule (Shpitzer / שפיצר).
    variable_changes : list of (start_month, new_annual_rate_pct) – for variable-rate tracks.
    cpi_annual_pct   : annual CPI estimate for CPI-indexed tracks.
    """
    n = years * 12
    if n <= 0 or principal <= 0:
        return []

    r_base = annual_rate_pct / 100 / 12
    cpi_m  = (1 + cpi_annual_pct / 100) ** (1 / 12) - 1 if cpi_annual_pct > 0 else 0.0

    rate_schedule = [r_base] * n
    if variable_changes:
        for (start_m, new_rate_pct) in sorted(variable_changes):
            for idx in range(max(0, start_m - 1), n):
                rate_schedule[idx] = new_rate_pct / 100 / 12

    balance = principal
    rows = []
    for i in range(n):
        r = rate_schedule[i]
        remaining = n - i
        if r == 0:
            payment = balance / remaining
        else:
            payment = balance * (r * (1 + r) ** remaining) / ((1 + r) ** remaining - 1)

        interest_pmt  = balance * r
        principal_pmt = payment - interest_pmt
        balance       = max(0.0, balance - principal_pmt)

        if cpi_m > 0:
            balance *= (1 + cpi_m)

        rows.append({
            "month":     i + 1,
            "year":      i // 12 + 1,
            "payment":   round(payment, 2),
            "principal": round(principal_pmt, 2),
            "interest":  round(interest_pmt, 2),
            "balance":   round(balance, 2),
        })
    return rows


def combine_schedules(schedules: list) -> list:
    """Sum multiple track schedules month-by-month into one combined schedule."""
    if not schedules:
        return []
    max_months = max(len(s) for s in schedules)
    combined = []
    for i in range(max_months):
        row = {"month": i + 1, "year": i // 12 + 1,
               "payment": 0.0, "principal": 0.0, "interest": 0.0, "balance": 0.0}
        for sched in schedules:
            if i < len(sched):
                row["payment"]   += sched[i]["payment"]
                row["principal"] += sched[i]["principal"]
                row["interest"]  += sched[i]["interest"]
                row["balance"]   += sched[i]["balance"]
        combined.append(row)
    return combined


def _plotly_dark_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(color="#93c5fd", size=15, family="Arial")),
        paper_bgcolor="#040c19", plot_bgcolor="#061018",
        font=dict(color="#94a3b8", family="Arial"),
        xaxis=dict(gridcolor="#0d2038", title="חודש", color="#4a6080", linecolor="#0d2038"),
        yaxis=dict(gridcolor="#0d2038", title="₪", color="#4a6080", linecolor="#0d2038"),
        legend=dict(bgcolor="#071525", bordercolor="#152d4a", borderwidth=1),
        margin=dict(l=10, r=10, t=44, b=10),
    )


def tool_advanced_financing():
    st.title("🔧 מימון מתוחכם")
    st.caption("מחשבון משכנתא מקצועי — לוח סילוקין, עד 3 מסלולים, גרפים ופירעון מוקדם")

    # ── TOP INPUTS ────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        total_loan = st.number_input(
            "סכום משכנתא כולל (₪)", min_value=100_000, max_value=10_000_000,
            step=50_000, value=1_500_000)
    with col2:
        num_tracks = st.selectbox("מספר מסלולים", [1, 2, 3], index=1)
    with col3:
        income_check = st.number_input(
            "הכנסה חודשית נטו לבדיקת יחס (₪, אופציונלי)",
            min_value=0, step=1_000, value=0)

    st.divider()
    st.markdown('<div class="section-title">הגדרת מסלולים</div>', unsafe_allow_html=True)

    # ── PER-TRACK INPUTS ──────────────────────────────────────────────────────
    default_splits = {1: [100], 2: [60, 40], 3: [33, 33, 34]}
    track_configs  = []
    cols           = st.columns(num_tracks)
    amounts_so_far = 0

    for idx in range(num_tracks):
        with cols[idx]:
            color = TRACK_COLORS[idx]
            st.markdown(
                f"<div style='color:{color};font-weight:700;font-size:16px'>{TRACK_NAMES[idx]}</div>",
                unsafe_allow_html=True)

            default_pct = default_splits[num_tracks][idx]
            default_amt = int(total_loan * default_pct / 100)
            if idx == num_tracks - 1:
                default_amt = max(0, total_loan - amounts_so_far)

            amount = st.number_input(
                "סכום (₪)", min_value=0, max_value=int(total_loan),
                step=10_000, value=default_amt, key=f"amt_{idx}")
            track_type = st.selectbox("סוג מסלול", TRACK_TYPES, key=f"type_{idx}")
            rate   = st.slider("ריבית שנתית (%)", 0.0, 15.0, 5.5, 0.1, key=f"rate_{idx}")
            years  = st.slider("תקופה (שנים)",    1,   20,   20,       key=f"years_{idx}")

            cpi              = 0.0
            variable_changes = None

            if "צמודה" in track_type:
                cpi = st.slider("הנחת מדד שנתי (%)", 0.0, 5.0, 2.5, 0.1, key=f"cpi_{idx}")

            if "פריים" in track_type or "משתנה" in track_type:
                stress = st.slider("תרחיש עלייה (%+)", 0.0, 5.0, 1.0, 0.5, key=f"stress_{idx}")
                if "5 שנים" in track_type:
                    variable_changes = [
                        (60 * k + 1, rate + stress)
                        for k in range(1, years // 5 + 1)
                    ]

            track_configs.append(dict(
                name=TRACK_NAMES[idx], color=color,
                amount=amount, type=track_type,
                rate=rate, years=years,
                cpi=cpi, variable_changes=variable_changes,
            ))
            amounts_so_far += amount

    total_configured = sum(tc["amount"] for tc in track_configs)
    if abs(total_configured - total_loan) > 500:
        st.warning(f"⚠️ סכום המסלולים ({fmt(total_configured):}) שונה מסכום המשכנתא ({fmt(total_loan)})")

    # ── BUILD SCHEDULES ───────────────────────────────────────────────────────
    schedules = []
    for tc in track_configs:
        if tc["amount"] > 0:
            schedules.append(build_amortization_schedule(
                tc["amount"], tc["rate"], tc["years"],
                cpi_annual_pct=tc["cpi"],
                variable_changes=tc["variable_changes"],
            ))
        else:
            schedules.append([])

    valid_schedules = [s for s in schedules if s]
    combined        = combine_schedules(valid_schedules)

    if not combined:
        st.info("הזן נתונים כדי לראות תוצאות.")
        return

    total_paid       = sum(r["payment"]   for r in combined)
    total_interest   = sum(r["interest"]  for r in combined)
    first_payment    = combined[0]["payment"]
    max_months       = len(combined)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 סיכום", "📋 לוח סילוקין", "📈 גרפים", "🔄 פירעון מוקדם"])

    # ────────── TAB 1: SUMMARY ────────────────────────────────────────────────
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            ("החזר חודשי התחלתי",    fmt(first_payment),          "חודש ראשון"),
            ("סה\"כ ריבית",           fmt(total_interest),          f"{total_interest/total_loan*100:.0f}% מהקרן"),
            ("עלות כוללת",            fmt(total_paid),              "קרן + ריבית"),
            ("תקופה מקסימלית",        f"{max_months // 12} שנים",  f"{max_months} תשלומים"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4], cards):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value">{value}</div>
                    <div class="sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        if income_check > 0:
            ratio     = first_payment / income_check
            level_txt = "🟢 תקין" if ratio < 0.30 else "🟡 גבוה" if ratio < 0.40 else "🔴 גבוה מאוד"
            cls       = "alert-green" if ratio < 0.30 else "alert-yellow" if ratio < 0.40 else "alert-red"
            st.markdown(f"""<div class="{cls}" style="margin-top:15px">
                {level_txt} &nbsp; יחס החזר להכנסה: <strong>{ratio*100:.1f}%</strong>
                ({fmt(first_payment)} מתוך {fmt(income_check)})
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="section-title">השוואת מסלולים</div>', unsafe_allow_html=True)

        rows_comp = []
        for tc, sched in zip(track_configs, schedules):
            if sched:
                rows_comp.append({
                    "מסלול":         tc["name"],
                    "סוג":           tc["type"],
                    "סכום":          fmt(tc["amount"]),
                    "ריבית":         f"{tc['rate']}%",
                    "תקופה":         f"{tc['years']} שנ׳",
                    "החזר חודשי":    fmt(sched[0]["payment"]),
                    "סה\"כ ריבית":   fmt(sum(r["interest"] for r in sched)),
                    "עלות כוללת":    fmt(sum(r["payment"]  for r in sched)),
                })
        if rows_comp:
            st.dataframe(pd.DataFrame(rows_comp), use_container_width=True, hide_index=True)

    # ────────── TAB 2: AMORTIZATION TABLE ────────────────────────────────────
    with tab2:
        view_mode = st.radio("תצוגה", ["לפי שנה (מקוצר)", "כל החודשים"], horizontal=True)

        if view_mode == "כל החודשים":
            display_rows = combined
        else:
            yearly: dict = {}
            for r in combined:
                y = r["year"]
                if y not in yearly:
                    yearly[y] = {"year": y, "payment": 0.0, "principal": 0.0,
                                 "interest": 0.0, "balance": 0.0}
                yearly[y]["payment"]   += r["payment"]
                yearly[y]["principal"] += r["principal"]
                yearly[y]["interest"]  += r["interest"]
                yearly[y]["balance"]    = r["balance"]
            display_rows = list(yearly.values())

        table_data = []
        for r in display_rows:
            row = {}
            if view_mode == "כל החודשים":
                row["חודש"] = r["month"]
                row["שנה"]  = r["year"]
            else:
                row["שנה"] = r["year"]
            row["תשלום"]     = fmt(r["payment"])
            row["קרן"]       = fmt(r["principal"])
            row["ריבית"]     = fmt(r["interest"])
            row["יתרת חוב"] = fmt(r["balance"])
            table_data.append(row)

        st.dataframe(pd.DataFrame(table_data), use_container_width=True,
                     hide_index=True, height=420)

        csv_bytes = pd.DataFrame([{
            "חודש": r["month"], "שנה": r["year"],
            "תשלום": r["payment"], "קרן": r["principal"],
            "ריבית": r["interest"], "יתרת חוב": r["balance"],
        } for r in combined]).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

        st.download_button(
            label="⬇️ הורד לוח סילוקין (CSV)",
            data=csv_bytes,
            file_name="לוח_סילוקין.csv",
            mime="text/csv",
        )

    # ────────── TAB 3: CHARTS ─────────────────────────────────────────────────
    with tab3:
        months     = [r["month"]    for r in combined]
        balances   = [r["balance"]  for r in combined]
        principals = [r["principal"] for r in combined]
        interests  = [r["interest"] for r in combined]

        # Chart 1 – Remaining balance
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=months, y=balances, mode="lines", name="יתרת חוב",
            fill="tozeroy", fillcolor="rgba(96,165,250,0.15)",
            line=dict(color="#60a5fa", width=2),
        ))
        if num_tracks > 1:
            for tc, sched in zip(track_configs, schedules):
                if sched:
                    fig1.add_trace(go.Scatter(
                        x=[r["month"]   for r in sched],
                        y=[r["balance"] for r in sched],
                        mode="lines", name=tc["name"],
                        line=dict(color=tc["color"], width=1.5, dash="dash"),
                    ))
        fig1.update_layout(**_plotly_dark_layout("יתרת חוב לאורך הזמן"))
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2 – Principal vs Interest breakdown
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months, y=interests, mode="lines", name="ריבית",
            fill="tozeroy", fillcolor="rgba(248,113,113,0.25)",
            line=dict(color="#f87171", width=2),
        ))
        fig2.add_trace(go.Scatter(
            x=months, y=principals, mode="lines", name="קרן",
            fill="tozeroy", fillcolor="rgba(52,211,153,0.25)",
            line=dict(color="#34d399", width=2),
        ))
        fig2.update_layout(**_plotly_dark_layout("פירוט תשלום חודשי — קרן מול ריבית"))
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3 – Monthly payment per track (only if multiple tracks)
        if num_tracks > 1:
            fig3 = go.Figure()
            for tc, sched in zip(track_configs, schedules):
                if sched:
                    fig3.add_trace(go.Scatter(
                        x=[r["month"]   for r in sched],
                        y=[r["payment"] for r in sched],
                        mode="lines", name=tc["name"],
                        line=dict(color=tc["color"], width=2),
                    ))
            fig3.update_layout(**_plotly_dark_layout("החזר חודשי לפי מסלול"))
            st.plotly_chart(fig3, use_container_width=True)

    # ────────── TAB 4: EARLY REPAYMENT ───────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">סימולטור פירעון מוקדם</div>',
                    unsafe_allow_html=True)
        st.caption("חשב כמה תחסוך אם תעשה פירעון חד-פעמי או תגדיל את ההחזר החודשי")

        ca, cb = st.columns(2)
        with ca:
            early_month = st.slider("בחודש מספר", 1, max_months, min(12, max_months))
            lump_sum    = st.number_input("פירעון חד-פעמי (₪)", min_value=0,
                                          step=10_000, value=100_000)
        with cb:
            extra_monthly = st.number_input("תוספת להחזר חודשי (₪)", min_value=0,
                                             step=500, value=0)

        if lump_sum > 0 or extra_monthly > 0:
            idx_row    = early_month - 1
            balance_at = combined[idx_row]["balance"]
            new_balance = max(0.0, balance_at - lump_sum)

            remaining_orig = max_months - idx_row
            orig_interest_remaining = sum(r["interest"] for r in combined[idx_row:])

            # Weighted average rate across active tracks
            active_amount = sum(tc["amount"] for tc in track_configs if tc["amount"] > 0)
            avg_rate = (
                sum(tc["rate"] * tc["amount"] for tc in track_configs if tc["amount"] > 0)
                / active_amount
            ) if active_amount > 0 else 5.5

            r_m = avg_rate / 100 / 12
            base_payment = combined[idx_row]["payment"] + extra_monthly

            if r_m > 0 and base_payment > new_balance * r_m:
                new_months = math.ceil(
                    -math.log(1 - new_balance * r_m / base_payment) / math.log(1 + r_m)
                )
            else:
                new_months = remaining_orig

            new_months = min(new_months, remaining_orig)

            if r_m > 0 and new_months > 0:
                new_payment        = new_balance * (r_m * (1 + r_m) ** new_months) / ((1 + r_m) ** new_months - 1)
                new_total_interest = new_payment * new_months - new_balance
            else:
                new_total_interest = 0.0

            months_saved   = remaining_orig - new_months
            interest_saved = max(0.0, orig_interest_remaining - new_total_interest)

            st.divider()
            c1, c2, c3 = st.columns(3)
            ep_cards = [
                ("יתרת חוב לאחר פירעון", fmt(new_balance), f"הייתה {fmt(balance_at)}"),
                ("חודשים שחסכת",          str(max(0, months_saved)),
                 f"{max(0,months_saved)//12} שנ׳ ו-{max(0,months_saved)%12} חודשים"),
                ("ריבית שחסכת (משוער)",   fmt(interest_saved), "הערכה בלבד"),
            ]
            for col, (label, value, sub) in zip([c1, c2, c3], ep_cards):
                with col:
                    st.markdown(f"""<div class="metric-card">
                        <div class="label">{label}</div>
                        <div class="value">{value}</div>
                        <div class="sub">{sub}</div>
                    </div>""", unsafe_allow_html=True)

            st.caption("⚠️ בפועל יש עמלת פירעון מוקדם לפי תקנות בנק ישראל — יש לבדוק מול הבנק.")

    st.caption("⚠️ כל החישובים אינדיקטיביים בלבד. יש להתייעץ עם יועץ משכנתאות מוסמך.")


# ─── TOOL: DEAL ANALYSIS ─────────────────────────────────────────────────────

def _score_deal(gross_yield, net_yield, cash_on_cash, monthly_cashflow, ltv_pct):
    """Return (total_score 0-100, breakdown list)."""
    score = 0
    breakdown = []

    def _pts(value, thresholds, label, display):
        # thresholds: [(min_val, points), ...] descending
        p = 0
        for threshold, pts in thresholds:
            if value >= threshold:
                p = pts
                break
        return p, (label, p, 20, display)

    rules = [
        ("תשואה ברוטו",     gross_yield,       [(7, 20), (5, 15), (4, 8), (0, 0)],  f"{gross_yield:.1f}%"),
        ("תשואה נטו",       net_yield,         [(5, 20), (3.5, 15), (2.5, 8), (0, 0)], f"{net_yield:.1f}%"),
        ("תשואה על ההון",   cash_on_cash,      [(8, 20), (5, 15), (3, 8), (0, 0)],  f"{cash_on_cash:.1f}%"),
        ("תזרים חודשי",     monthly_cashflow,  [(2000, 20), (500, 15), (0, 8), (-9999, 0)], fmt(monthly_cashflow)),
        ("מינוף (LTV)",     100 - ltv_pct,     [(50, 20), (35, 15), (25, 8), (0, 0)], f"LTV {ltv_pct:.0f}%"),
    ]
    for label, value, thresholds, display in rules:
        p, row = _pts(value, thresholds, label, display)
        score += p
        breakdown.append(row)

    return score, breakdown


def tool_deal_analysis():
    st.title("📊 ניתוח עסקה")
    st.caption("ניתוח מקצועי — תשואות, תזרים, תרחישים, מחשבון יציאה ושמירת עסקאות")

    if "saved_deals" not in st.session_state:
        st.session_state["saved_deals"] = []

    # ── 1. PROPERTY DETAILS ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">📍 פרטי הנכס</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        deal_name = st.text_input("שם העסקה", value="דירה חדשה")
        prop_type = st.selectbox("סוג נכס", ["דירה להשקעה", "דירה ראשונה", "נכס מסחרי", "קרקע", "אחר"])
    with c2:
        price     = st.number_input("מחיר רכישה (₪)", min_value=100_000, max_value=50_000_000,
                                    step=50_000, value=2_000_000)
        size_sqm  = st.number_input("גודל (מ\"ר)", min_value=10, max_value=1_000, step=5, value=80)
    with c3:
        is_first      = st.selectbox("סוג רכישה", ["דירה ראשונה", "דירה נוספת / משקיע"]) == "דירה ראשונה"
        has_broker_in = st.checkbox("תיווך ברכישה (2%)?", value=False)
    st.caption(f"מחיר למ\"ר: {fmt(price / size_sqm if size_sqm else 0)}")

    # ── 2. ENTRY COSTS ────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">💸 עלויות כניסה</div>', unsafe_allow_html=True)
    purchase_tax = calc_purchase_tax(price, is_first)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("מס רכישה (אוטומטי)", fmt(purchase_tax))
    with c2:
        lawyer_fee  = st.number_input("שכ\"ט עו\"ד (₪)", min_value=0, step=1_000,
                                      value=int(price * 0.005))
    with c3:
        broker_fee  = st.number_input("תיווך (₪)", min_value=0, step=1_000,
                                      value=int(price * 0.02) if has_broker_in else 0)
    with c4:
        renovation  = st.number_input("שיפוץ (₪)", min_value=0, step=5_000, value=0)

    total_entry = purchase_tax + lawyer_fee + broker_fee + renovation
    st.markdown(f"**סה\"כ עלויות כניסה: {fmt(total_entry)}**")

    # ── 3. FINANCING ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">🏦 מימון</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        mortgage       = st.number_input("סכום משכנתא (₪)", min_value=0, max_value=int(price),
                                         step=50_000, value=int(price * 0.60))
    with c2:
        mortgage_rate  = st.slider("ריבית (%)", 0.0, 12.0, 5.5, 0.1)
    with c3:
        mortgage_years = st.slider("תקופה (שנים)", 5, 30, 25)

    equity           = price + total_entry - mortgage
    monthly_mortgage = calc_mortgage_payment(mortgage, mortgage_rate, mortgage_years) if mortgage > 0 else 0.0
    ltv_pct          = mortgage / price * 100 if price > 0 else 0.0

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("הון עצמי נדרש",  fmt(equity))
    with c2: st.metric("החזר חודשי",     fmt(monthly_mortgage))
    with c3: st.metric("LTV",            f"{ltv_pct:.0f}%")

    # ── 4. INCOME ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">💰 הכנסות</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        monthly_rent      = st.number_input("שכ\"ד חודשי (₪)", min_value=0, step=200, value=6_500)
    with c2:
        occupancy_pct     = st.slider("תפוסה (%)", 50, 100, 95)
    with c3:
        appreciation_pct  = st.slider("עליית ערך שנתית (%)", 0.0, 10.0, 3.0, 0.5)

    effective_rent = monthly_rent * occupancy_pct / 100
    annual_rent    = effective_rent * 12

    # ── 5. RUNNING EXPENSES ───────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">🔧 הוצאות שוטפות (חודשי)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: hoa_fee          = st.number_input("ועד בית (₪)",    min_value=0, step=50,  value=300)
    with c2: prop_tax_monthly = st.number_input("ארנונה (₪)",     min_value=0, step=100, value=0)
    with c3: insurance        = st.number_input("ביטוח (₪)",      min_value=0, step=50,  value=150)
    with c4: mgmt_pct         = st.slider("ניהול (% שכ\"ד)", 0.0, 10.0, 0.0, 0.5)

    mgmt_fee               = monthly_rent * mgmt_pct / 100
    total_monthly_expenses = hoa_fee + prop_tax_monthly + insurance + mgmt_fee
    annual_expenses        = total_monthly_expenses * 12

    # ── CORE CALCULATIONS ─────────────────────────────────────────────────────
    monthly_cashflow = effective_rent - monthly_mortgage - total_monthly_expenses
    annual_cashflow  = monthly_cashflow * 12
    annual_net_income = annual_rent - annual_expenses
    gross_yield      = annual_rent / price * 100 if price > 0 else 0.0
    net_yield        = annual_net_income / price * 100 if price > 0 else 0.0
    cash_on_cash     = annual_cashflow / equity * 100 if equity > 0 else 0.0

    score, score_breakdown = _score_deal(gross_yield, net_yield, cash_on_cash,
                                         monthly_cashflow, ltv_pct)

    # ── RESULTS HEADER ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("## 📊 תוצאות הניתוח")

    score_color = "#60a5fa" if score >= 70 else "#fbbf24" if score >= 50 else "#f87171"
    score_label = "🟢 עסקה טובה" if score >= 70 else "🟡 עסקה סבירה" if score >= 50 else "🔴 עסקה חלשה"

    col_score, col_kpis = st.columns([1, 3])
    with col_score:
        st.markdown(f"""<div class="metric-card" style="border-color:{score_color}">
            <div class="label">ציון עסקה</div>
            <div class="value" style="color:{score_color};font-size:52px">{score}</div>
            <div class="sub">{score_label}</div>
        </div>""", unsafe_allow_html=True)
        st.progress(score / 100)

    with col_kpis:
        kpi_cards = [
            ("תשואה ברוטו",     f"{gross_yield:.2f}%",     f"{fmt(annual_rent)} שנתי"),
            ("תשואה נטו",       f"{net_yield:.2f}%",       f"{fmt(annual_net_income)} נטו"),
            ("תשואה על ההון",   f"{cash_on_cash:.2f}%",    "Cash-on-Cash"),
            ("תזרים חודשי",     fmt(monthly_cashflow),
             "🟢 חיובי" if monthly_cashflow >= 0 else "🔴 שלילי"),
        ]
        r1, r2, r3, r4 = st.columns(4)
        for col, (label, value, sub) in zip([r1, r2, r3, r4], kpi_cards):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value" style="font-size:22px">{value}</div>
                    <div class="sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

    with st.expander("🔍 פירוט ציון העסקה"):
        for label, pts, max_pts, val in score_breakdown:
            ca, cb, cc = st.columns([3, 1, 2])
            ca.markdown(f"**{label}** — {val}")
            cb.markdown(f"**{pts}/{max_pts}**")
            cc.progress(pts / max_pts if max_pts > 0 else 0)

    # ── DETAIL TABS ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 פירוט פיננסי", "🎭 תרחישים", "🚪 מחשבון יציאה", "💾 שמור ושתף"])

    # ── TAB 1: FINANCIAL BREAKDOWN ────────────────────────────────────────────
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">עלויות כניסה</div>', unsafe_allow_html=True)
            entry_rows = {
                "מחיר רכישה":           fmt(price),
                "מס רכישה":             fmt(purchase_tax),
                "שכ\"ט עו\"ד":          fmt(lawyer_fee),
                "תיווך":                fmt(broker_fee),
                "שיפוץ":                fmt(renovation),
                "**סה\"כ השקעה**":      fmt(price + total_entry),
            }
            for k, v in entry_rows.items():
                ca, cb = st.columns([3, 1]); ca.markdown(k); cb.markdown(f"**{v}**")

        with c2:
            st.markdown('<div class="section-title">תזרים חודשי</div>', unsafe_allow_html=True)
            cf_rows = {
                f"שכ\"ד ({occupancy_pct}% תפוסה)": fmt(effective_rent),
                "פחות: משכנתא":          f"- {fmt(monthly_mortgage)}",
                "פחות: ועד בית":         f"- {fmt(hoa_fee)}",
                "פחות: ביטוח":           f"- {fmt(insurance)}",
                "פחות: ארנונה":          f"- {fmt(prop_tax_monthly)}",
                "פחות: ניהול":           f"- {fmt(mgmt_fee)}",
                f"**תזרים נטו**":        f"**{fmt(monthly_cashflow)}**",
            }
            for k, v in cf_rows.items():
                ca, cb = st.columns([3, 1]); ca.markdown(k); cb.markdown(v)

        # 10-year cashflow chart
        st.divider()
        yrs = list(range(1, 11))
        cum_cf = []
        running = 0.0
        for y in yrs:
            yr_rent     = monthly_rent * (occupancy_pct / 100) * 12 * (1.02 ** (y - 1))
            yr_expenses = annual_expenses * (1.02 ** (y - 1))
            running    += yr_rent - yr_expenses - monthly_mortgage * 12
            cum_cf.append(running)

        fig_cf = go.Figure()
        colors_cf = ["#34d399" if v >= 0 else "#f87171" for v in cum_cf]
        fig_cf.add_trace(go.Bar(x=yrs, y=cum_cf, name="תזרים מצטבר",
                                marker_color=colors_cf))
        fig_cf.update_layout(**_plotly_dark_layout("תזרים מצטבר — 10 שנים"))
        fig_cf.update_layout(xaxis_title="שנה")
        st.plotly_chart(fig_cf, use_container_width=True)

    # ── TAB 2: SCENARIOS ──────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">השוואת תרחישים</div>', unsafe_allow_html=True)

        scenarios = {
            "🔴 פסימי":  {"rent_m": 0.85, "occ": 85,          "rate_d": +1.0, "appr_d": -2.0},
            "🟡 בסיסי":  {"rent_m": 1.00, "occ": occupancy_pct,"rate_d":  0.0, "appr_d":  0.0},
            "🟢 אופטימי":{"rent_m": 1.15, "occ": 97,           "rate_d": -0.5, "appr_d": +2.0},
        }

        sc_rows = []
        for sc_name, s in scenarios.items():
            s_rent     = monthly_rent * s["rent_m"] * s["occ"] / 100
            s_rate     = max(1.0, mortgage_rate + s["rate_d"])
            s_mm       = calc_mortgage_payment(mortgage, s_rate, mortgage_years) if mortgage > 0 else 0.0
            s_cf       = s_rent - s_mm - total_monthly_expenses
            s_gross    = s_rent * 12 / price * 100 if price > 0 else 0
            s_net      = (s_rent * 12 - annual_expenses) / price * 100 if price > 0 else 0
            s_coc      = s_cf * 12 / equity * 100 if equity > 0 else 0
            s_score, _ = _score_deal(s_gross, s_net, s_coc, s_cf, ltv_pct)
            sc_rows.append({
                "תרחיש":         sc_name,
                "שכ\"ד חודשי":  fmt(s_rent),
                "ריבית":         f"{s_rate:.1f}%",
                "תזרים חודשי":  fmt(s_cf),
                "תשואה ברוטו":  f"{s_gross:.1f}%",
                "תשואה נטו":    f"{s_net:.1f}%",
                "Cash-on-Cash":  f"{s_coc:.1f}%",
                "ציון":          s_score,
            })
        st.dataframe(pd.DataFrame(sc_rows), use_container_width=True, hide_index=True)

        # Sensitivity table: rent rows × interest rate columns
        st.divider()
        st.markdown('<div class="section-title">טבלת רגישות — תזרים חודשי (שכ"ד מול ריבית)</div>',
                    unsafe_allow_html=True)
        rent_mults  = [0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30]
        rate_deltas = [-1.0, -0.5, 0.0, +0.5, +1.0, +1.5, +2.0]
        sens_rows = []
        for rm in rent_mults:
            r_val = monthly_rent * rm * occupancy_pct / 100
            row   = {f"שכ\"ד: {fmt(r_val)}": ""}
            for rd in rate_deltas:
                rt   = max(0.5, mortgage_rate + rd)
                s_mm = calc_mortgage_payment(mortgage, rt, mortgage_years) if mortgage > 0 else 0.0
                s_cf = r_val - s_mm - total_monthly_expenses
                row[f"ריבית {rt:.1f}%"] = fmt(s_cf)
            sens_rows.append(row)
        df_sens = pd.DataFrame(sens_rows)
        df_sens = df_sens.rename(columns={df_sens.columns[0]: "שכ\"ד \\ ריבית"})
        # drop the empty first value column then rename properly
        first_col = df_sens.columns[0]
        df_sens[first_col] = [f"שכ\"ד {fmt(monthly_rent * rm * occupancy_pct / 100)}" for rm in rent_mults]
        st.dataframe(df_sens, use_container_width=True, hide_index=True)

    # ── TAB 3: EXIT CALCULATOR ────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">מחשבון יציאה — מכירה בשנה X</div>',
                    unsafe_allow_html=True)
        st.caption("חשב כמה תרוויח נטו אם תמכור את הנכס בשנה מסוימת")

        c_a, c_b = st.columns(2)
        with c_a:
            exit_year        = st.slider("שנת מכירה", 1, 30, 10)
            selling_broker   = st.slider("תיווך במכירה (%)", 0.0, 3.0, 2.0, 0.5)
        with c_b:
            exempt_shevach   = st.checkbox("פטור ממס שבח?", value=is_first)
            custom_exit_price = st.number_input(
                "מחיר מכירה ידני (0 = חשב אוטומטי לפי עליית ערך)",
                min_value=0, step=50_000, value=0)

        exit_value = (custom_exit_price if custom_exit_price > 0
                      else price * (1 + appreciation_pct / 100) ** exit_year)

        # Remaining mortgage at exit
        if mortgage > 0:
            sched_exit   = build_amortization_schedule(mortgage, mortgage_rate, mortgage_years)
            exit_idx     = min(exit_year * 12, len(sched_exit)) - 1
            rem_mortgage = sched_exit[exit_idx]["balance"] if sched_exit else 0.0
        else:
            rem_mortgage = 0.0

        cum_cf_exit      = monthly_cashflow * 12 * exit_year
        gross_profit     = exit_value - price
        selling_costs    = exit_value * (selling_broker / 100 + 0.005)
        capital_gains_tax = 0.0 if exempt_shevach else max(0.0, gross_profit * 0.25)
        net_proceeds     = exit_value - rem_mortgage - capital_gains_tax - selling_costs
        total_return     = net_proceeds - equity + cum_cf_exit
        roi_total        = total_return / equity * 100 if equity > 0 else 0.0
        cagr             = ((max(0.01, net_proceeds + cum_cf_exit) / equity)
                            ** (1 / exit_year) - 1) * 100 if exit_year > 0 and equity > 0 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        exit_cards = [
            ("ערך הנכס בשנה " + str(exit_year), fmt(exit_value),    f"עלייה של {fmt(exit_value - price)}"),
            ("יתרת משכנתא",                      fmt(rem_mortgage),  "לפירעון"),
            ("תזרים מצטבר",                      fmt(cum_cf_exit),   f"{exit_year} שנות שכירות"),
            ("רווח נטו כולל",                    fmt(total_return),
             f"ROI {roi_total:.0f}% | CAGR {cagr:.1f}%"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4], exit_cards):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value" style="font-size:20px">{value}</div>
                    <div class="sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        with st.expander("📋 פירוט חישוב היציאה"):
            exit_detail = {
                "מחיר מכירה":             fmt(exit_value),
                "פחות: יתרת משכנתא":      f"- {fmt(rem_mortgage)}",
                "פחות: מס שבח (25%)":      f"- {fmt(capital_gains_tax)}" + (" (פטור)" if exempt_shevach else ""),
                "פחות: עלויות מכירה":      f"- {fmt(selling_costs)}",
                "**תמורה נטו**":           fmt(net_proceeds),
                "פלוס: תזרים מצטבר":      fmt(cum_cf_exit),
                "פחות: הון עצמי שהושקע":   f"- {fmt(equity)}",
                "**רווח נטו כולל**":       fmt(total_return),
                "תשואה כוללת (ROI)":       f"{roi_total:.1f}%",
                "תשואה שנתית (CAGR)":      f"{cagr:.1f}%",
            }
            for k, v in exit_detail.items():
                ca, cb = st.columns([3, 1]); ca.markdown(k); cb.markdown(f"**{v}**")

        # Exit value vs mortgage balance chart
        yrs_30  = list(range(1, 31))
        vals_30 = [price * (1 + appreciation_pct / 100) ** y for y in yrs_30]
        if mortgage > 0 and sched_exit:
            mort_30 = [sched_exit[min(y * 12, len(sched_exit)) - 1]["balance"] for y in yrs_30]
        else:
            mort_30 = [0.0] * 30
        equity_30 = [v - m for v, m in zip(vals_30, mort_30)]

        fig_exit = go.Figure()
        fig_exit.add_trace(go.Scatter(
            x=yrs_30, y=vals_30, name="ערך הנכס",
            fill="tozeroy", fillcolor="rgba(96,165,250,0.12)",
            line=dict(color="#60a5fa", width=2)))
        fig_exit.add_trace(go.Scatter(
            x=yrs_30, y=mort_30, name="יתרת משכנתא",
            fill="tozeroy", fillcolor="rgba(248,113,113,0.12)",
            line=dict(color="#f87171", width=2)))
        fig_exit.add_trace(go.Scatter(
            x=yrs_30, y=equity_30, name="הון עצמי בנכס",
            line=dict(color="#34d399", width=2, dash="dash")))
        fig_exit.add_vline(x=exit_year, line_dash="dot", line_color="#fbbf24",
                           annotation_text=f"יציאה שנה {exit_year}",
                           annotation_font_color="#fbbf24")
        fig_exit.update_layout(**_plotly_dark_layout("ערך הנכס מול יתרת משכנתא (30 שנים)"))
        fig_exit.update_layout(xaxis_title="שנה")
        st.plotly_chart(fig_exit, use_container_width=True)

    # ── TAB 4: SAVE & SHARE ───────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">💾 שמור ושתף</div>', unsafe_allow_html=True)

        deal_snapshot = {
            "שם עסקה":        deal_name,
            "סוג נכס":        prop_type,
            "מחיר רכישה":     price,
            "הון עצמי":       round(equity),
            "משכנתא":         mortgage,
            "החזר חודשי":     round(monthly_mortgage),
            "שכד חודשי":      monthly_rent,
            "תזרים חודשי":    round(monthly_cashflow),
            "תשואה ברוטו":    round(gross_yield, 2),
            "תשואה נטו":      round(net_yield, 2),
            "תשואה על הון":   round(cash_on_cash, 2),
            "ציון":            score,
            "תאריך":          str(date.today()),
        }

        c_save, c_json, c_csv = st.columns(3)
        with c_save:
            if st.button("💾 שמור לרשימה", type="primary", use_container_width=True):
                st.session_state["saved_deals"].append(deal_snapshot)
                st.success(f"✅ '{deal_name}' נשמרה!")

        with c_json:
            st.download_button(
                label="📤 ייצא JSON",
                data=json.dumps(deal_snapshot, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"עסקה_{deal_name}.json",
                mime="application/json",
                use_container_width=True,
            )

        with c_csv:
            csv_summary = pd.DataFrame(
                [{"פרמטר": k, "ערך": str(v)} for k, v in deal_snapshot.items()]
            ).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="📊 ייצא CSV",
                data=csv_summary,
                file_name=f"עסקה_{deal_name}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Saved deals list
        st.divider()
        n_saved = len(st.session_state["saved_deals"])
        st.markdown(f'<div class="section-title">עסקאות שמורות ({n_saved})</div>',
                    unsafe_allow_html=True)

        if st.session_state["saved_deals"]:
            df_saved = pd.DataFrame(st.session_state["saved_deals"])
            show_cols = [c for c in
                ["שם עסקה", "סוג נכס", "מחיר רכישה", "תזרים חודשי",
                 "תשואה ברוטו", "תשואה נטו", "ציון", "תאריך"]
                if c in df_saved.columns]
            st.dataframe(df_saved[show_cols], use_container_width=True, hide_index=True)

            col_dl, col_clear = st.columns(2)
            with col_dl:
                all_csv = df_saved.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                st.download_button("📥 הורד את כל העסקאות (CSV)", data=all_csv,
                                   file_name="כל_העסקאות.csv", mime="text/csv",
                                   use_container_width=True)
            with col_clear:
                if st.button("🗑️ נקה רשימה", use_container_width=True):
                    st.session_state["saved_deals"] = []
                    st.rerun()
        else:
            st.info("אין עסקאות שמורות. לחץ 'שמור לרשימה' לאחר מילוי הטופס.")

    st.caption("⚠️ כל החישובים אינדיקטיביים בלבד. יש להתייעץ עם יועץ נדל\"ן ורואה חשבון.")


# ─── TOOL: AI CHAT ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """אתה יועץ נדל"ן מומחה ישראלי בשם "מתן AI".
אתה מסייע למשקיעים, רוכשים ראשונים, ואנשי מקצוע בתחום הנדל"ן הישראלי.
אתה מומחה ב:
- חוקי מיסוי נדל"ן ישראלי (מס רכישה, מס שבח, מס הכנסה משכירות)
- משכנתאות ומימון נדל"ן בישראל (בנק ישראל, הוראות LTV, פריים)
- שוק הנדל"ן הישראלי (מחירים, מגמות, אזורים)
- תמ"א 38, פינוי-בינוי, חיזוק מבנים
- חוק המכר, חוק השכירות, הסכמי מכר
- תשואות, ניתוח עסקאות, ROI
- נדל"ן מסחרי, קרקעות, ייזום
ענה תמיד בעברית, בצורה מקצועית אך ברורה.
כשרלוונטי, ציין נתונים מספריים עדכניים (2025-2026).
אם שאלה חורגת מתחום הנדל"ן, הסבר בנימוס שאתה מתמחה בנדל"ן בלבד."""


def tool_ai_chat():
    st.title("🤖 צ'אט AI — יועץ נדל\"ן")
    st.caption("שאל כל שאלה בנושא נדל\"ן, מיסוי, משכנתאות ועסקאות — מופעל על Gemini Flash")

    # Initialize Gemini
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("הזן Gemini API Key:", type="password",
                                help="קבל מפתח חינמי ב-aistudio.google.com")
        if not api_key:
            st.info("נדרש Gemini API Key כדי להפעיל את הצ'אט.")
            return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display conversation
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Welcome message on first load
    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown(
                "שלום! אני **מתן AI** — יועץ הנדל\"ן החכם שלך 🏠\n\n"
                "אני יכול לעזור לך בכל שאלה על:\n"
                "- מס רכישה ומס שבח\n"
                "- משכנתאות ומימון\n"
                "- ניתוח עסקאות ותשואות\n"
                "- חוקי נדל\"ן בישראל\n\n"
                "**מה תרצה לדעת?**"
            )

    # Chat input
    if prompt := st.chat_input("שאל שאלה על נדל\"ן..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build history for Gemini
        gemini_history = []
        for msg in st.session_state.chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                try:
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(prompt)
                    answer = response.text
                except Exception as e:
                    answer = f"❌ שגיאה: {e}"
            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Clear chat button
    if st.session_state.chat_history:
        st.divider()
        if st.button("🗑️ נקה שיחה", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ─── TOOL: LEARNING LIBRARY ───────────────────────────────────────────────────

LEARNING_TOPICS = [
    "מיסוי נדל\"ן",
    "משכנתאות ומימון",
    "השקעות נדל\"ן",
    "שוק הנדל\"ן",
    "חוקים ורגולציה",
    "ייזום ופיתוח",
    "כלכלה ומאקרו",
    "כללי",
]

LEARNING_ADMIN_PASSWORD = "matan2024"

SAMPLE_CONTENT = [
    {
        "id": "sample_1",
        "title": "מס רכישה — מדריך מלא 2026",
        "topic": "מיסוי נדל\"ן",
        "type": "article",
        "url": "",
        "description": "הסבר מפורט על מדרגות מס הרכישה בישראל לשנת 2026 — דירה ראשונה מול דירה נוספת.",
        "summary": "מס הרכישה הוא מס חד-פעמי שמשלם הקונה. לדירה ראשונה: 0% עד 1.97M₪, 3.5% עד 2.34M₪, 5% עד 6.05M₪. לדירה נוספת: 8% עד 6.05M₪, 10% מעלה. חשוב להכיר את המדרגות לתכנון פיננסי נכון.",
        "questions": [
            {"q": "מה שיעור מס הרכישה לדירה ראשונה עד 1,978,745 ₪?", "options": ["0%", "3.5%", "5%", "8%"], "answer": 0},
            {"q": "מי משלם מס רכישה?", "options": ["המוכר", "הקונה", "שניהם", "אף אחד"], "answer": 1},
            {"q": "מה שיעור מס הרכישה לדירה נוספת עד 6 מיליון ₪?", "options": ["3.5%", "5%", "8%", "10%"], "answer": 2},
            {"q": "מס הרכישה הוא מס:", "options": ["שנתי", "חד-פעמי", "חודשי", "עם מכירה"], "answer": 1},
            {"q": "לדירה ראשונה ב-2.5 מיליון ₪, על איזה חלק משלמים 5%?", "options": ["כל הסכום", "החלק מ-2.34M עד 2.5M", "החלק מ-1.97M עד 2.34M", "לא משלמים כלל"], "answer": 1},
        ],
        "added_by": "admin",
        "date_added": "2026-03-01",
    },
    {
        "id": "sample_2",
        "title": "יסודות המשכנתא — ריבית, מסלולים ולוח שפיצר",
        "topic": "משכנתאות ומימון",
        "type": "article",
        "url": "",
        "description": "הסבר על לוח שפיצר, מסלולי ריבית (קל\"צ, פריים, צמוד מדד), ואיך לבחור תמהיל נכון.",
        "summary": "לוח שפיצר הוא שיטת החזר קבוע בה כל תשלום כולל קרן וריבית. מסלולי ריבית עיקריים: קל\"צ (קבועה לא צמודה), פריים (ריבית בנק ישראל + 1.5%), צמוד מדד. המלצת בנק ישראל: לפחות שליש ריבית קבועה.",
        "questions": [
            {"q": "מה הוא לוח שפיצר?", "options": ["תשלום גדל עם הזמן", "תשלום קבוע לאורך כל התקופה", "תשלום קרן בלבד", "תשלום ריבית בלבד"], "answer": 1},
            {"q": "ריבית פריים מורכבת מ:", "options": ["ריבית בנק ישראל בלבד", "ריבית בנק ישראל + 1.5%", "ריבית LIBOR", "ריבית קבועה של הבנק"], "answer": 1},
            {"q": "מהו ה-LTV המקסימלי לדירה ראשונה לפי בנק ישראל?", "options": ["50%", "60%", "75%", "90%"], "answer": 2},
            {"q": "מה פירוש קל\"צ?", "options": ["קצרה לא זמינה", "קבועה לא צמודה", "קלה לצמצום", "קרן לא צמודה"], "answer": 1},
            {"q": "מהו אחוז ההחזר המקסימלי המומלץ מההכנסה?", "options": ["20%", "30%", "40%", "50%"], "answer": 2},
        ],
        "added_by": "admin",
        "date_added": "2026-03-01",
    },
    {
        "id": "sample_3",
        "title": "תשואה על נדל\"ן — ברוטו, נטו ותשואה על ההון",
        "topic": "השקעות נדל\"ן",
        "type": "article",
        "url": "",
        "description": "הבדל בין תשואה ברוטו לנטו, חישוב תשואה על ההון (Cash on Cash), ומה נחשב לתשואה טובה בישראל.",
        "summary": "תשואה ברוטו = שכ\"ד שנתי / מחיר נכס. תשואה נטו = שכ\"ד שנתי פחות הוצאות / מחיר. תשואה על ההון (CoC) = תזרים שנתי / הון עצמי שהושקע. בישראל תשואה נטו של 3-4% נחשבת סבירה.",
        "questions": [
            {"q": "כיצד מחשבים תשואה ברוטו?", "options": ["שכ\"ד שנתי / הון עצמי", "שכ\"ד שנתי / מחיר הנכס", "שכ\"ד חודשי × 12 / משכנתא", "רווח ממכירה / מחיר"], "answer": 1},
            {"q": "מה ההבדל בין תשואה ברוטו לנטו?", "options": ["אין הבדל", "נטו מחסירה הוצאות תפעול", "ברוטו מחסיר מיסים", "נטו כוללת עליית ערך"], "answer": 1},
            {"q": "תשואה על ההון (Cash on Cash) מחושבת לפי:", "options": ["תזרים / מחיר נכס", "תזרים / הון עצמי", "שכ\"ד / הון עצמי", "רווח / מחיר"], "answer": 1},
            {"q": "תשואה נטו של 4% בישראל נחשבת:", "options": ["גרועה מאוד", "סבירה", "מצוינת", "בלתי אפשרית"], "answer": 1},
            {"q": "אילו הוצאות מחסירים לחישוב תשואה נטו?", "options": ["רק מיסים", "ועד בית, ביטוח, תיקונים, מיסים", "רק ועד בית", "אין להחסיר"], "answer": 1},
        ],
        "added_by": "admin",
        "date_added": "2026-03-01",
    },
]


def _learning_init():
    if "learning_role" not in st.session_state:
        st.session_state.learning_role = None
        st.session_state.learning_user_name = ""
    if "learning_content" not in st.session_state:
        st.session_state.learning_content = [item.copy() for item in SAMPLE_CONTENT]
    if "learning_scores" not in st.session_state:
        st.session_state.learning_scores = {}
    if "learning_quiz_active" not in st.session_state:
        st.session_state.learning_quiz_active = None
        st.session_state.learning_quiz_answers = {}
        st.session_state.learning_quiz_submitted = False


def _learning_login():
    st.title("🎓 מערכת למידה")
    st.markdown("ספריית ידע מקצועית לצוות — נדל\"ן, מיסוי, מימון ועסקאות")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 כניסת עובד")
        emp_name = st.text_input("שם מלא", key="login_emp_name", placeholder="הכנס שמך")
        if st.button("כניסה לספרייה", type="primary", use_container_width=True):
            if emp_name.strip():
                st.session_state.learning_role = "employee"
                st.session_state.learning_user_name = emp_name.strip()
                st.rerun()
            else:
                st.error("נא הכנס שם")
    with col2:
        st.markdown("### 🔑 כניסת מנהל")
        admin_pass = st.text_input("סיסמת מנהל", type="password", key="login_admin_pass")
        if st.button("כניסה כמנהל", use_container_width=True):
            if admin_pass == LEARNING_ADMIN_PASSWORD:
                st.session_state.learning_role = "admin"
                st.session_state.learning_user_name = "מתן"
                st.rerun()
            else:
                st.error("סיסמה שגויה")


def _ai_generate_quiz(title, description, url_hint=""):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None, None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    context = f"כותרת: {title}\nתיאור: {description}"
    if url_hint:
        context += f"\nקישור: {url_hint}"
    prompt = f"""בהתבסס על תוכן הלימוד הבא, צור:
1. סיכום קצר (3-4 משפטים) בעברית
2. 5 שאלות אמריקאיות (multiple choice) בעברית, כל שאלה עם 4 תשובות, תשובה נכונה אחת

{context}

החזר JSON בלבד, ללא markdown, בפורמט:
{{
  "summary": "סיכום...",
  "questions": [
    {{"q": "שאלה?", "options": ["א", "ב", "ג", "ד"], "answer": 0}}
  ]
}}
answer הוא אינדקס 0-3 של התשובה הנכונה."""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        return data.get("summary", ""), data.get("questions", [])
    except Exception:
        return None, None


def _learning_admin_view():
    st.title("🎓 מערכת למידה — ניהול")
    st.caption(f"מחובר כמנהל: {st.session_state.learning_user_name}")
    if st.button("🚪 יציאה"):
        st.session_state.learning_role = None
        st.rerun()

    tab_add, tab_lib, tab_scores = st.tabs(["➕ הוסף תוכן", "📚 ניהול ספרייה", "📊 ציונים"])

    # ── TAB: ADD CONTENT ──────────────────────────────────────────────────────
    with tab_add:
        st.markdown('<div class="section-title">הוספת תוכן חדש לספרייה</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("כותרת *", placeholder="שם השיעור / הנושא")
            new_topic = st.selectbox("נושא *", LEARNING_TOPICS)
        with c2:
            new_type = st.selectbox(
                "סוג תוכן",
                ["article", "youtube", "podcast"],
                format_func=lambda x: {"article": "📄 מאמר", "youtube": "▶️ יוטיוב", "podcast": "🎙️ פודקאסט"}[x],
            )
            new_url = st.text_input("קישור (URL)", placeholder="https://...")
        new_desc = st.text_area("תיאור / תקציר ידני", placeholder="תאר את תוכן השיעור...", height=100)

        st.divider()
        col_gen, col_save = st.columns(2)
        with col_gen:
            if st.button("🤖 צור סיכום ושאלות (AI)", use_container_width=True, type="primary"):
                if new_title:
                    with st.spinner("מייצר שאלות עם AI..."):
                        summary, questions = _ai_generate_quiz(new_title, new_desc, new_url)
                    if summary and questions:
                        st.session_state["_new_summary"] = summary
                        st.session_state["_new_questions"] = questions
                        st.success(f"✅ נוצרו {len(questions)} שאלות!")
                    else:
                        st.error("לא ניתן ליצור שאלות — בדוק את ה-API Key")
                else:
                    st.warning("הזן כותרת קודם")

        if "_new_summary" in st.session_state:
            with st.expander("👁️ תצוגה מקדימה", expanded=True):
                st.markdown(f"**סיכום:** {st.session_state['_new_summary']}")
                st.markdown("**שאלות:**")
                for i, q in enumerate(st.session_state.get("_new_questions", []), 1):
                    correct = q.get("options", [""])[q.get("answer", 0)]
                    st.markdown(f"{i}. {q['q']} ✅ `{correct}`")

        with col_save:
            if st.button("💾 שמור לספרייה", use_container_width=True):
                if not new_title.strip():
                    st.error("נא הכנס כותרת")
                else:
                    summary = st.session_state.pop("_new_summary", new_desc[:200])
                    questions = st.session_state.pop("_new_questions", [])
                    new_item = {
                        "id": str(uuid.uuid4())[:8],
                        "title": new_title.strip(),
                        "topic": new_topic,
                        "type": new_type,
                        "url": new_url.strip(),
                        "description": new_desc.strip(),
                        "summary": summary,
                        "questions": questions,
                        "added_by": "admin",
                        "date_added": str(date.today()),
                    }
                    st.session_state.learning_content.append(new_item)
                    st.success(f"✅ '{new_title}' נוסף לספרייה!")
                    st.rerun()

    # ── TAB: MANAGE LIBRARY ───────────────────────────────────────────────────
    with tab_lib:
        content = st.session_state.learning_content
        st.markdown(f'<div class="section-title">ספרייה ({len(content)} פריטים)</div>', unsafe_allow_html=True)
        if not content:
            st.info("הספרייה ריקה. הוסף תוכן בלשונית 'הוסף תוכן'.")
        else:
            topic_filter = st.selectbox("סנן לפי נושא", ["הכל"] + LEARNING_TOPICS, key="admin_topic_filter")
            filtered = content if topic_filter == "הכל" else [c for c in content if c["topic"] == topic_filter]
            for item in filtered:
                type_icon = {"article": "📄", "youtube": "▶️", "podcast": "🎙️"}.get(item["type"], "📄")
                with st.expander(f"{type_icon} {item['title']} — {item['topic']}"):
                    st.markdown(f"**תיאור:** {item.get('description', '—')}")
                    st.markdown(f"**סיכום:** {item.get('summary', '—')}")
                    st.markdown(f"**שאלות:** {len(item.get('questions', []))}")
                    if item.get("url"):
                        st.markdown(f"**קישור:** {item['url']}")
                    st.caption(f"נוסף: {item.get('date_added', '')}")
                    if st.button("🗑️ מחק", key=f"del_{item['id']}"):
                        st.session_state.learning_content = [c for c in content if c["id"] != item["id"]]
                        st.rerun()

    # ── TAB: SCORES ───────────────────────────────────────────────────────────
    with tab_scores:
        scores = st.session_state.learning_scores
        st.markdown('<div class="section-title">ציוני כל העובדים</div>', unsafe_allow_html=True)
        if not scores:
            st.info("אין עדיין ציונים. ציונים יופיעו כאשר עובדים יגישו מבחנים.")
        else:
            all_rows = []
            for emp_name, emp_scores in scores.items():
                for s in emp_scores:
                    pct = s["score"] / s["total"] * 100 if s["total"] > 0 else 0
                    all_rows.append({
                        "עובד": emp_name,
                        "נושא": s.get("title", "—"),
                        "ציון": f"{s['score']}/{s['total']}",
                        "אחוז": f"{pct:.0f}%",
                        "תאריך": s.get("date", ""),
                    })
            st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)

            st.divider()
            st.markdown('<div class="section-title">סיכום לפי עובד</div>', unsafe_allow_html=True)
            for emp_name, emp_scores in scores.items():
                if emp_scores:
                    avg = sum(s["score"] / s["total"] for s in emp_scores if s["total"] > 0) / len(emp_scores) * 100
                    with st.expander(f"👤 {emp_name} — ממוצע {avg:.0f}% ({len(emp_scores)} מבחנים)"):
                        for s in emp_scores:
                            pct = s["score"] / s["total"] * 100 if s["total"] > 0 else 0
                            icon = "🟢" if pct >= 80 else "🟡" if pct >= 60 else "🔴"
                            ca, cb = st.columns([3, 1])
                            ca.markdown(s.get("title", "—"))
                            cb.markdown(f"{icon} {s['score']}/{s['total']}")


def _show_quiz(emp_name):
    content_id = st.session_state.learning_quiz_active
    item = next((c for c in st.session_state.learning_content if c["id"] == content_id), None)
    if not item:
        st.session_state.learning_quiz_active = None
        st.rerun()
        return

    questions = item.get("questions", [])

    if st.button("← חזור לספרייה"):
        st.session_state.learning_quiz_active = None
        st.session_state.learning_quiz_submitted = False
        st.rerun()

    st.markdown(f"## 🧪 מבחן: {item['title']}")
    st.markdown(f"*{item['topic']}* · {len(questions)} שאלות")
    st.divider()

    if st.session_state.learning_quiz_submitted:
        answers = st.session_state.learning_quiz_answers
        score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["answer"])
        pct = score / len(questions) * 100 if questions else 0
        icon = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
        st.markdown(f"## {icon} תוצאה: {score}/{len(questions)} ({pct:.0f}%)")
        if pct >= 80:
            st.markdown('<div class="alert-green">מצוין! שלטת בחומר היטב.</div>', unsafe_allow_html=True)
        elif pct >= 60:
            st.markdown('<div class="alert-yellow">תוצאה טובה — כדאי לחזור על הנושאים שפספסת.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-red">כדאי לחזור על החומר ולנסות שוב.</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### פירוט תשובות")
        for i, q in enumerate(questions):
            user_ans = answers.get(i)
            correct = q["answer"]
            is_correct = user_ans == correct
            mark = "✅" if is_correct else "❌"
            st.markdown(f"**{i+1}. {q['q']}** {mark}")
            for j, opt in enumerate(q["options"]):
                if j == correct:
                    prefix = "✅ "
                elif j == user_ans and not is_correct:
                    prefix = "❌ "
                else:
                    prefix = "○ "
                st.markdown(f"&nbsp;&nbsp;&nbsp;{prefix}{opt}")

        col_retry, col_back = st.columns(2)
        with col_retry:
            if st.button("🔄 נסה שוב", use_container_width=True):
                st.session_state.learning_quiz_answers = {}
                st.session_state.learning_quiz_submitted = False
                st.rerun()
        with col_back:
            if st.button("← חזור לספרייה", key="back2", use_container_width=True):
                st.session_state.learning_quiz_active = None
                st.session_state.learning_quiz_submitted = False
                st.rerun()
    else:
        answers = st.session_state.learning_quiz_answers
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(f"**{i+1}. {q['q']}**")
                choice = st.radio(
                    f"שאלה {i+1}",
                    options=list(range(len(q["options"]))),
                    format_func=lambda x, opts=q["options"]: opts[x],
                    key=f"q_{i}",
                    label_visibility="collapsed",
                )
                answers[i] = choice
                st.markdown("---")
            submitted = st.form_submit_button("✅ הגש מבחן", use_container_width=True, type="primary")

        if submitted:
            st.session_state.learning_quiz_answers = answers
            st.session_state.learning_quiz_submitted = True
            score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["answer"])
            if emp_name not in st.session_state.learning_scores:
                st.session_state.learning_scores[emp_name] = []
            st.session_state.learning_scores[emp_name].append({
                "content_id": content_id,
                "title": item["title"],
                "score": score,
                "total": len(questions),
                "date": str(date.today()),
            })
            st.rerun()


def _learning_employee_view():
    name = st.session_state.learning_user_name
    st.title("🎓 מערכת למידה")
    st.caption(f"שלום {name}!")
    if st.button("🚪 יציאה"):
        st.session_state.learning_role = None
        st.session_state.learning_quiz_active = None
        st.session_state.learning_quiz_submitted = False
        st.rerun()

    if st.session_state.learning_quiz_active:
        _show_quiz(name)
        return

    tab_lib, tab_scores = st.tabs(["📚 ספריית תכנים", "🏆 הציונים שלי"])

    # ── TAB: CONTENT LIBRARY ──────────────────────────────────────────────────
    with tab_lib:
        content = st.session_state.learning_content
        if not content:
            st.info("הספרייה ריקה כרגע. המנהל יוסיף תכנים בקרוב.")
        else:
            topic_filter = st.selectbox("נושא", ["הכל"] + LEARNING_TOPICS, key="emp_topic_filter")
            filtered = content if topic_filter == "הכל" else [c for c in content if c["topic"] == topic_filter]
            emp_scores = st.session_state.learning_scores.get(name, [])
            for item in filtered:
                type_icon = {"article": "📄", "youtube": "▶️", "podcast": "🎙️"}.get(item["type"], "📄")
                completed = any(s["content_id"] == item["id"] for s in emp_scores)
                badge = " ✅" if completed else ""
                with st.expander(f"{type_icon} {item['title']}{badge} — {item['topic']}"):
                    if item.get("url"):
                        if item["type"] == "youtube":
                            url = item["url"]
                            vid_id = ""
                            if "v=" in url:
                                vid_id = url.split("v=")[1].split("&")[0]
                            elif "youtu.be/" in url:
                                vid_id = url.split("youtu.be/")[1].split("?")[0]
                            if vid_id:
                                st.markdown(
                                    f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{vid_id}" '
                                    f'frameborder="0" allowfullscreen></iframe>',
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(f"[🔗 פתח קישור]({url})")
                        else:
                            st.markdown(f"[🔗 {item['url']}]({item['url']})")
                    if item.get("summary"):
                        st.markdown(f"**📝 סיכום:** {item['summary']}")
                    if item.get("questions"):
                        n_q = len(item["questions"])
                        label = f"🔄 בצע שוב מבחן ({n_q} שאלות)" if completed else f"🧪 התחל מבחן ({n_q} שאלות)"
                        if st.button(label, key=f"quiz_start_{item['id']}", type="primary"):
                            st.session_state.learning_quiz_active = item["id"]
                            st.session_state.learning_quiz_answers = {}
                            st.session_state.learning_quiz_submitted = False
                            st.rerun()
                    else:
                        st.caption("אין שאלות לתוכן זה")

    # ── TAB: MY SCORES ────────────────────────────────────────────────────────
    with tab_scores:
        emp_scores = st.session_state.learning_scores.get(name, [])
        if not emp_scores:
            st.info("עדיין לא השלמת מבחנים. גש לספרייה והתחל!")
        else:
            total_taken = len(emp_scores)
            avg_pct = sum(s["score"] / s["total"] for s in emp_scores if s["total"] > 0) / total_taken * 100
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">מבחנים שהושלמו</div>
                    <div class="value">{total_taken}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">ממוצע ציונים</div>
                    <div class="value">{avg_pct:.0f}%</div>
                </div>""", unsafe_allow_html=True)
            st.divider()
            for s in reversed(emp_scores):
                pct = s["score"] / s["total"] * 100 if s["total"] > 0 else 0
                icon = "🟢" if pct >= 80 else "🟡" if pct >= 60 else "🔴"
                ca, cb = st.columns([3, 1])
                ca.markdown(f"{icon} **{s.get('title', '—')}** ({s.get('date', '')})")
                cb.markdown(f"**{s['score']}/{s['total']}** ({pct:.0f}%)")


def tool_learning():
    _learning_init()
    if st.session_state.learning_role is None:
        _learning_login()
    elif st.session_state.learning_role == "admin":
        _learning_admin_view()
    else:
        _learning_employee_view()


# ─── TOOL: LAWS & TAXES REFERENCE ────────────────────────────────────────────

LAW_CARDS = [
    {
        "title": "מס רכישה",
        "category": "מיסוי",
        "summary": "מס חד-פעמי שמשלם הקונה בעת רכישת נכס",
        "content": """**מי משלם:** הקונה בלבד. **מתי:** תוך 60 יום מחתימת החוזה.

**דירה ראשונה (2026):**
- 0% עד ₪1,978,745
- 3.5% על החלק שבין ₪1,978,745 ל-₪2,347,040
- 5% על החלק שבין ₪2,347,040 ל-₪6,055,070
- 8% על החלק שבין ₪6,055,070 ל-₪20,183,565
- 10% על כל סכום מעל ₪20,183,565

**דירה נוספת / משקיע:**
- 8% על החלק עד ₪6,055,070 · 10% מעלה

**פטורים מיוחדים:** עולים חדשים, נכים, גרוש/גרושה חד-הורי בתנאים מסוימים.""",
    },
    {
        "title": "מס שבח",
        "category": "מיסוי",
        "summary": "מס על הרווח ממכירת נכס — 25% מהרווח הריאלי",
        "content": """**מי משלם:** המוכר. **שיעור:** 25% על הרווח הריאלי.

**חישוב בסיסי:**
(מחיר מכירה − מחיר קנייה − הוצאות מוכרות) × 25%

**הוצאות מוכרות:** שכ"ט עו"ד, תיווך, שיפוצים מוכרים, מס רכישה ששולם, פחת.

**פטור לדירת מגורים יחידה:**
- מי שמכר דירה יחידה ולא מכר ב-18 חודשים האחרונים — פטור מלא.

**חישוב ליניארי (דירה שנרכשה לפני 2014):**
- חלק הרווח מלפני 1.1.2014 — פטור. חלק מ-2014 ואילך — 25%.

**ניכוי מדד:** עלות הרכישה מתואמת למדד המחירים לצרכן.""",
    },
    {
        "title": "מס הכנסה על שכירות",
        "category": "מיסוי",
        "summary": "מיסוי הכנסות משכר דירה — 3 מסלולים",
        "content": """**מסלול א׳ — שיעור מופחת 10%:**
- 10% מהשכירות הגולמית. ללא ניכוי הוצאות. פשוט ומהיר.

**מסלול ב׳ — פטור (עד תקרה 2026):**
- שכ"ד חודשי עד ₪5,471 — פטור מלא ממס.
- אם עולה על התקרה — מיסוי על העודף לפי מס שולי.

**מסלול ג׳ — מס שולי רגיל:**
- מצרף לכלל ההכנסות. מנכה הוצאות (פחת 2%, ריבית, ועד בית, תיקונים).
- מתאים כשיש הוצאות גבוהות ומדרגת מס נמוכה.

**המלצה:** השווה את 3 המסלולים לפי הכנסתך הכוללת — ראה מחשבון ברשות המיסים.""",
    },
    {
        "title": "חוק המכר (דירות)",
        "category": "חוקים",
        "summary": "הגנות חוקיות לרוכש דירה מקבלן",
        "content": """**ליקויי בנייה — אחריות הקבלן:**
- 7 שנים: ליקויי שלד ויסוד
- 3 שנים: ליקויי רטיבות, אינסטלציה, חשמל
- שנה: ליקויי גמר (ריצוף, טיח, צבע)

**ערבות בנקאית:** חובה עד מסירת הדירה — מגן על כספי הרוכש.

**מועד מסירה:** כל איחור מעל 60 יום → פיצוי של 1.5 שכ"ד לחודש.

**מפרט טכני:** חלק מחייב מהחוזה — הקבלן מחויב לו.

**פגמים נסתרים:** זכות תביעה גם לאחר הרכישה בתקופת האחריות.""",
    },
    {
        "title": "חוק השכירות",
        "category": "חוקים",
        "summary": "זכויות וחובות משכיר ושוכר",
        "content": """**הסכם שכירות:** חייב להיות בכתב. מומלץ לרשום בטאבו.

**בטחונות מקסימליים:** שיק ביטחון / ערבות בנקאית עד 3 חודשי שכ"ד.

**תיקונים:**
- תקלות שוטפות (נורות, ברז טפטוף קל) — השוכר
- תיקוני מבנה ותשתיות — המשכיר

**פינוי שוכר:** רק דרך בית משפט (תביעת פינוי). לא ניתן לנעול/לנתק שירותים.

**חוק שכירות הוגנת (2017):**
- הגבלת עמלת תיווך לחצי חודש שכ"ד
- זכות להכניס שוכר חלופי בתנאים מסוימים
- הגנה מפני פינוי לא מוצדק""",
    },
    {
        "title": "תמ\"א 38",
        "category": "תכנון",
        "summary": "חיזוק מבנים ישנים ותוספת בנייה",
        "content": """**מטרה:** חיזוק מבנים שנבנו לפני 1980 מפני רעידות אדמה.

**תמ"א 38/1 — חיזוק + תוספת:**
- הקבלן מחזק, הדיירים מקבלים: ממ"ד, מרפסת, מעלית, חניה.
- הקבלן מרוויח: קומות נוספות למכירה.

**תמ"א 38/2 — הריסה ובנייה:**
- הריסת הבניין ובניית חדש + דירות גדולות יותר לדיירים.

**הסכמה נדרשת:** 66% מדיירי הבניין (38/1), 80% (38/2).

**חשוב:** תמ"א 38 בוטלה כתוכנית ארצית החל מ-2022 — כעת ברישוי מקומי בלבד.""",
    },
    {
        "title": "פינוי-בינוי",
        "category": "תכנון",
        "summary": "הריסה ובנייה מחדש של מתחמים שלמים",
        "content": """**מהו:** פרויקט עירוני של הריסת שכונות ישנות ובניית בניינים חדשים.

**יתרון לדיירים:** דירה חדשה + גדולה יותר + ממ"ד + חניה + מחסן — ללא עלות.

**הסכמה:** 80% מהדיירים במתחם (לאחר תיקון חוק 2006).

**מסרב לא סביר:** ניתן לתבוע אותו בגין נזקי שאר הדיירים.

**ליווי מומלץ:** ועד בית עם עו"ד מטעם הדיירים — עלויות הייעוץ על היזם.

**מיסוי:** פטור ממס שבח ומס רכישה לדיירים הותיקים.""",
    },
    {
        "title": "רישום בטאבו",
        "category": "רישום",
        "summary": "מרשם המקרקעין הרשמי — הגנה על הבעלות",
        "content": """**חשיבות:** רישום בטאבו = בעלות חוקית מוגמרת. ללא רישום — הבעלות חשופה.

**מסמכים לרישום:** שטר מכר, אישור מסים (שבח+רכישה), אישור עירייה (היטל השבחה).

**תקופה:** 6–18 חודשים בממוצע מגמר העסקה.

**נסח טאבו:** מסמך המאמת בעלות, שעבודים, הערות — הפק ב-gov.il (₪27 בדיגיטל).

**הערת אזהרה:** נרשמת מיד עם חתימת חוזה — מגן על הקונה עד להשלמת הרישום.

**שכירות לטאבו:** שכירות מעל 5 שנים ניתן לרשום בטאבו להגנה מלאה.""",
    },
    {
        "title": "בדיקת נאותות (Due Diligence)",
        "category": "רכישה",
        "summary": "בדיקות חובה לפני כל רכישת נכס",
        "content": """**בדיקות משפטיות:**
- נסח טאבו — שעבודים, עיקולים, הערות אזהרה
- תיק בניין בעירייה — חריגות בנייה, צווי הריסה
- היתר בנייה — בדוק שהנכס תואם להיתר

**בדיקות פיזיות:**
- שמאי מקרקעין — שווי ומצב הנכס
- מהנדס / בדק בית — ליקויים, חריגות, לחות

**בדיקות כספיות:**
- חובות לעירייה (ארנונה, היטל השבחה)
- חובות לוועד בית
- מצב המשכנתא הקיימת — שחרור שעבוד

**עלות ממוצעת:** שמאי ₪1,500–3,000 · בדק בית ₪1,000–2,000""",
    },
    {
        "title": "היטל השבחה",
        "category": "מיסוי",
        "summary": "תשלום לעירייה בגין עליית ערך מתכנון",
        "content": """**מהו:** 50% מעליית ערך הנכס הנובעת מאישור תב"ע / שינוי ייעוד / הקלה.

**מתי משלמים:** בעת מימוש הזכויות — בנייה, מכירה, פיצול דירה.

**מי משלם:** בעל הנכס בעת המימוש (לא בעת אישור התוכנית).

**שומה:** שמאי מטעם הוועדה המקומית קובע את עליית הערך.

**ערעור:** ניתן לערער על השומה תוך 45 יום ע"י שמאי מטעמך.

**פטורים:** מכירה לקרוב משפחה, מוסד ציבורי, ועוד — בתנאים מסוימים.""",
    },
]


def tool_laws_taxes():
    st.title("⚖️ חוקים ומיסים")
    st.caption("מדריך מקיף לחוקי נדל\"ן ישראלי — מיסים, זכויות, תכנון ורישום")

    tab_ref, tab_ai = st.tabs(["📖 מדריך חוקים ומיסים", "🤖 שאל את ה-AI המשפטי"])

    with tab_ref:
        col_search, col_cat = st.columns([2, 1])
        with col_search:
            search = st.text_input("🔍 חיפוש נושא", placeholder="לדוגמה: מס שבח, פינוי, שכירות...")
        with col_cat:
            cats = ["הכל"] + list(dict.fromkeys(c["category"] for c in LAW_CARDS))
            cat_filter = st.selectbox("קטגוריה", cats)

        filtered = LAW_CARDS
        if cat_filter != "הכל":
            filtered = [c for c in filtered if c["category"] == cat_filter]
        if search.strip():
            s = search.lower()
            filtered = [c for c in filtered if s in c["title"].lower() or s in c["summary"].lower() or s in c["content"].lower()]

        st.caption(f"{len(filtered)} נושאים")
        for card in filtered:
            with st.expander(f"**{card['title']}** — {card['summary']}"):
                st.markdown(card["content"])

    with tab_ai:
        st.markdown("### 🤖 יועץ משפטי AI — שאל כל שאלה על נדל\"ן")
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.warning("נדרש Gemini API Key — הגדר ב-.streamlit/secrets.toml")
            return

        if "law_chat" not in st.session_state:
            st.session_state.law_chat = []

        for msg in st.session_state.law_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.law_chat:
            with st.chat_message("assistant"):
                st.markdown(
                    "שלום! אני יועץ משפטי AI לנדל\"ן ישראלי 📜\n\n"
                    "אני יכול לעזור עם:\n"
                    "- פרשנות חוקים ותקנות\n"
                    "- שאלות על מיסים ופטורים\n"
                    "- בדיקת זכויות ברכישה/שכירות\n\n"
                    "⚠️ *התשובות הן כלליות ואינן מחליפות ייעוץ משפטי פרטני.*"
                )

        if prompt := st.chat_input("שאל שאלה משפטית על נדל\"ן..."):
            st.session_state.law_chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            genai.configure(api_key=api_key)
            law_model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction="""אתה עו"ד מומחה לנדל"ן ישראלי.
ענה בעברית, בצורה מקצועית וברורה, על שאלות הקשורות לנדל"ן: מיסים, חוזים, זכויות, תכנון ובנייה.
תמיד ציין בסוף: "⚠️ תשובה זו כללית ואינה מחליפה ייעוץ משפטי פרטני."
אם השאלה לא קשורה לנדל"ן — הסבר בנימוס.""",
            )
            with st.chat_message("assistant"):
                with st.spinner("חושב..."):
                    try:
                        history = [
                            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                            for m in st.session_state.law_chat[:-1]
                        ]
                        chat = law_model.start_chat(history=history)
                        resp = chat.send_message(prompt)
                        answer = resp.text
                    except Exception as e:
                        answer = f"❌ שגיאה: {e}"
                st.markdown(answer)
            st.session_state.law_chat.append({"role": "assistant", "content": answer})

        if st.session_state.law_chat:
            if st.button("🗑️ נקה שיחה", key="clear_law"):
                st.session_state.law_chat = []
                st.rerun()


# ─── TOOL: TAX AUTHORITY ─────────────────────────────────────────────────────

INCOME_BRACKETS_2026 = [
    (84_120, 0.10),
    (120_720, 0.14),
    (193_800, 0.20),
    (269_280, 0.31),
    (560_280, 0.35),
    (721_560, 0.47),
    (float("inf"), 0.50),
]


def calc_income_tax(annual_income: float) -> float:
    tax = 0.0
    prev = 0.0
    for ceiling, rate in INCOME_BRACKETS_2026:
        if annual_income <= prev:
            break
        taxable = min(annual_income, ceiling) - prev
        tax += taxable * rate
        prev = ceiling
    return tax


def tool_tax_authority():
    st.title("🏛️ רשות המיסים")
    st.caption("מחשבוני מס מקצועיים — מס שבח, מס שכירות, פטורים ותכנון מס")

    tab_shevach, tab_rent, tab_guide = st.tabs([
        "📈 מס שבח",
        "🏠 מס שכירות — השוואת מסלולים",
        "📋 פטורים ומועדים",
    ])

    # ── TAB 1: MAS SHEVACH ────────────────────────────────────────────────────
    with tab_shevach:
        st.markdown('<div class="section-title">מחשבון מס שבח</div>', unsafe_allow_html=True)
        st.caption("מס על רווח ממכירת נכס — 25% מהרווח הריאלי, בכפוף לפטורים")

        c1, c2 = st.columns(2)
        with c1:
            sell_price = st.number_input("מחיר מכירה (₪)", min_value=0, step=50_000, value=2_500_000)
            buy_price = st.number_input("מחיר רכישה מקורי (₪)", min_value=0, step=50_000, value=1_200_000)
            buy_year = st.number_input("שנת רכישה", min_value=1980, max_value=2025, value=2010)
        with c2:
            lawyer_sell = st.number_input("שכ\"ט עו\"ד מכירה (₪)", min_value=0, step=1_000, value=15_000)
            lawyer_buy = st.number_input("שכ\"ט עו\"ד + מס רכישה ששולם (₪)", min_value=0, step=5_000, value=60_000)
            renovation_cost = st.number_input("השקעות מוכרות בנכס (₪)", min_value=0, step=10_000, value=0,
                                               help="שיפוצים עם קבלות, תוספות בנייה בהיתר")
            broker_sell = st.number_input("תיווך במכירה (₪)", min_value=0, step=5_000, value=0)

        is_single = st.checkbox("זוהי דירתי היחידה (לבחינת פטור)", value=True)

        # CPI adjustment (simplified: assume 2% avg annual)
        years_held = max(1, 2026 - buy_year)
        cpi_factor = (1.02) ** years_held
        buy_price_indexed = buy_price * cpi_factor

        total_deductions = lawyer_sell + lawyer_buy + renovation_cost + broker_sell
        nominal_profit = sell_price - buy_price - total_deductions
        real_profit = sell_price - buy_price_indexed - total_deductions

        # Linear exemption: proportion before 2014 is exempt
        LINEAR_CUTOFF = 2014
        if buy_year < LINEAR_CUTOFF:
            years_before_cutoff = LINEAR_CUTOFF - buy_year
            exempt_fraction = years_before_cutoff / years_held
        else:
            exempt_fraction = 0.0

        taxable_profit = max(0, real_profit * (1 - exempt_fraction))
        full_exempt = is_single and years_held >= 0  # simplified — full single-apt check

        tax_shevach = 0.0 if full_exempt else taxable_profit * 0.25
        effective_rate = tax_shevach / max(1, sell_price) * 100

        st.divider()
        st.markdown("## 📊 תוצאות חישוב מס שבח")
        c1, c2, c3, c4 = st.columns(4)
        cards_s = [
            ("רווח נומינלי", fmt(max(0, nominal_profit)), "לפני תיאום מדד"),
            ("רווח ריאלי", fmt(max(0, real_profit)), f"לאחר מדד × {cpi_factor:.2f}"),
            ("רווח חייב במס", fmt(taxable_profit), f"פטור ליניארי {exempt_fraction*100:.0f}%"),
            ("מס שבח לתשלום", fmt(tax_shevach), f"שיעור אפקטיבי {effective_rate:.1f}%"),
        ]
        for col, (label, value, sub) in zip([c1, c2, c3, c4], cards_s):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value">{value}</div>
                    <div class="sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        if full_exempt and is_single:
            st.markdown("""<div class="alert-green">
                ✅ <strong>פטור מלא לדירת מגורים יחידה</strong><br>
                אם זוהי דירתך היחידה ולא מכרת דירה ב-18 חודשים האחרונים — אתה פטור ממס שבח.
                מומלץ לוודא זכאות עם עו"ד מקרקעין.
            </div>""", unsafe_allow_html=True)
        elif exempt_fraction > 0:
            st.markdown(f"""<div class="alert-yellow">
                ⚡ <strong>פטור ליניארי חלקי — {exempt_fraction*100:.0f}% פטור</strong><br>
                החלק מלפני 1.1.2014 פטור ממס. החלק מ-2014 ואילך חייב ב-25%.
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="section-title">פירוט החישוב</div>', unsafe_allow_html=True)
        breakdown = {
            "מחיר מכירה": fmt(sell_price),
            f"מחיר רכישה מקורי": fmt(buy_price),
            f"מחיר רכישה מתואם מדד ({buy_year}→2026)": fmt(buy_price_indexed),
            "שכ\"ט עו\"ד ומס רכישה": fmt(lawyer_buy),
            "שכ\"ט עו\"ד מכירה + תיווך": fmt(lawyer_sell + broker_sell),
            "השקעות מוכרות": fmt(renovation_cost),
            "**רווח ריאלי לפני פטור**": fmt(max(0, real_profit)),
            f"**פטור ליניארי ({exempt_fraction*100:.0f}%)**": f"- {fmt(max(0, real_profit) * exempt_fraction)}",
            "**רווח חייב במס**": fmt(taxable_profit),
            "**מס שבח (25%)**": fmt(tax_shevach),
        }
        for k, v in breakdown.items():
            ca, cb = st.columns([3, 1])
            ca.markdown(k)
            cb.markdown(f"**{v}**")
        st.caption("⚠️ החישוב אינדיקטיבי. תיאום מדד מחושב בהנחת 2% בשנה. יש להתייעץ עם עו\"ד מקרקעין.")

    # ── TAB 2: RENTAL INCOME TAX ──────────────────────────────────────────────
    with tab_rent:
        st.markdown('<div class="section-title">מחשבון מס הכנסה על שכירות — השוואת מסלולים</div>',
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            monthly_rent = st.number_input("שכ\"ד חודשי (₪)", min_value=0, step=500, value=5_000)
            other_annual_income = st.number_input("הכנסה שנתית אחרת (₪)", min_value=0, step=10_000, value=180_000,
                                                   help="משכורת, עסק עצמאי וכו׳")
        with c2:
            annual_expenses = st.number_input("הוצאות שנתיות מוכרות (₪)", min_value=0, step=1_000, value=3_000,
                                               help="ועד בית, ביטוח, תיקונים, פחת (2% מהנכס)")
            property_value = st.number_input("שווי הנכס לחישוב פחת (₪)", min_value=0, step=100_000, value=1_500_000)

        annual_rent = monthly_rent * 12
        depreciation = property_value * 0.02  # 2% annual depreciation
        total_expenses = annual_expenses + depreciation
        rent_ceiling_2026 = 5_471 * 12  # annual

        # Route A: 10% flat
        tax_a = annual_rent * 0.10

        # Route B: Exemption up to ceiling
        if annual_rent <= rent_ceiling_2026:
            tax_b = 0.0
            b_note = f"פטור מלא — שכ\"ד שנתי ({fmt(annual_rent)}) מתחת לתקרה ({fmt(rent_ceiling_2026)})"
        else:
            excess = annual_rent - rent_ceiling_2026
            combined_b = other_annual_income + excess
            tax_on_combined = calc_income_tax(combined_b)
            tax_on_other = calc_income_tax(other_annual_income)
            tax_b = tax_on_combined - tax_on_other
            b_note = f"מיסוי שולי על העודף ({fmt(excess)}) מעל התקרה"

        # Route C: Regular marginal tax with deductions
        net_rent_c = max(0, annual_rent - total_expenses)
        combined_c = other_annual_income + net_rent_c
        tax_on_combined_c = calc_income_tax(combined_c)
        tax_on_other_c = calc_income_tax(other_annual_income)
        tax_c = max(0, tax_on_combined_c - tax_on_other_c)

        best = min(tax_a, tax_b, tax_c)

        st.divider()
        st.markdown("## 📊 השוואת מסלולים")
        c1, c2, c3 = st.columns(3)
        routes = [
            ("מסלול א׳ — 10% קבוע", tax_a, f"ללא ניכוי הוצאות · פשוט"),
            ("מסלול ב׳ — פטור/שולי", tax_b, b_note[:50]),
            ("מסלול ג׳ — מס שולי + הוצאות", tax_c, f"הוצאות: {fmt(total_expenses)} (כולל פחת {fmt(depreciation)})"),
        ]
        for col, (label, tax_val, note) in zip([c1, c2, c3], routes):
            is_best = abs(tax_val - best) < 1
            border = "border: 2px solid #60a5fa;" if is_best else ""
            badge = " 🏆 מומלץ" if is_best else ""
            with col:
                st.markdown(f"""<div class="metric-card" style="{border}">
                    <div class="label">{label}{badge}</div>
                    <div class="value">{fmt(tax_val)}</div>
                    <div class="sub">{note}</div>
                </div>""", unsafe_allow_html=True)

        saving = max(tax_a, tax_b, tax_c) - best
        if saving > 100:
            st.markdown(f"""<div class="alert-green" style="margin-top:15px">
                💡 <strong>חיסכון בבחירת המסלול האופטימלי: {fmt(saving)} לשנה</strong>
            </div>""", unsafe_allow_html=True)

        st.divider()
        rows_rent = {
            "שכ\"ד שנתי": fmt(annual_rent),
            "הכנסה שנתית אחרת": fmt(other_annual_income),
            "הוצאות מוכרות (כולל פחת)": fmt(total_expenses),
            "פחת (2% משווי הנכס)": fmt(depreciation),
            "תקרת פטור שנתית (2026)": fmt(rent_ceiling_2026),
        }
        for k, v in rows_rent.items():
            ca, cb = st.columns([3, 1])
            ca.markdown(k)
            cb.markdown(f"**{v}**")
        st.caption("⚠️ החישוב אינדיקטיבי — אינו כולל ביטוח לאומי וביטוח בריאות. התייעץ עם רו\"ח.")

    # ── TAB 3: EXEMPTIONS GUIDE ───────────────────────────────────────────────
    with tab_guide:
        st.markdown('<div class="section-title">פטורים עיקריים ומועדי הגשה</div>', unsafe_allow_html=True)
        exemptions = [
            ("פטור מס שבח — דירת מגורים יחידה",
             "מי שלא מכר דירה ב-18 החודשים הקודמים ומכר דירה יחידה — פטור מלא. מגבלת שווי: ₪5,008,000 (2026).",
             "⏱️ דיווח תוך 30 יום מהמכירה לרשות המיסים"),
            ("פטור ליניארי (נכסים שנרכשו לפני 2014)",
             "החלק היחסי של הרווח שנצבר לפני 1.1.2014 — פטור ממס שבח, גם בדירה שאינה יחידה.",
             "⏱️ דיווח תוך 30 יום"),
            ("פטור מס שכירות — עד תקרה",
             "שכ\"ד חודשי עד ₪5,471 (2026) — פטור מלא ממס. מגיש דוח שנתי רק אם עבר את התקרה.",
             "⏱️ דוח שנתי עד 30/4"),
            ("פינוי-בינוי — פטור מס שבח ורכישה",
             "דיירים שמסרו דירה בפרויקט פינוי-בינוי ומקבלים דירה חדשה — פטורים ממס שבח ומס רכישה.",
             "✅ אוטומטי עם אישור הפרויקט"),
            ("עולה חדש — הנחה במס רכישה",
             "עולה חדש זכאי לשיעור מס רכישה מופחת של 0.5% על דירה ראשונה בישראל (עד תקרה).",
             "⏱️ הגשת בקשה במועד הדיווח"),
        ]
        for title, desc, timing in exemptions:
            with st.expander(f"**{title}**"):
                st.markdown(desc)
                st.caption(timing)

        st.divider()
        st.markdown('<div class="section-title">מועדי דיווח חשובים</div>', unsafe_allow_html=True)
        deadlines = [
            ("מס שבח — דיווח ותשלום", "תוך 30 יום ממועד המכירה"),
            ("מס רכישה — תשלום", "תוך 60 יום מחתימת החוזה"),
            ("מס שכירות — דוח שנתי", "עד 30 באפריל של השנה העוקבת"),
            ("ביטול שומה / השגה", "תוך 30 יום מקבלת השומה"),
        ]
        for event, deadline in deadlines:
            ca, cb = st.columns([2, 1])
            ca.markdown(f"**{event}**")
            cb.markdown(f"📅 {deadline}")


# ─── TOOL: CONTRACT ANALYSIS ─────────────────────────────────────────────────

CONTRACT_CHECKLIST = {
    "חוזה רכישה": [
        "פרטי הצדדים — שמות, ת.ז., כתובות",
        "תיאור הנכס — גוש, חלקה, כתובת, גודל",
        "מחיר ולוח תשלומים מפורט",
        "מועד מסירת החזקה",
        "מצב הנכס — פנוי / מושכר / עם מטלטלין",
        "ערבות / בטחונות (קבלן — ערבות בנקאית חוק המכר)",
        "תנאים מתלים (קבלת משכנתא, היתר, אישורים)",
        "קנסות איחור (0.5%–1% לחודש)",
        "הסדרת חריגות בנייה (אם יש)",
        "רישום בטאבו — מועד ואחריות",
        "הצהרות המוכר (אין שעבוד, עיקול, תביעה)",
        "מס שבח — מי נושא ומתי",
    ],
    "חוזה שכירות": [
        "פרטי הצדדים",
        "תיאור הנכס ומצבו",
        "תקופת השכירות + אופציה",
        "סכום שכ\"ד + מועדי תשלום",
        "הצמדה למדד / העלאה שנתית",
        "בטחונות (שיקים, ערבות בנקאית, ערבים)",
        "חלוקת אחריות לתיקונים",
        "שינויים בנכס — אישור מראש",
        "איסור על העברת שכירות לאחר",
        "הסרת בטחונות בתום השכירות",
        "תנאי פינוי מוקדם",
        "ביטוח נכס — מי אחראי",
    ],
}


def tool_contract_analysis():
    st.title("📄 ניתוח חוזים")
    st.caption("הדבק טקסט חוזה → AI מנתח, מזהה סיכונים ומפיק סיכום מקצועי + צ'קליסט")

    tab_analyze, tab_checklist = st.tabs(["🔍 ניתוח AI לחוזה", "✅ צ'קליסט בדיקה"])

    with tab_analyze:
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        contract_type = st.selectbox("סוג חוזה", ["חוזה רכישה", "חוזה שכירות", "הסכם אחר"])
        contract_text = st.text_area(
            "הדבק כאן את טקסט החוזה",
            height=280,
            placeholder="הדבק את כל נוסח החוזה כאן — ניתן להדביק גם חלקי חוזה לבחינה..."
        )

        if st.button("🤖 נתח חוזה", type="primary", use_container_width=True):
            if not contract_text.strip():
                st.error("נא להדביק טקסט חוזה")
            elif not api_key:
                st.error("נדרש Gemini API Key")
            else:
                with st.spinner("מנתח חוזה עם AI..."):
                    try:
                        genai.configure(api_key=api_key)
                        contract_model = genai.GenerativeModel(
                            model_name="gemini-2.0-flash",
                            system_instruction="""אתה עו"ד מומחה לחוזי נדל"ן ישראלי.
נתח חוזים בעברית. תמיד ציין: "ניתוח זה אינו מחליף ייעוץ משפטי פרטני".""",
                        )
                        prompt = f"""נתח את חוזה ה{contract_type} הבא והחזר JSON בלבד (ללא markdown):
{{
  "summary": "תקציר קצר של העסקה (2-3 משפטים)",
  "parties": "פרטי הצדדים כפי שמופיעים בחוזה",
  "key_terms": ["תנאי מפתח 1", "תנאי מפתח 2", ...],
  "red_flags": ["בעיה פוטנציאלית 1", "בעיה פוטנציאלית 2", ...],
  "missing_clauses": ["סעיף חסר 1", "סעיף חסר 2", ...],
  "recommendations": ["המלצה 1", "המלצה 2", ...],
  "risk_level": "נמוך / בינוני / גבוה"
}}

חוזה לניתוח:
{contract_text[:6000]}"""
                        resp = contract_model.generate_content(prompt)
                        raw = resp.text.strip()
                        if "```" in raw:
                            raw = raw.split("```")[1]
                            if raw.startswith("json"):
                                raw = raw[4:]
                        analysis = json.loads(raw)
                        st.session_state["contract_analysis"] = analysis
                    except Exception as e:
                        st.error(f"שגיאה בניתוח: {e}")

        if "contract_analysis" in st.session_state:
            a = st.session_state["contract_analysis"]
            risk = a.get("risk_level", "בינוני")
            risk_cls = "alert-green" if risk == "נמוך" else "alert-yellow" if risk == "בינוני" else "alert-red"
            risk_icon = "🟢" if risk == "נמוך" else "🟡" if risk == "בינוני" else "🔴"

            st.divider()
            st.markdown(f"""<div class="{risk_cls}">
                {risk_icon} <strong>רמת סיכון: {risk}</strong>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"**📋 תקציר:** {a.get('summary', '—')}")
            st.markdown(f"**👥 צדדים:** {a.get('parties', '—')}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ תנאי מפתח**")
                for item in a.get("key_terms", []):
                    st.markdown(f"- {item}")

                st.markdown("**💡 המלצות**")
                for item in a.get("recommendations", []):
                    st.markdown(f"- {item}")

            with col2:
                if a.get("red_flags"):
                    st.markdown("**🚩 דגלים אדומים**")
                    for item in a["red_flags"]:
                        st.markdown(f"- ⚠️ {item}")

                if a.get("missing_clauses"):
                    st.markdown("**❓ סעיפים חסרים**")
                    for item in a["missing_clauses"]:
                        st.markdown(f"- {item}")

            st.caption("⚠️ ניתוח זה הוא כלי עזר בלבד ואינו מחליף ייעוץ משפטי.")
            if st.button("🗑️ נקה ניתוח"):
                del st.session_state["contract_analysis"]
                st.rerun()

    with tab_checklist:
        st.markdown('<div class="section-title">צ\'קליסט בדיקת חוזה</div>', unsafe_allow_html=True)
        checklist_type = st.selectbox("סוג חוזה לבדיקה", list(CONTRACT_CHECKLIST.keys()))
        items = CONTRACT_CHECKLIST[checklist_type]

        if f"checklist_{checklist_type}" not in st.session_state:
            st.session_state[f"checklist_{checklist_type}"] = {item: False for item in items}

        checked_count = 0
        for item in items:
            key = f"chk_{checklist_type}_{item}"
            val = st.checkbox(item, value=st.session_state[f"checklist_{checklist_type}"].get(item, False), key=key)
            st.session_state[f"checklist_{checklist_type}"][item] = val
            if val:
                checked_count += 1

        progress = checked_count / len(items) if items else 0
        st.divider()
        st.progress(progress)
        st.caption(f"הושלם: {checked_count}/{len(items)} סעיפים ({progress*100:.0f}%)")
        if progress == 1.0:
            st.markdown('<div class="alert-green">✅ כל הסעיפים נבדקו!</div>', unsafe_allow_html=True)
        if st.button("אפס צ'קליסט"):
            st.session_state[f"checklist_{checklist_type}"] = {item: False for item in items}
            st.rerun()


# ─── TOOL: PROFESSIONALS DATABASE ────────────────────────────────────────────

PROFESSIONAL_CATEGORIES = ["עו\"ד מקרקעין", "יועץ משכנתאות", "שמאי מקרקעין", "מתווך", "קבלן שיפוצים", "רואה חשבון", "מהנדס / אדריכל", "אחר"]

SAMPLE_PROFESSIONALS = [
    {"id": "p1", "name": "דוד לוי", "category": "עו\"ד מקרקעין", "phone": "052-1234567",
     "city": "תל אביב", "rating": 5, "notes": "מומחה עסקאות יוקרה ותמ\"א 38", "email": "david@law.co.il"},
    {"id": "p2", "name": "רחל כהן", "category": "יועץ משכנתאות", "phone": "054-7654321",
     "city": "רמת גן", "rating": 5, "notes": "עובדת עם כל הבנקים, מתמחה בתמהילים מורכבים", "email": "rachel@mortgage.co.il"},
    {"id": "p3", "name": "מיכאל גרינברג", "category": "שמאי מקרקעין", "phone": "050-9876543",
     "city": "ירושלים", "rating": 4, "notes": "שמאות לנכסים מסחריים ומגורים", "email": "michael@shamai.co.il"},
    {"id": "p4", "name": "יוסי אברמוביץ", "category": "מתווך", "phone": "053-1122334",
     "city": "חיפה", "rating": 4, "notes": "התמחות קריית ים, קריית אתא", "email": ""},
]


def tool_professionals():
    st.title("👥 מאגר אנשי מקצוע")
    st.caption("ניהול רשימת אנשי מקצוע — עו\"ד, יועצי משכנתאות, שמאים, קבלנים ועוד")

    if "professionals" not in st.session_state:
        st.session_state.professionals = [p.copy() for p in SAMPLE_PROFESSIONALS]

    tab_list, tab_add = st.tabs(["📋 המאגר", "➕ הוסף איש מקצוע"])

    with tab_list:
        profs = st.session_state.professionals
        col_search, col_cat, col_city = st.columns(3)
        with col_search:
            search_p = st.text_input("🔍 חיפוש שם", placeholder="חפש לפי שם...")
        with col_cat:
            cat_p = st.selectbox("קטגוריה", ["הכל"] + PROFESSIONAL_CATEGORIES, key="prof_cat")
        with col_city:
            cities = ["הכל"] + sorted(set(p["city"] for p in profs if p["city"]))
            city_p = st.selectbox("עיר", cities)

        filtered_p = profs
        if cat_p != "הכל":
            filtered_p = [p for p in filtered_p if p["category"] == cat_p]
        if city_p != "הכל":
            filtered_p = [p for p in filtered_p if p["city"] == city_p]
        if search_p.strip():
            s = search_p.lower()
            filtered_p = [p for p in filtered_p if s in p["name"].lower()]

        st.caption(f"{len(filtered_p)} אנשי מקצוע")

        for prof in filtered_p:
            stars = "⭐" * prof.get("rating", 0)
            with st.expander(f"**{prof['name']}** — {prof['category']} · {prof['city']} {stars}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"📞 **{prof['phone']}**")
                    if prof.get("email"):
                        st.markdown(f"✉️ {prof['email']}")
                with c2:
                    st.markdown(f"🏙️ {prof['city']}")
                    st.markdown(f"⭐ דירוג: {prof.get('rating', 0)}/5")
                if prof.get("notes"):
                    st.markdown(f"📝 {prof['notes']}")
                if st.button("🗑️ מחק", key=f"del_prof_{prof['id']}"):
                    st.session_state.professionals = [p for p in profs if p["id"] != prof["id"]]
                    st.rerun()

        if filtered_p:
            csv_p = pd.DataFrame([{
                "שם": p["name"], "קטגוריה": p["category"], "טלפון": p["phone"],
                "עיר": p["city"], "דירוג": p["rating"], "הערות": p.get("notes", ""),
            } for p in filtered_p]).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("📥 ייצא CSV", data=csv_p, file_name="אנשי_מקצוע.csv", mime="text/csv")

    with tab_add:
        st.markdown('<div class="section-title">הוספת איש מקצוע חדש</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("שם מלא *")
            new_cat = st.selectbox("קטגוריה *", PROFESSIONAL_CATEGORIES, key="new_prof_cat")
            new_phone = st.text_input("טלפון *")
        with c2:
            new_city = st.text_input("עיר")
            new_email = st.text_input("אימייל")
            new_rating = st.slider("דירוג (1-5)", 1, 5, 4)
        new_notes = st.text_area("הערות / התמחות", height=80)

        if st.button("➕ הוסף לרשימה", type="primary", use_container_width=True):
            if not new_name.strip() or not new_phone.strip():
                st.error("שם וטלפון הם שדות חובה")
            else:
                new_prof = {
                    "id": str(uuid.uuid4())[:8],
                    "name": new_name.strip(),
                    "category": new_cat,
                    "phone": new_phone.strip(),
                    "city": new_city.strip(),
                    "email": new_email.strip(),
                    "rating": new_rating,
                    "notes": new_notes.strip(),
                }
                st.session_state.professionals.append(new_prof)
                st.success(f"✅ {new_name} נוסף למאגר!")
                st.rerun()


# ─── TOOL: PROPERTY DATABASE ──────────────────────────────────────────────────

PROPERTY_STATUSES = ["בחינה", "מועמד", "בהליך", "נרכש", "נדחה"]
PROPERTY_TYPES = ["דירה", "דירת גן", "בית פרטי", "דופלקס", "פנטהאוס", "נכס מסחרי", "קרקע", "אחר"]


def tool_property_db():
    st.title("🗄️ מאגר נדל\"ן")
    st.caption("מעקב ואנליזה של נכסים — השוואה, תשואה, ציון, סטטוס")

    if "property_db" not in st.session_state:
        st.session_state.property_db = []

    tab_list, tab_add, tab_compare = st.tabs(["📋 רשימת נכסים", "➕ הוסף נכס", "⚖️ השוואה"])

    with tab_list:
        props = st.session_state.property_db
        if not props:
            st.info("אין נכסים. הוסף נכסים בלשונית 'הוסף נכס'.")
        else:
            col_status, col_type = st.columns(2)
            with col_status:
                status_f = st.selectbox("סטטוס", ["הכל"] + PROPERTY_STATUSES, key="prop_status_f")
            with col_type:
                type_f = st.selectbox("סוג", ["הכל"] + PROPERTY_TYPES, key="prop_type_f")

            filtered_pr = props
            if status_f != "הכל":
                filtered_pr = [p for p in filtered_pr if p["status"] == status_f]
            if type_f != "הכל":
                filtered_pr = [p for p in filtered_pr if p["prop_type"] == type_f]

            st.caption(f"{len(filtered_pr)} נכסים")
            for prop in filtered_pr:
                price_sqm = prop["price"] / prop["size"] if prop["size"] > 0 else 0
                gross_yield = (prop["monthly_rent"] * 12 / prop["price"] * 100) if prop["price"] > 0 and prop["monthly_rent"] > 0 else 0
                status_icon = {"בחינה": "🔵", "מועמד": "🟡", "בהליך": "🟠", "נרכש": "🟢", "נדחה": "🔴"}.get(prop["status"], "⚪")
                with st.expander(f"{status_icon} **{prop['address']}** — {prop['prop_type']} · {fmt(prop['price'])}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("מחיר", fmt(prop["price"]))
                    c2.metric("₪ למ\"ר", f"₪{price_sqm:,.0f}")
                    c3.metric("תשואה ברוטו", f"{gross_yield:.1f}%" if gross_yield > 0 else "—")

                    if prop.get("notes"):
                        st.markdown(f"📝 {prop['notes']}")
                    st.caption(f"נוסף: {prop.get('date_added', '')}")

                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        new_status = st.selectbox("עדכן סטטוס", PROPERTY_STATUSES,
                                                   index=PROPERTY_STATUSES.index(prop["status"]),
                                                   key=f"status_{prop['id']}")
                        if new_status != prop["status"]:
                            prop["status"] = new_status
                            st.rerun()
                    with c_del:
                        st.write("")
                        if st.button("🗑️ מחק", key=f"del_prop_{prop['id']}"):
                            st.session_state.property_db = [p for p in props if p["id"] != prop["id"]]
                            st.rerun()

            csv_props = pd.DataFrame([{
                "כתובת": p["address"], "סוג": p["prop_type"], "מחיר": p["price"],
                "גודל (מ\"ר)": p["size"], "שכ\"ד חודשי": p["monthly_rent"],
                "סטטוס": p["status"], "הערות": p.get("notes", ""),
            } for p in filtered_pr]).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("📥 ייצא CSV", data=csv_props, file_name="נכסים.csv", mime="text/csv")

    with tab_add:
        st.markdown('<div class="section-title">הוספת נכס למעקב</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            new_address = st.text_input("כתובת / תיאור הנכס *")
            new_price = st.number_input("מחיר מבוקש (₪)", min_value=0, step=50_000, value=2_000_000)
            new_size = st.number_input("גודל (מ\"ר)", min_value=0, step=5, value=80)
        with c2:
            new_prop_type = st.selectbox("סוג נכס", PROPERTY_TYPES)
            new_rent = st.number_input("שכ\"ד חודשי אפשרי (₪)", min_value=0, step=500, value=0,
                                        help="להערכת תשואה — אפשר להשאיר 0")
            new_status_add = st.selectbox("סטטוס", PROPERTY_STATUSES)
        new_notes_prop = st.text_area("הערות", height=80)

        if st.button("➕ הוסף נכס", type="primary", use_container_width=True):
            if not new_address.strip():
                st.error("נא הכנס כתובת")
            else:
                new_prop = {
                    "id": str(uuid.uuid4())[:8],
                    "address": new_address.strip(),
                    "prop_type": new_prop_type,
                    "price": new_price,
                    "size": new_size,
                    "monthly_rent": new_rent,
                    "status": new_status_add,
                    "notes": new_notes_prop.strip(),
                    "date_added": str(date.today()),
                }
                st.session_state.property_db.append(new_prop)
                st.success(f"✅ '{new_address}' נוסף למאגר!")
                st.rerun()

    with tab_compare:
        props = st.session_state.property_db
        if len(props) < 2:
            st.info("הוסף לפחות 2 נכסים כדי להשוות.")
        else:
            prop_labels = [f"{p['address']} ({fmt(p['price'])})" for p in props]
            selected_labels = st.multiselect("בחר עד 3 נכסים להשוואה", prop_labels, max_selections=3)
            selected_props = [props[prop_labels.index(l)] for l in selected_labels if l in prop_labels]

            if selected_props:
                compare_data = []
                for p in selected_props:
                    price_sqm = p["price"] / p["size"] if p["size"] > 0 else 0
                    gross_yield = p["monthly_rent"] * 12 / p["price"] * 100 if p["price"] > 0 and p["monthly_rent"] > 0 else 0
                    compare_data.append({
                        "כתובת": p["address"],
                        "סוג": p["prop_type"],
                        "מחיר": fmt(p["price"]),
                        "גודל": f"{p['size']} מ\"ר",
                        "מחיר למ\"ר": fmt(price_sqm),
                        "שכ\"ד": fmt(p["monthly_rent"]) if p["monthly_rent"] > 0 else "—",
                        "תשואה ברוטו": f"{gross_yield:.1f}%" if gross_yield > 0 else "—",
                        "סטטוס": p["status"],
                    })
                st.dataframe(pd.DataFrame(compare_data).T, use_container_width=True)


# ─── TOOL: CONTRACT LIBRARY ───────────────────────────────────────────────────

CONTRACT_TEMPLATES = [
    {
        "id": "tmpl_1",
        "title": "זכרון דברים — רכישת דירה",
        "category": "רכישה",
        "description": "מסמך ראשוני שנחתם לפני חוזה המכר המלא. מחייב את הצדדים לעסקה.",
        "content": """זכרון דברים

נערך ונחתם ביום ___ לחודש ___ שנת ___

בין: ___________________ (ת.ז. ___________) — המוכר
לבין: ___________________ (ת.ז. ___________) — הקונה

הצדדים מסכימים בזאת:

1. **הנכס:** דירה ברח׳ ___________________, עיר ___________, גוש ___, חלקה ___, תת-חלקה ___.
2. **מחיר:** סך של ₪___________ (במילים: ___________).
3. **לוח תשלומים:**
   - ₪___________ — עם חתימת זיכרון הדברים (פיקדון)
   - ₪___________ — עם חתימת חוזה מלא
   - יתרת ₪___________ — עם מסירת החזקה
4. **מועד מסירה:** ___________________.
5. **תנאי מתלה:** העסקה כפופה לקבלת משכנתא בסך ₪___________ תוך ___ ימים.
6. הצדדים מתחייבים לחתום על חוזה מכר מלא תוך ___ ימים.

חתימת המוכר: _______________    חתימת הקונה: _______________""",
    },
    {
        "id": "tmpl_2",
        "title": "חוזה שכירות — דירת מגורים",
        "category": "שכירות",
        "description": "חוזה שכירות סטנדרטי לדירת מגורים הכולל את כל הסעיפים המקובלים.",
        "content": """הסכם שכירות — דירת מגורים

נערך ביום ___ לחודש ___ שנת ___

המשכיר: ___________________ (ת.ז. ___________), מרח׳ ___________________
השוכר: ___________________ (ת.ז. ___________), מרח׳ ___________________

1. **הנכס:** דירה בת ___ חדרים ברח׳ ___________________, קומה ___, עיר ___________.
2. **תקופת השכירות:** מיום ___ ועד ___ (אופציה: ___ חודשים נוספים בהודעה של 60 יום).
3. **שכר דירה:** ₪___________ לחודש, צמוד למדד המחירים לצרכן לבסיס ___________.
   תשלום: עד ה-___ לכל חודש, בהעברה בנקאית / שיקים.
4. **בטחונות:**
   - שיקים דחויים / ערבות בנקאית בסך ___ חודשי שכ"ד.
   - ערב: ___________________ (ת.ז. ___________).
5. **חלוקת תיקונים:**
   - המשכיר: תשתיות, צנרת, חשמל, גג, קירות נושאים.
   - השוכר: קלקולים שוטפים מתחת ₪300 לתקלה.
6. **שינויים בנכס:** אסור ללא אישור כתוב מהמשכיר.
7. **איסור העברה:** אין להסב / להשכיר משנה ללא אישור.
8. **מצב הנכס:** מסור במצב ___________________, עם הפריטים: ___________________.

חתימת המשכיר: _______________    חתימת השוכר: _______________""",
    },
    {
        "id": "tmpl_3",
        "title": "יפוי כוח לעסקת מקרקעין",
        "category": "יפוי כוח",
        "description": "יפוי כוח לעו\"ד או קרוב משפחה לביצוע עסקאות מקרקעין.",
        "content": """יפוי כוח בלתי חוזר

אני החתום מטה, ___________________ (ת.ז. ___________), מרח׳ ___________________,
מסמיך ומייפה בזאת את כוחו של:
___________________ (ת.ז. / רישיון עו"ד ___________), מרח׳ ___________________

לפעול בשמי ובמקומי לצורך:

1. רכישה / מכירה של הנכס הידוע כ: ___________________, גוש ___, חלקה ___, תת-חלקה ___.
2. חתימה על כל חוזה, מסמך, הצהרה הנוגעת לעסקה.
3. ייצוגי מול כל רשות — טאבו, מס שבח, עירייה, בנק.
4. קבלה ומסירה של כספים הנובעים מהעסקה.
5. רישום הנכס בלשכת רישום המקרקעין.

יפוי כוח זה הינו בלתי חוזר ויעמוד בתוקף עד להשלמת העסקה.

תאריך: _______________
חתימת מייפה הכוח: _______________
אימות נוטריון / עו"ד: _______________""",
    },
    {
        "id": "tmpl_4",
        "title": "הסכם שיתוף בנכס",
        "category": "שותפות",
        "description": "הסכם בין שותפים ברכישת נכס — חלוקת זכויות, הוצאות, ועקרונות מכירה עתידית.",
        "content": """הסכם שיתוף במקרקעין

נערך ביום ___ לחודש ___ שנת ___

הצדדים:
- שותף א׳: ___________________ (ת.ז. ___________) — חלק: ___%
- שותף ב׳: ___________________ (ת.ז. ___________) — חלק: ___%

לגבי הנכס: ___________________, גוש ___, חלקה ___.

1. **חלוקת בעלות:** שותף א׳ — __% · שותף ב׳ — __%.
2. **מימון:** כל שותף ממן ___% מהון עצמי ומנשא ___% מהמשכנתא.
3. **הוצאות שוטפות:** כל שותף נושא בחלקו היחסי בהוצאות (ועד בית, ביטוח, ארנונה).
4. **השכרה:** ההחלטה על השכרה והשוכר תהיה בהסכמת שני הצדדים.
5. **מכירה:** לא תהיה מכירה ללא הסכמת שני הצדדים. זכות סירוב ראשונה לשותף.
6. **פירוק שיתוף:** במקרה של חילוקי דעות — פירוק דרך בית משפט או הסכמה הדדית.

חתימת שותף א׳: _______________    חתימת שותף ב׳: _______________""",
    },
    {
        "id": "tmpl_5",
        "title": "הסכם שכ\"ט — יועץ נדל\"ן",
        "category": "שכר טרחה",
        "description": "הסכם עם יועץ השקעות נדל\"ן המגדיר את תנאי הליווי ושכר הטרחה.",
        "content": """הסכם שכר טרחה — ליווי השקעות נדל"ן

נערך ביום ___ לחודש ___ שנת ___

בין: מתן משלוף, יועץ נדל"ן, מרח׳ ___________________
לבין: ___________________ (ת.ז. ___________) — הלקוח

1. **שירותי הייעוץ כוללים:**
   - ניתוח שוק ואיתור נכסים מתאימים
   - ניתוח כלכלי ובדיקת כדאיות השקעה
   - ליווי במשא ומתן
   - תיאום עם אנשי מקצוע (עו"ד, שמאי, יועץ משכנתאות)

2. **שכר טרחה:** ₪___________ + מע"מ, לתשלום:
   - 50% עם חתימת הסכם זה
   - 50% עם חתימת חוזה רכישה

3. **תקופת ההסכם:** ___ חודשים מיום החתימה.

4. **סודיות:** הייעוץ הינו אישי וחסוי.

חתימת היועץ: _______________    חתימת הלקוח: _______________""",
    },
]


def tool_contract_library():
    st.title("📁 מאגר חוזים")
    st.caption("ספריית תבניות חוזים מוכנות לשימוש — רכישה, שכירות, יפוי כוח, שותפות")

    if "custom_templates" not in st.session_state:
        st.session_state.custom_templates = []

    all_templates = CONTRACT_TEMPLATES + st.session_state.custom_templates

    tab_lib, tab_add = st.tabs(["📚 ספריית תבניות", "➕ הוסף תבנית"])

    with tab_lib:
        cats_t = ["הכל"] + list(dict.fromkeys(t["category"] for t in all_templates))
        cat_t = st.selectbox("קטגוריה", cats_t)
        filtered_t = all_templates if cat_t == "הכל" else [t for t in all_templates if t["category"] == cat_t]

        st.caption(f"{len(filtered_t)} תבניות")
        for tmpl in filtered_t:
            with st.expander(f"**{tmpl['title']}** — {tmpl['description']}"):
                st.markdown(f"*קטגוריה: {tmpl['category']}*")
                st.text_area("תוכן התבנית", value=tmpl["content"], height=350, key=f"view_{tmpl['id']}")

                col_copy, col_dl = st.columns(2)
                with col_dl:
                    st.download_button(
                        "📥 הורד כ-TXT",
                        data=tmpl["content"].encode("utf-8"),
                        file_name=f"{tmpl['title']}.txt",
                        mime="text/plain",
                        key=f"dl_{tmpl['id']}",
                        use_container_width=True,
                    )
                if tmpl["id"].startswith("custom_") and st.button("🗑️ מחק", key=f"del_tmpl_{tmpl['id']}"):
                    st.session_state.custom_templates = [t for t in st.session_state.custom_templates if t["id"] != tmpl["id"]]
                    st.rerun()

    with tab_add:
        st.markdown('<div class="section-title">הוספת תבנית חדשה</div>', unsafe_allow_html=True)
        new_t_title = st.text_input("כותרת התבנית *")
        new_t_cat = st.text_input("קטגוריה", placeholder="לדוגמה: שכירות, רכישה, אחר")
        new_t_desc = st.text_input("תיאור קצר")
        new_t_content = st.text_area("תוכן התבנית *", height=300, placeholder="הכנס את נוסח החוזה כאן...")

        if st.button("💾 שמור תבנית", type="primary", use_container_width=True):
            if not new_t_title.strip() or not new_t_content.strip():
                st.error("כותרת ותוכן הם שדות חובה")
            else:
                st.session_state.custom_templates.append({
                    "id": f"custom_{uuid.uuid4().__str__()[:8]}",
                    "title": new_t_title.strip(),
                    "category": new_t_cat.strip() or "אחר",
                    "description": new_t_desc.strip(),
                    "content": new_t_content.strip(),
                })
                st.success("✅ תבנית נוספה!")
                st.rerun()


# ─── TOOL: DEAL MANAGEMENT ────────────────────────────────────────────────────

DEAL_STAGES = ["🔍 איתור", "📋 בדיקות", "🤝 מו\"מ", "📝 חוזה", "🏁 סגירה"]
DEAL_STAGE_CHECKLIST = {
    "🔍 איתור": [
        "איתור נכס מתאים",
        "בדיקת מחיר ראשונית vs. שוק",
        "ביקור פיזי בנכס",
        "חישוב תשואה גסה",
        "תקשורת ראשונית עם המוכר/מתווך",
    ],
    "📋 בדיקות": [
        "הפקת נסח טאבו",
        "בדיקת תיק בניין בעירייה",
        "שמאות (אם נדרש)",
        "בדק בית / מהנדס",
        "בדיקת חובות עירייה",
        "בדיקת חובות ועד בית",
        "בדיקת שעבודים ומשכנתאות",
        "בחינת היתר בנייה",
    ],
    "🤝 מו\"מ": [
        "הגשת הצעת מחיר",
        "משא ומתן על מחיר",
        "סיכום תנאים (לוח תשלומים, מועד מסירה)",
        "זכרון דברים (אופציונלי)",
        "סיכום פרטי עסקה בכתב",
    ],
    "📝 חוזה": [
        "שכירת עו\"ד מקרקעין",
        "קבלת טיוטת חוזה",
        "בדיקת חוזה עם עו\"ד",
        "הסדרת משכנתא / מימון",
        "חתימה על חוזה",
        "תשלום מס רכישה (תוך 60 יום)",
        "רישום הערת אזהרה",
    ],
    "🏁 סגירה": [
        "תשלום יתרת התמורה",
        "קבלת מפתחות",
        "פרוטוקול מסירה",
        "העברת שירותים (חשמל, מים, גז, ועד)",
        "תשלום שכ\"ט עו\"ד",
        "רישום בטאבו (תוך 30 יום)",
        "ביטוח נכס",
    ],
}


def tool_deal_mgmt():
    st.title("📋 ניהול עסקה")
    st.caption("CRM לניהול עסקאות נדל\"ן — שלבים, צ'קליסט, מועדים והערות")

    if "deals" not in st.session_state:
        st.session_state.deals = []
    if "active_deal" not in st.session_state:
        st.session_state.active_deal = None

    deals = st.session_state.deals

    col_sidebar, col_main = st.columns([1, 3])

    with col_sidebar:
        st.markdown("### עסקאות")
        if st.button("➕ עסקה חדשה", use_container_width=True, type="primary"):
            st.session_state.active_deal = "__new__"
            st.rerun()

        for deal in deals:
            stage_idx = next((i for i, s in enumerate(DEAL_STAGES) if s == deal["stage"]), 0)
            progress_pct = int((stage_idx + 1) / len(DEAL_STAGES) * 100)
            is_active = st.session_state.active_deal == deal["id"]
            btn_style = "primary" if is_active else "secondary"
            if st.button(
                f"{deal['stage']} {deal['name'][:20]}\n{fmt(deal['price'])}",
                key=f"deal_btn_{deal['id']}",
                use_container_width=True,
                type=btn_style,
            ):
                st.session_state.active_deal = deal["id"]
                st.rerun()

    with col_main:
        active_id = st.session_state.active_deal

        if active_id is None:
            if not deals:
                st.markdown("""<div class="coming-soon">
                    <div style="font-size:50px">📋</div>
                    <div style="font-size:20px;color:#60a5fa;margin:10px 0">התחל לנהל עסקאות</div>
                    <div>לחץ "עסקה חדשה" כדי להוסיף את הנכס הראשון שלך</div>
                </div>""", unsafe_allow_html=True)
            else:
                # Dashboard
                st.markdown('<div class="section-title">סיכום עסקאות</div>', unsafe_allow_html=True)
                stage_counts = {s: sum(1 for d in deals if d["stage"] == s) for s in DEAL_STAGES}
                cols_d = st.columns(len(DEAL_STAGES))
                for col, stage in zip(cols_d, DEAL_STAGES):
                    with col:
                        st.markdown(f"""<div class="metric-card">
                            <div class="label">{stage}</div>
                            <div class="value">{stage_counts[stage]}</div>
                        </div>""", unsafe_allow_html=True)

        elif active_id == "__new__":
            st.markdown('<div class="section-title">עסקה חדשה</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                nd_name = st.text_input("שם העסקה *", placeholder="לדוגמה: דירה בתל אביב")
                nd_address = st.text_input("כתובת הנכס")
                nd_price = st.number_input("מחיר עסקה (₪)", min_value=0, step=50_000, value=2_000_000)
            with c2:
                nd_stage = st.selectbox("שלב נוכחי", DEAL_STAGES)
                nd_contact = st.text_input("איש קשר (מוכר/מתווך)")
                nd_target_date = st.date_input("תאריך יעד לסגירה", value=date.today())
            nd_notes = st.text_area("הערות", height=80)

            if st.button("💾 צור עסקה", type="primary", use_container_width=True):
                if not nd_name.strip():
                    st.error("נא הכנס שם עסקה")
                else:
                    new_deal = {
                        "id": str(uuid.uuid4())[:8],
                        "name": nd_name.strip(),
                        "address": nd_address.strip(),
                        "price": nd_price,
                        "stage": nd_stage,
                        "contact": nd_contact.strip(),
                        "target_date": str(nd_target_date),
                        "notes": nd_notes.strip(),
                        "checklist": {s: {item: False for item in items} for s, items in DEAL_STAGE_CHECKLIST.items()},
                        "date_created": str(date.today()),
                    }
                    st.session_state.deals.append(new_deal)
                    st.session_state.active_deal = new_deal["id"]
                    st.rerun()

        else:
            deal = next((d for d in deals if d["id"] == active_id), None)
            if not deal:
                st.session_state.active_deal = None
                st.rerun()
                return

            # Deal header
            col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
            with col_h1:
                st.markdown(f"## {deal['name']}")
                st.caption(f"📍 {deal['address']} · {fmt(deal['price'])}")
            with col_h2:
                new_stage = st.selectbox("שלב", DEAL_STAGES,
                                          index=DEAL_STAGES.index(deal["stage"]),
                                          key=f"stage_sel_{deal['id']}")
                if new_stage != deal["stage"]:
                    deal["stage"] = new_stage
                    st.rerun()
            with col_h3:
                st.caption(f"יעד: {deal.get('target_date', '—')}")
                if st.button("🗑️ מחק עסקה", key=f"del_deal_{deal['id']}"):
                    st.session_state.deals = [d for d in deals if d["id"] != deal["id"]]
                    st.session_state.active_deal = None
                    st.rerun()

            # Stage progress bar
            stage_idx = DEAL_STAGES.index(deal["stage"])
            progress_val = (stage_idx + 1) / len(DEAL_STAGES)
            st.progress(progress_val)
            st.caption(f"התקדמות: שלב {stage_idx + 1}/{len(DEAL_STAGES)}")
            st.divider()

            tab_check, tab_notes, tab_info = st.tabs(["✅ צ'קליסט", "📝 הערות", "ℹ️ פרטי עסקה"])

            with tab_check:
                # Show checklist for all stages, highlight current
                for stage in DEAL_STAGES:
                    is_current = stage == deal["stage"]
                    is_past = DEAL_STAGES.index(stage) < stage_idx
                    header_color = "#60a5fa" if is_current else "#10b981" if is_past else "#3d5878"
                    st.markdown(f"<div style='color:{header_color};font-weight:700;margin:15px 0 5px 0'>{stage}</div>",
                                unsafe_allow_html=True)
                    items_stage = DEAL_STAGE_CHECKLIST[stage]
                    for item in items_stage:
                        key_c = f"chk_{deal['id']}_{stage}_{item}"
                        current_val = deal["checklist"].get(stage, {}).get(item, False)
                        new_val = st.checkbox(item, value=current_val, key=key_c,
                                               disabled=(not is_current and not is_past))
                        deal["checklist"].setdefault(stage, {})[item] = new_val

                # Overall progress
                total_items = sum(len(v) for v in DEAL_STAGE_CHECKLIST.values())
                checked_items = sum(
                    1 for s, items in DEAL_STAGE_CHECKLIST.items()
                    for item in items
                    if deal["checklist"].get(s, {}).get(item, False)
                )
                st.divider()
                st.progress(checked_items / total_items if total_items else 0)
                st.caption(f"סה\"כ: {checked_items}/{total_items} משימות הושלמו")

            with tab_notes:
                new_notes_deal = st.text_area("הערות ותיעוד", value=deal.get("notes", ""),
                                               height=300, key=f"notes_{deal['id']}")
                if st.button("💾 שמור הערות", key=f"save_notes_{deal['id']}"):
                    deal["notes"] = new_notes_deal
                    st.success("✅ הערות נשמרו")

            with tab_info:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**שם עסקה:** {deal['name']}")
                    st.markdown(f"**כתובת:** {deal.get('address', '—')}")
                    st.markdown(f"**מחיר:** {fmt(deal['price'])}")
                with c2:
                    st.markdown(f"**איש קשר:** {deal.get('contact', '—')}")
                    st.markdown(f"**תאריך יצירה:** {deal.get('date_created', '—')}")
                    st.markdown(f"**תאריך יעד:** {deal.get('target_date', '—')}")

                deal_json = json.dumps({k: v for k, v in deal.items() if k != "checklist"},
                                        ensure_ascii=False, indent=2)
                st.download_button("📤 ייצא עסקה (JSON)", data=deal_json.encode("utf-8"),
                                   file_name=f"עסקה_{deal['name']}.json", mime="application/json")


# ─── COMING SOON ─────────────────────────────────────────────────────────────

def tool_coming_soon(name: str):
    st.markdown(f"""<div class="coming-soon">
        <div style="font-size:60px">🚧</div>
        <div style="font-size:24px; font-weight:700; color:#60a5fa; margin:15px 0">{name}</div>
        <div>הכלי הזה בפיתוח ויתווסף בקרוב</div>
    </div>""", unsafe_allow_html=True)


# ─── ROUTER ───────────────────────────────────────────────────────────────────

if selected_tool == "calc_power":
    tool_purchase_power()
elif selected_tool == "advanced_financing":
    tool_advanced_financing()
elif selected_tool == "deal_analysis":
    tool_deal_analysis()
elif selected_tool == "laws_taxes":
    tool_laws_taxes()
elif selected_tool == "tax_authority":
    tool_tax_authority()
elif selected_tool == "contract_analysis":
    tool_contract_analysis()
elif selected_tool == "professionals":
    tool_professionals()
elif selected_tool == "property_db":
    tool_property_db()
elif selected_tool == "contract_library":
    tool_contract_library()
elif selected_tool == "deal_mgmt":
    tool_deal_mgmt()
elif selected_tool == "learning":
    tool_learning()
elif selected_tool == "ai_chat":
    tool_ai_chat()
else:
    tool_coming_soon(selected_label)
