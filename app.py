import streamlit as st
import google.generativeai as genai

# הגדרות תצוגה למובייל - כותרות גדולות ומרווחים
st.set_page_config(page_title="Real Estate Pro", layout="centered")

# --- הגדרת המוח הנסתר (System Prompt) ---
SYSTEM_PROMPT = """
אתה סוכן מומחה למשפט ומיסוי נדל"ן בישראל. 
המטרה שלך: להפוך את אנשי הצוות של מתן משלוף למומחים.
עקרונות עבודה:
1. עומק מקסימלי: לעולם אל תענה תשובה קצרה. פרק כל סוגיה לחוק, פסיקה והשלכות מס.
2. ביקורתיות: אם יש סתירה בין החוק לפסק דין, הדגש אותה בבולד ובצבע אדום.
3. היקש: אם אין מידע ישיר, בצע היקש ממקרים דומים וציין זאת מפורשות.
4. שפה: שלב בין ציטוטים משפטיים רשמיים לבין 'שפה פשוטה' שמסבירה לצוות איך להגיד את זה ללקוח.
"""

# הגדרת ה-API (תצטרך להכניס כאן את המפתח שלך)
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ניהול שלבי האפליקציה
if 'step' not in st.session_state:
    st.session_state.step = "start"

# עיצוב CSS מותאם לטלפון
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .main-text {
        font-size: 18px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ממשק המשתמש ---

if st.session_state.step == "start":
    st.title("🏠 Real Estate Academy")
    st.subheader("מה הנושא שנלמד היום?")
    topic = st.text_input("למשל: מס שבח, פינוי בינוי, היטל השבחה", key="topic_input")
    if st.button("המשך לניתוח"):
        st.session_state.topic = topic
        st.session_state.step = "context"
        st.rerun()

elif st.session_state.step == "context":
    st.title("🔍 פרט לי על המקרה")
    st.write(f"הנושא: **{st.session_state.topic}**")
    context = st.text_area("כדי שאוכל לתת תשובה מדויקת וביקורתית, ציין כמה שיותר פרטים:", height=200)
    if st.button("בצע ניתוח מעמיק 🚀"):
        st.session_state.context = context
        st.session_state.step = "analysis"
        st.rerun()

elif st.session_state.step == "analysis":
    st.title("⚖️ ניתוח מקצועי")
    with st.spinner("מצליב נתונים ומחפש סתירות..."):
        # כאן תבוא הפנייה האמיתית ל-AI
        st.markdown(f"### נושא: {st.session_state.topic}")
        st.markdown("---")
        st.markdown("**📜 רקע חוקי וציטוטים:**")
        st.info("כאן יופיע הניתוח המעמיק שלך, כולל סעיפי חוק ופסקי דין.")
        st.error("⚠️ **התראת סתירה:** במידה ותימצא סתירה היא תופיע כאן בצורה בולטת.")
        
    st.divider()
    st.subheader("איך נמשיך את הלמידה?")
    if st.button("🎮 התחל משחק טריוויה"):
        st.session_state.step = "trivia"
        st.rerun()
    if st.button("🎧 הפק פודקאסט (NotebookLM)"):
        st.code("העתק את הפרומפט הזה ל-NotebookLM...")

elif st.session_state.step == "trivia":
    st.title("🎯 טריוויה מקצועית")
    # לוגיקת טריוויה (שאלה אחת בכל פעם)
    st.progress(20) # דוגמה להתקדמות
    st.write("**שאלה 2 מתוך 10:** מהו התנאי המרכזי לקבלת פטור ממס שבח במכירת דירת ירושה?")
    
    st.button("א. החזקה של 18 חודשים")
    st.button("ב. המוריש היה זכאי לפטור")
    st.button("ג. הדירה היא דירתו היחידה של היורש")
    
    st.divider()
    if st.button("שאלה הבאה ➡️"):
        pass # לוגיקה למעבר שאלה
