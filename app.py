import os
import pandas as pd
import plotly.express as px
import streamlit as st

# הגדרת עמוד ב-Streamlit
st.set_page_config(
    page_title="לוח בקרה אישי",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# עיצוב מותאם לתמיכה בעברית (RTL)
st.markdown(
    """
    <style>
    div[data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SHIFTS_FILE = "shifts_data.csv"

# טעינת נתוני משמרות מקובץ CSV (שמירה קבועה)
def load_shifts():
    if os.path.exists(SHIFTS_FILE):
        return pd.read_csv(SHIFTS_FILE)
    else:
        return pd.DataFrame(
            columns=["תאריך", "תפקיד", "שעות", "תעריף לשעה", "סה כ לתשלום"]
        )

def save_shifts(df):
    df.to_csv(SHIFTS_FILE, index=False)

# כותרת ראשית
st.title("📊 לוח בקרה אישי - מעקב משמרות, לימודים וכושר")
st.write("מערכת מרכזית לניהול שגרת העבודה, הלימודים והאימונים.")

# חלוקה לכרטיסיות (Tabs)
tab1, tab2, tab3 = st.tabs([
    "💼 מעקב משמרות", 
    "📚 לימודי רפואה", 
    "🏃 יומן כושר (3,000מ' / קרוספיט)"
])

# ==========================================
# כרטיסייה 1: מעקב משמרות
# ==========================================
with tab1:
    st.header("ניהול וחישוב משמרות")

    shifts_df = load_shifts()

    col_form, col_stats = st.columns([1, 2])

    with col_form:
        st.subheader("הוספת משמרת חדשה")
        with st.form("add_shift_form", clear_on_submit=True):
            shift_date = st.date_input("תאריך המשמרת")
            role = st.selectbox("תפקיד", ["פראמדיק", "סטודנט לרפואה", "הדרכה/איחוד הצלה"])
            hours = st.number_input("מספר שעות", min_value=0.5, max_value=24.0, value=8.0, step=0.5)
            rate = st.number_input("תעריף לשעה (₪)", min_value=0, value=60, step=5)

            submitted = st.form_submit_button("שמור משמרת")
            if submitted:
                total_pay = hours * rate
                new_row = pd.DataFrame([{
                    "תאריך": str(shift_date),
                    "תפקיד": role,
                    "שעות": hours,
                    "תעריף לשעה": rate,
                    "סה כ לתשלום": total_pay
                }])
                shifts_df = pd.concat([shifts_df, new_row], ignore_index=True)
                save_shifts(shifts_df)
                st.success("המשמרת נשמרה בהצלחה!")
                st.rerun()

    with col_stats:
        if not shifts_df.empty:
            total_hours = shifts_df["שעות"].sum()
            total_income = shifts_df["סה כ לתשלום"].sum()
            avg_hours = shifts_df["שעות"].mean()

            m1, m2, m3 = st.columns(3)
            m1.metric("סה\"כ שעות", f"{total_hours:.1f} ש'")
            m2.metric("צפי הכנסה", f"₪{total_income:,.0f}")
            m3.metric("ממוצע למשמרת", f"{avg_hours:.1f} ש'")

            st.subheader("חלוקת שעות לפי תפקיד")
            fig = px.pie(
                shifts_df,
                values="שעות",
                names="תפקיד",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("עדיין לא נרשמו משמרות. השתמש בטופס מימין כדי להוסיף.")

    st.subheader("היסטוריית משמרות")
    if not shifts_df.empty:
        st.dataframe(shifts_df, use_container_width=True)
        if st.button("מחק את כל הנתונים"):
            if os.path.exists(SHIFTS_FILE):
                os.remove(SHIFTS_FILE)
                st.warning("הנתונים נמחקו.")
                st.rerun()

# ==========================================
# כרטיסייה 2: לימודי רפואה
# ==========================================
with tab2:
    st.header("מעקב מוכנות למבחנים")

    topics = [
        "רפואה דחופה וטראומה",
        "רפואה פנימית",
        "פרמקולוגיה",
        "רפואת ילדים",
        "כירורגיה"
    ]

    for topic in topics:
        key_name = f"progress_{topic}"
        default_val = st.session_state.get(key_name, 50)
        val = st.slider(f"אחוז מוכנות: {topic}", 0, 100, value=default_val, key=key_name)
        st.progress(val / 100)

# ==========================================
# כרטיסייה 3: כושר
# ==========================================
with tab3:
    st.header("מעקב אימונים")

    col_run, col_crossfit = st.columns(2)

    with col_run:
        st.subheader("מגמת ריצת 3,000 מטר")
        run_data = pd.DataFrame({
            "תאריך": ["2026-08-01", "2026-09-01", "2026-10-01"],
            "זמן (בדקות)": [19.5, 18.8, 18.0]
        })
        fig_run = px.line(
            run_data, 
            x="תאריך", 
            y="זמן (בדקות)", 
            markers=True, 
            title="שיפור זמנים ב-3000 מטר"
        )
        fig_run.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_run, use_container_width=True)

    with col_crossfit:
        st.subheader("אימוני קרוספיט שבועיים")
        st.number_input("מספר אימונים השבוע", min_value=0, max_value=7, value=2)
        st.text_area("הערות ל-WOD / דגשים להבא", "דגש על טכניקה ועבודה רציפה")
