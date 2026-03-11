import streamlit as st

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
    "🔧 מימון מתוחכם": "coming",
    "📊 ניתוח עסקה": "coming",
    "⚖️ חוקים ומיסים": "coming",
    "🎓 מערכת למידה": "coming",
    "🤖 צ'אט AI": "coming",
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
else:
    tool_coming_soon(selected_label)
