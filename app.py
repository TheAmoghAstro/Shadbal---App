import streamlit as st
import pandas as pd
import datetime

# Page Configuration
st.set_page_config(
    page_title="ષડ્બળ એનાલિટિક્સ ડેશબોર્ડ (The Amogh Astro)",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-male {
        background-color: #f59e0b;
        color: #020617;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
    }
    .badge-female {
        background-color: #ec4899;
        color: #ffffff;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
    }
    .interpretation-box {
        background-color: #0b1329;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Parashari Benchmarks (Shashtiamsa)
BENCHMARKS_SHASHTIAMSA = {
    "Sun": {"name": "સૂર્ય", "req": 390.0, "rupa": 6.5},
    "Moon": {"name": "ચંદ્ર", "req": 360.0, "rupa": 6.0},
    "Mars": {"name": "મંગળ", "req": 300.0, "rupa": 5.0},
    "Mercury": {"name": "બુધ", "req": 420.0, "rupa": 7.0},
    "Jupiter": {"name": "ગુરુ", "req": 390.0, "rupa": 6.5},
    "Venus": {"name": "શુક્ર", "req": 330.0, "rupa": 5.5},
    "Saturn": {"name": "શનિ", "req": 300.0, "rupa": 5.0}
}

# ----------------- Helper Functions ----------------- #

def normalize_to_100_scale(actual: float, required: float, max_limit: float = 600.0) -> float:
    """Calculates 0-100% score anchored at 60% passing benchmark."""
    if actual < required:
        score = (actual / required) * 60.0
    else:
        score = 60.0 + ((actual - required) / (max_limit - required)) * 40.0
    return round(min(100.0, max(0.0, score)), 1)

def get_status_meta(score: float):
    if score >= 85:
        return "સર્વોચ્ચ બળવાન", "#10b981"
    elif score >= 70:
        return "ઉત્તમ બળ", "#22c55e"
    elif score >= 60:
        return "સક્ષમ (પાસ)", "#38bdf8"
    elif score >= 50:
        return "સીમાવર્તી", "#f59e0b"
    else:
        return "નિર્બળ", "#f43f5e"

def generate_interpretations(metrics: dict, gender: str) -> tuple:
    """Generates gender-tailored relationship and health texts."""
    v = metrics["Venus"]["score_100"]
    j = metrics["Jupiter"]["score_100"]
    m = metrics["Mars"]["score_100"]
    s = metrics["Sun"]["score_100"]
    mo = metrics["Moon"]["score_100"]
    sat = metrics["Saturn"]["score_100"]

    if gender == "પુરુષ (Male)":
        honorific = "શ્રીમાન (જાતક)"
        if v >= 60.0:
            rel_txt = f"પુરુષ કુંડળીમાં પત્ની અને વૈવાહિક સુખના મુખ્ય કારક **શુક્ર ({v}%)** ૬૦% પાસિંગ માર્ક કરતાં ઉપર હોવાથી દાંપત્યજીવનમાં આકર્ષણ, સુમેળ અને પત્ની તરફથી ઉત્તમ સાથ-સહકાર પ્રાપ્ત થશે."
        else:
            rel_txt = f"પુરુષ કુંડળીમાં પત્ની સુખના કારક **શુક્ર ({v}%)** બેન્ચમાર્કથી નીચે નિર્બળ છે. આથી અપેક્ષાઓનું નિયમન રાખવું, સંબંધોમાં પરસ્પર સંવાદ વધારવો અને શુક્રના ઉપાય (જેમ કે શુક્રવારનું વ્રત અથવા લક્ષ્મી ઉપાસના) કરવા હિતાવહ રહેશે."
        rel_txt += f" કુટુંબ વૃદ્ધિ અને સંતાન સુખના કારક ગુરુનું બળ **{j}%** છે."

        if s >= 60.0:
            health_txt = f"વાઇટાલિટી અને આંતરિક રોગપ્રતિકારક શક્તિના કારક **સૂર્ય ({s}%)** સક્ષમ છે, જેથી શારીરિક સ્ટેમિના અને આત્મવિશ્વાસ ઉત્તમ રહેશે."
        else:
            health_txt = f"જીવનશક્તિના કારક **સૂર્ય ({s}%)** નબળા હોવાથી આંખોની સંભાળ, વિટામિન D તથા અતિશય થાક સામે નિયમિત સૂર્ય નમસ્કાર ફાયદાકારક રહેશે."
        health_txt += f" સ્નાયુ અને વાત રોગ (Vata Balance) ના નિયમન માટે શનિનું બળ **{sat}%** પર સ્થિત છે."

    else:
        honorific = "શ્રીમતી/કુમારી (જાતિકા)"
        if j >= 60.0:
            rel_txt = f"સ્ત્રી જાતિકા માટે પતિ સુખ અને વૈવાહિક સ્થિરતાના મુખ્ય કારક **ગુરુ ({j}%)** સક્ષમ હોવાથી પતિ તરફથી શ્રેષ્ઠ આદર, પરિપક્વ માર્ગદર્શન અને સુખી દાંપત્યજીવન મળશે."
        else:
            rel_txt = f"સ્ત્રી કુંડળીમાં પતિ કારક **ગુરુ ({j}%)** ૬૦% પાસિંગ લાઇન કરતાં નબળા છે. આથી લગ્ન સંબંધી નિર્ણયોમાં વડીલોની સલાહ લેવી અને ગુરુની ઉપાસના (કેસર તિલક / વિષ્ણુ સહસ્ત્રનામ) કરવી લાભદાયી રહેશે."
        rel_txt += f" માંગલ્ય અને સૌભાગ્ય વૃદ્ધિ માટે પૂરક પરિબળ શુક્ર **{v}%** અને મંગળ **{m}%** ક્ષમતા દર્શાવે છે."

        if mo >= 60.0 and m >= 60.0:
            health_txt = f"હોર્મોનલ અને માનસિક સંતુલન માટે **ચંદ્ર ({mo}%)** તથા રક્ત પરિભ્રમણ માટે **મંગળ ({m}%)** બંને સક્ષમ હોવાથી શારીરિક ઊર્જા અને માનસિક સ્થિરતા ઉત્તમ રહેશે."
        else:
            health_txt = f"સ્ત્રી સ્વાસ્થ્યમાં **ચંદ્ર ({mo}%)** અથવા **મંગળ ({m}%)** બેન્ચમાર્કથી નીચે હોવાથી રક્ત સંબંધી બાબતો (હિમોગ્લોબિન / આયર્ન), હોર્મોનલ બેલેન્સ અને પૂરતી ઊંઘ પ્રત્યે વિશેષ જાગૃતિ રાખવી."
        health_txt += f" સામાન્ય રોગપ્રતિકારક શક્તિ (સૂર્ય) **{s}%** પર છે."

    return honorific, rel_txt, health_txt

# ----------------- Sidebar Inputs ----------------- #

st.sidebar.title("કુંડળી & જાતક વિગતો")

client_name = st.sidebar.text_input("પૂરું નામ", value="Mita")
client_gender = st.sidebar.radio("લિંગ (Gender)", ["પુરુષ (Male)", "સ્ત્રી (Female)"], index=1)

# જન્મ તારીખ અને સમય બાજુબાજુમાં (Columns)
col_date, col_time = st.sidebar.columns(2)
dob = col_date.date_input("જન્મ તારીખ", value=datetime.date(1995, 11, 16))
tob = col_time.time_input("જન્મ સમય", value=datetime.time(10, 30))

pob = st.sidebar.text_input("જન્મ સ્થળ", value="અમદાવાદ")

unit_choice = st.sidebar.selectbox("ગણતરી યુનિટ", ["ષષ્ટ્યાંશ (Shashtiamsa ~ 300-500)", "રૂપા (Rupas ~ 5.0-8.5)"], index=1)
is_rupa = "રૂપા" in unit_choice

st.sidebar.markdown("---")
st.sidebar.subheader("ગ્રહ ષડ્બળ સ્કોર ઇનપુટ")

# Sample Presets
preset = st.sidebar.selectbox("સેમ્પલ પ્રીસેટ લોડ કરો", ["કસ્ટમ / મેન્યુઅલ", "સંતુલિત કુંડળી", "બળવાન ગુરુ (ઉચ્ચ જ્ઞાન)", "પીડિત શુક્ર (વૈવાહિક સંઘર્ષ)"])

default_values = {
    "Sun": 415.2, "Moon": 382.0, "Mars": 345.5,
    "Mercury": 435.0, "Jupiter": 370.0, "Venus": 355.0, "Saturn": 290.0
}
if preset == "બળવાન ગુરુ (ઉચ્ચ જ્ઞાન)":
    default_values = {"Sun": 430.0, "Moon": 395.0, "Mars": 310.0, "Mercury": 425.0, "Jupiter": 510.0, "Venus": 340.0, "Saturn": 315.0}
elif preset == "પીડિત શુક્ર (વૈવાહિક સંઘર્ષ)":
    default_values = {"Sun": 405.0, "Moon": 370.0, "Mars": 360.0, "Mercury": 410.0, "Jupiter": 420.0, "Venus": 240.0, "Saturn": 280.0}

raw_inputs = {}
for p_key, meta in BENCHMARKS_SHASHTIAMSA.items():
    default_val = default_values[p_key] / 60.0 if is_rupa else default_values[p_key]
    step_val = 0.1 if is_rupa else 1.0
    val = st.sidebar.number_input(
        f"{meta['name']} ({p_key})",
        min_value=0.0,
        max_value=15.0 if is_rupa else 900.0,
        value=float(round(default_val, 2)),
        step=step_val
    )
    raw_inputs[p_key] = val * 60.0 if is_rupa else val

# ----------------- Main Dashboard Calculations ----------------- #

total_energy = sum(raw_inputs.values())
if total_energy == 0:
    st.error("કુલ ષડ્બળ પોઇન્ટ્સ શૂન્ય હોઈ શકે નહીં.")
    st.stop()

processed_metrics = {}
for p_key, meta in BENCHMARKS_SHASHTIAMSA.items():
    actual = raw_inputs[p_key]
    req = meta["req"]
    score_100 = normalize_to_100_scale(actual, req)
    share_pct = round((actual / total_energy) * 100.0, 1)
    status_label, status_color = get_status_meta(score_100)
    
    processed_metrics[p_key] = {
        "name": meta["name"],
        "actual": actual / 60.0 if is_rupa else actual,
        "req": meta["rupa"] if is_rupa else meta["req"],
        "score_100": score_100,
        "share_pct": share_pct,
        "status": status_label,
        "color": status_color
    }

honorific, relationship_text, health_text = generate_interpretations(processed_metrics, client_gender)

# Format Birth Time cleanly (HH:MM AM/PM)
formatted_time = tob.strftime("%I:%M %p")

# ----------------- UI Layout & Rendering ----------------- #

badge_class = "badge-male" if client_gender == "પુરુષ (Male)" else "badge-female"
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:12px; margin-bottom:16px;">
    <div>
        <span class="{badge_class}">{honorific}</span>
        <h2 style="margin:4px 0 0 0; color:#f8fafc;">{client_name} - ષડ્બળ ક્ષમતા એનાલિટિક્સ</h2>
        <span style="color:#94a3b8; font-size:0.85rem;">જન્મ તારીખ: <b>{dob.strftime('%d/%m/%Y')}</b> | સમય: <b>{formatted_time}</b> | સ્થળ: <b>{pob}</b></span>
    </div>
    <div style="text-align:right;">
        <span style="color:#94a3b8; font-size:0.8rem;">કુલ ગ્રહીય ઉર્જા</span><br>
        <strong style="color:#f59e0b; font-size:1.3rem;">{round(total_energy / (60.0 if is_rupa else 1.0), 1)} {'રૂપા' if is_rupa else 'ષષ્ટ્યાંશ'}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# 7 Planets Grid
st.subheader("૦–૧૦૦% ગ્રહ ક્ષમતા સ્કોરકાર્ડ (૬૦% બેન્ચમાર્ક એન્કડ)")

grid_cols = st.columns(4)
col_idx = 0

for p_key, data in processed_metrics.items():
    with grid_cols[col_idx % 4]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:#f8fafc; font-size:1.05rem;">{data['name']} <span style="font-size:0.75rem; color:#64748b;">({p_key})</span></strong>
                <span style="background-color:{data['color']}22; color:{data['color']}; border:1px solid {data['color']}55; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:600;">
                    {data['status']}
                </span>
            </div>
            <div style="margin: 10px 0 6px 0; display:flex; justify-content:space-between; align-items:baseline;">
                <span style="font-size:2rem; font-weight:800; color:{data['color']};">{data['score_100']}%</span>
                <span style="font-size:0.75rem; color:#94a3b8;">હિસ્સો: {data['share_pct']}%</span>
            </div>
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">
                પ્રાપ્ત: <b style="color:#cbd5e1;">{round(data['actual'], 1)}</b> / જરૂર: {round(data['req'], 1)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(float(data['score_100'] / 100.0))
        st.caption("૦% ──────── ૬૦% પાસિંગ ──────── ૧૦૦%")
    col_idx += 1

st.markdown("---")

# Gender Tailored Interpretations Section
st.subheader(f"લિંગ-આધારિત વૈદિક ફળાદેશ ({honorific})")

col_rel, col_health = st.columns(2)

with col_rel:
    st.markdown(f"""
    <div class="interpretation-box" style="border-left-color: #ec4899;">
        <h4 style="color:#f472b6; margin-top:0;">💍 દાંપત્ય & ભાગીદારી સંબંધો</h4>
        <p style="color:#e2e8f0; font-size:0.92rem; line-height:1.6;">
            {relationship_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_health:
    st.markdown(f"""
    <div class="interpretation-box" style="border-left-color: #10b981;">
        <h4 style="color:#34d399; margin-top:0;">🌿 શારીરિક વાઇટાલિટી અને સ્વાસ્થ્ય</h4>
        <p style="color:#e2e8f0; font-size:0.92rem; line-height:1.6;">
            {health_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Analytical Table View
with st.expander("વિગતવાર સારાંશ ટેબલ અને એક્સપોર્ટ"):
    table_rows = []
    for k, v in processed_metrics.items():
        table_rows.append({
            "ગ્રહ (Planet)": f"{v['name']} ({k})",
            "પ્રાપ્ત સ્કોર": round(v['actual'], 2),
            "લઘુત્તમ જરૂરિયાત": round(v['req'], 2),
            "૦-૧૦૦% ક્ષમતા": f"{v['score_100']}%",
            "કુલ ઉર્જા હિસ્સો %": f"{v['share_pct']}%",
            "પરિણામ સ્થિતિ": v['status']
        })
    df_report = pd.DataFrame(table_rows)
    st.dataframe(df_report, use_container_width=True)

    csv_data = df_report.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="રિપોર્ટ CSV ડાઉનલોડ કરો",
        data=csv_data,
        file_name=f"{client_name}_shadbala_report.csv",
        mime="text/csv"
    )
