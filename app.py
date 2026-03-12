import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
import json
from datetime import date
import google.generativeai as genai

st.set_page_config(page_title="Real Estate Pro | מתן משלוף", layout="wide", page_icon="🏠")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f1923; }
    [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
    .metric-card {
        background: linear-gradient(135deg, #1a2a3a, #0f1923);
        border: 1px solid #2a3f55;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card .label { font-size: 13px; color: #8899aa; margin-bottom: 4px; }
    .metric-card .value { font-size: 26px; font-weight: 700; color: #4fc3f7; }
    .metric-card .sub   { font-size: 12px; color: #667788; margin-top: 4px; }
    .alert-green  { background:#0d3325; border:1px solid #1b5e3b; border-radius:10px; padding:15px; }
    .alert-yellow { background:#332b00; border:1px solid #5c4a00; border-radius:10px; padding:15px; }
    .alert-red    { background:#3a0d0d; border:1px solid #7a1a1a; border-radius:10px; padding:15px; }
    .section-title { font-size:18px; font-weight:700; color:#4fc3f7; margin:20px 0 10px 0; }
    .coming-soon {
        text-align:center; padding:80px 20px;
        color:#556677; font-size:18px;
    }
    .stButton>button { border-radius:10px; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR NAVIGATION ───────────────────────────────────────────────────────
TOOLS = {
    "🏦 מחשבון יכולת רכישה": "calc_power",
    "🔧 מימון מתוחכם": "advanced_financing",
    "📊 ניתוח עסקה": "deal_analysis",
    "⚖️ חוקים ומיסים": "coming",
    "🎓 מערכת למידה": "coming",
    "🤖 צ'אט AI": "ai_chat",
    "📄 ניתוח חוזים": "coming",
    "🏛️ רשות המיסים": "coming",
    "👥 מאגר אנשי מקצוע": "coming",
    "🗄️ מאגר נדל\"ן": "coming",
    "📁 מאגר חוזים": "coming",
    "📋 ניהול עסקה": "coming",
}

with st.sidebar:
    st.markdown("## 🏠 Real Estate Pro")
    st.markdown("*פלטפורמת הנדל\"ן של מתן משלוף*")
    st.divider()
    selected_label = st.radio("בחר כלי:", list(TOOLS.keys()), label_visibility="collapsed")
    selected_tool = TOOLS[selected_label]


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
TRACK_COLORS = ["#4fc3f7", "#81c784", "#ffb74d"]
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
        title=title,
        paper_bgcolor="#0f1923", plot_bgcolor="#0f1923",
        font=dict(color="#e8e8e8"),
        xaxis=dict(gridcolor="#1a2a3a", title="חודש"),
        yaxis=dict(gridcolor="#1a2a3a", title="₪"),
        legend=dict(bgcolor="#1a2a3a"),
        margin=dict(l=10, r=10, t=40, b=10),
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
            fill="tozeroy", fillcolor="rgba(79,195,247,0.15)",
            line=dict(color="#4fc3f7", width=2),
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
            fill="tozeroy", fillcolor="rgba(229,115,115,0.35)",
            line=dict(color="#e57373", width=2),
        ))
        fig2.add_trace(go.Scatter(
            x=months, y=principals, mode="lines", name="קרן",
            fill="tozeroy", fillcolor="rgba(129,199,132,0.35)",
            line=dict(color="#81c784", width=2),
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

    score_color = "#4fc3f7" if score >= 70 else "#ffb74d" if score >= 50 else "#e57373"
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
        colors_cf = ["#81c784" if v >= 0 else "#e57373" for v in cum_cf]
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
            fill="tozeroy", fillcolor="rgba(79,195,247,0.1)",
            line=dict(color="#4fc3f7", width=2)))
        fig_exit.add_trace(go.Scatter(
            x=yrs_30, y=mort_30, name="יתרת משכנתא",
            fill="tozeroy", fillcolor="rgba(229,115,115,0.1)",
            line=dict(color="#e57373", width=2)))
        fig_exit.add_trace(go.Scatter(
            x=yrs_30, y=equity_30, name="הון עצמי בנכס",
            line=dict(color="#81c784", width=2, dash="dash")))
        fig_exit.add_vline(x=exit_year, line_dash="dot", line_color="#ffb74d",
                           annotation_text=f"יציאה שנה {exit_year}",
                           annotation_font_color="#ffb74d")
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
        model_name="gemini-1.5-flash",
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


# ─── COMING SOON ─────────────────────────────────────────────────────────────

def tool_coming_soon(name: str):
    st.markdown(f"""<div class="coming-soon">
        <div style="font-size:60px">🚧</div>
        <div style="font-size:24px; font-weight:700; color:#4fc3f7; margin:15px 0">{name}</div>
        <div>הכלי הזה בפיתוח ויתווסף בקרוב</div>
    </div>""", unsafe_allow_html=True)


# ─── ROUTER ───────────────────────────────────────────────────────────────────

if selected_tool == "calc_power":
    tool_purchase_power()
elif selected_tool == "advanced_financing":
    tool_advanced_financing()
elif selected_tool == "deal_analysis":
    tool_deal_analysis()
elif selected_tool == "ai_chat":
    tool_ai_chat()
else:
    tool_coming_soon(selected_label)
