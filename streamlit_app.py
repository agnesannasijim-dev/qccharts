import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page configuration
st.set_page_config(
    page_title="QC Charts",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        .main-header {
            font-size: 48px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 24px;
            font-weight: 500;
            color: #4a4a4a;
            margin-bottom: 30px;
        }
        .section-divider {
            margin: 40px 0;
            border-top: 2px solid #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# Main header - removed icon, made more professional
st.markdown('<div class="main-header">QC Charts</div>', unsafe_allow_html=True)


# Add your content sections below
st.header("Features")
st.write("Your QC charting features will go here...")

# ── Hormone acceptance limits (mean, SD) ────────────────────────────────
HORMONE_LIMITS = {
    "11-deoxycorticosterone":           {"mean": 3886818.2972973,  "sd": 464077},
    "11-deoxycortisol":      {"mean": 2501761,  "sd": 448085},
    "17-OHP":         {"mean": 3108554,  "sd": 310483},
    "21-deoxycortisol":           {"mean": 620665,  "sd": 116829},
    "Aldosterone":           {"mean": 285861,  "sd": 32149},
    "Androstenedione":           {"mean": 9805975,  "sd": 1188447},
    "Corticosterone":                   {"mean": 1280725,  "sd": 316788},
    "Cortisol":                 {"mean": 852575,  "sd": 91374},
    "Cortisone":        {"mean": 1020745,  "sd": 178291},
    "Dexamethasone":                    {"mean": 138210,  "sd": 16339},
    "DHEA":     {"mean": 40226,  "sd": 6058},
    "DHEA-S":               {"mean": 33152,  "sd": 4877},
    "DHT":            {"mean": 264301,  "sd": 46227},
    "Progesterone":                   {"mean": 3332469,  "sd": 549259},
    "Testosterone":                    {"mean": 8762589,  "sd": 1004209},
}

DATA_FILE = "qc_data.csv"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem; font-weight: 700;
        color: #1a1a2e; margin-bottom: 0rem;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 1.05rem; color: #555;
        margin-top: 0.2rem; margin-bottom: 1.5rem;
    }
    .limit-card {
        background: #f0f4ff;
        border-left: 4px solid #4e6ef2;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 10px 0 16px 0;
        font-size: 0.95rem;
    }
    .pass-box {
        background: #d4edda; color: #155724;
        border-radius: 8px; padding: 14px 18px;
        font-weight: 600; font-size: 1rem;
        border-left: 5px solid #28a745;
    }
    .fail-box {
        background: #f8d7da; color: #721c24;
        border-radius: 8px; padding: 14px 18px;
        font-weight: 600; font-size: 1rem;
        border-left: 5px solid #dc3545;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    div[data-testid="metric-container"] {
        background: #f8f9fa;
        border: 0.5px solid #dee2e6;
        border-radius: 10px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ── Data helpers ───────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    return pd.DataFrame(columns=["hormone","initials","email","datetime","sst_value","status"])

def save_entry(hormone, initials, email, sst_value, status):
    df = load_data()
    new_row = {
        "hormone":   hormone,
        "initials":  initials.upper(),
        "email":     email.lower().strip(),
        "datetime":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sst_value": round(sst_value, 4),
        "status":    status,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def check_limits(hormone, value):
    lim   = HORMONE_LIMITS[hormone]
    mean  = lim["mean"]
    sd    = lim["sd"]
    upper = mean + 2 * sd
    lower = mean - 2 * sd
    status = "PASS" if lower <= value <= upper else "FAIL"
    return status, mean, sd, upper, lower

def send_email_alert(to_email, initials, hormone, value, upper, lower,
                     smtp_server, smtp_port, sender_email, sender_password):
    try:
        msg = MIMEMultipart()
        msg["From"]    = sender_email
        msg["To"]      = to_email
        msg["Subject"] = f"⚠️ QC Alert: {hormone} SST out of range"
        body = f"""Dear {initials},

This is an automated alert from QC Charts Made Easier.

The SST value entered for {hormone} is OUTSIDE the ±2SD acceptance limits.

  Hormone    : {hormone}
  Value      : {value}
  Valid range: {lower:.4f} – {upper:.4f}
  Date/Time  : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Please investigate and do not report patient results until the issue is resolved.

— QC Charts Made Easier
"""
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)

# ── Levey-Jennings chart ───────────────────────────────────────────────────────
def plot_lj_chart(hormone, df_h):
    lim  = HORMONE_LIMITS[hormone]
    mean = lim["mean"]
    sd   = lim["sd"]

    x      = list(range(len(df_h)))
    labels = [
        f"{row['initials']}  —  {pd.to_datetime(row['datetime']).strftime('%d %b %Y %H:%M')}"
        for _, row in df_h.iterrows()
    ]
    colors = ["#dc3545" if s == "FAIL" else "#2563eb" for s in df_h["status"]]

    fig = go.Figure()

    # Shaded bands
    for n, fill in [(3,"rgba(220,53,69,0.07)"),(2,"rgba(255,193,7,0.10)"),(1,"rgba(37,99,235,0.06)")]:
        fig.add_hrect(y0=mean - n*sd, y1=mean + n*sd, fillcolor=fill, line_width=0)

    # Control lines
    line_cfg = [
        (mean + 3*sd, "red",        "dash",   "+3SD"),
        (mean - 3*sd, "red",        "dash",   "−3SD"),
        (mean + 2*sd, "#e67e00",    "dash",   "+2SD"),
        (mean - 2*sd, "#e67e00",    "dash",   "−2SD"),
        (mean + 1*sd, "#2563eb",    "dot",    "+1SD"),
        (mean - 1*sd, "#2563eb",    "dot",    "−1SD"),
        (mean,        "#16a34a",    "solid",  "Mean"),
    ]
    for y_val, color, dash, label in line_cfg:
        fig.add_hline(
            y=y_val, line_color=color, line_dash=dash, line_width=1.4,
            annotation_text=f"<b>{label}</b> {y_val:.3f}",
            annotation_position="right",
            annotation_font=dict(size=11, color=color)
        )

    # Data trace
    fig.add_trace(go.Scatter(
        x=x, y=df_h["sst_value"],
        mode="lines+markers",
        line=dict(color="#94a3b8", width=1.5),
        marker=dict(color=colors, size=11, line=dict(width=1.5, color="white")),
        text=labels,
        hovertemplate="<b>%{text}</b><br>Value: %{y}<extra></extra>",
        name="SST value"
    ))

    # Red X markers for failures
    fail_df = df_h[df_h["status"] == "FAIL"]
    if not fail_df.empty:
        fail_x = [df_h.index.get_loc(i) if i in df_h.index else list(df_h.index).index(i)
                  for i in fail_df.index]
        fig.add_trace(go.Scatter(
            x=[list(df_h.reset_index().index)[list(df_h.index).index(i)] for i in fail_df.index],
            y=fail_df["sst_value"],
            mode="markers",
            marker=dict(symbol="x", color="#dc3545", size=14, line=dict(width=2.5)),
            name="FAIL",
            hoverinfo="skip"
        ))

    fig.update_layout(
        title=dict(text=f"<b>Levey-Jennings Chart</b> — {hormone}", font=dict(size=16, color="#1a1a2e")),
        xaxis=dict(
            title="Run number",
            tickvals=x,
            ticktext=[f"#{i+1}" for i in x],
            showgrid=True, gridcolor="#f1f5f9"
        ),
        yaxis=dict(
            title=f"SST Value",
            showgrid=True, gridcolor="#f1f5f9"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=460,
        showlegend=False,
        margin=dict(r=120, t=50, b=50, l=60),
        hovermode="x unified"
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="main-title">📊 QC Charts Made Easier</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Sex Steroid Hormone Panel · Internal Quality Control System</p>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Email Alert Settings")
    st.caption("Configure SMTP to enable automatic alerts when an SST value fails.")
    smtp_server   = st.text_input("SMTP Server",    value="smtp.gmail.com")
    smtp_port     = st.number_input("SMTP Port",    value=587, step=1)
    sender_email  = st.text_input("Sender Email",   placeholder="alerts@yourlab.com")
    sender_pass   = st.text_input("Sender Password",type="password")
    email_enabled = bool(sender_email and sender_pass)
    if email_enabled:
        st.success("✅ Email alerts enabled")
    else:
        st.info("Enter credentials to enable email alerts.")

    st.divider()
    st.markdown("## 📋 Acceptance Limits")
    st.caption("Pre-loaded ±2SD limits for each hormone.")
    for h, lim in HORMONE_LIMITS.items():
        lo = lim["mean"] - 2*lim["sd"]
        hi = lim["mean"] + 2*lim["sd"]
        st.markdown(
            f"**{h}**  \n"
            f"`{lo:.3f} – {hi:.3f}`"
        )

# ═════════════════════════════════════════════════════════════════════════════
#  TABS
# ═════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📝  Enter SST Result", "📈  QC Charts", "📋  Data Table"])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 1 · Entry form
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Enter your SST result")
    st.caption("Complete all fields after running the SST on the instrument.")

    with st.form("sst_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        initials = col1.text_input(
            "Your Initials *",
            max_chars=5,
            placeholder="e.g. JD",
            help="Enter up to 5 characters"
        )
        email_input = col2.text_input(
            "Your Email *",
            placeholder="e.g. j.doe@lab.com",
            help="Used for QC failure alerts"
        )

        hormone = st.selectbox(
            "Hormone *",
            list(HORMONE_LIMITS.keys()),
            help="Select the hormone you are testing"
        )

        # Live limit preview
        lim   = HORMONE_LIMITS[hormone]
        lo    = lim["mean"] - 2*lim["sd"]
        hi    = lim["mean"] + 2*lim["sd"]
        st.markdown(f"""
        <div class="limit-card">
            <b>{hormone}</b> &nbsp;·&nbsp; Acceptance limits (±2SD)<br>
            Mean: <b>{lim['mean']}</b> &nbsp;|&nbsp;
            Lower limit: <b>{lo:.4f}</b> &nbsp;|&nbsp;
            Upper limit: <b>{hi:.4f}</b> &nbsp;|&nbsp;
        </div>
        """, unsafe_allow_html=True)

        sst_value = st.number_input(
            f"SST Value *",
            min_value=0.0,
            step=0.001,
            format="%.4f",
            help="Enter the result read from the instrument"
        )

        submitted = st.form_submit_button(
            "✅  Submit SST Result",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        # Validation
        if not initials.strip():
            st.error("Please enter your initials.")
        elif not email_input.strip() or "@" not in email_input:
            st.error("Please enter a valid email address.")
        elif sst_value <= 0.0:
            st.error("Please enter a valid SST value greater than 0.")
        else:
            status, mean_v, sd_v, upper, lower = check_limits(hormone, sst_value)
            save_entry(hormone, initials.strip(), email_input.strip(), sst_value, status)

            if status == "PASS":
                st.markdown(f"""
                <div class="pass-box">
                    ✅  PASS &nbsp;—&nbsp; {hormone} &nbsp;|&nbsp;
                    Value: {sst_value} &nbsp;|&nbsp;
                    Within ±2SD ({lower:.4f} – {upper:.4f})
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"""
                <div class="fail-box">
                    ❌  FAIL &nbsp;—&nbsp; {hormone} &nbsp;|&nbsp;
                    Value: {sst_value} &nbsp;|&nbsp;
                    Outside ±2SD ({lower:.4f} – {upper:.4f})
                </div>
                """, unsafe_allow_html=True)

                if email_enabled:
                    result = send_email_alert(
                        email_input.strip(), initials.strip().upper(),
                        hormone, sst_value, upper, lower,
                        smtp_server, smtp_port, sender_email, sender_pass
                    )
                    if result is True:
                        st.info(f"📧 Alert email sent to **{email_input}**")
                    else:
                        st.warning(f"📧 Email could not be sent: {result}")
                else:
                    st.warning("📧 Email alerts are disabled. Configure SMTP in the sidebar.")

            # Entry summary
            st.markdown("---")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Initials",  initials.upper())
            c2.metric("Hormone",   hormone)
            c3.metric("Value",     f"{sst_value}")
            c4.metric("Status",    status)
            c5.metric("Time",      datetime.now().strftime("%H:%M"))

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 2 · Charts
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Levey-Jennings QC Charts")

    df_all = load_data()

    if df_all.empty:
        st.info("No data yet. Enter SST results in the **Enter SST Result** tab to begin.")
    else:
        col_sel, col_info = st.columns([2, 1])
        sel_hormone = col_sel.selectbox(
            "Select hormone",
            list(HORMONE_LIMITS.keys()),
            key="chart_sel"
        )
        df_h = df_all[df_all["hormone"] == sel_hormone].reset_index(drop=True)

        if df_h.empty:
            st.info(f"No data recorded yet for **{sel_hormone}**.")
        else:
            total  = len(df_h)
            passes = int((df_h["status"] == "PASS").sum())
            fails  = int((df_h["status"] == "FAIL").sum())
            rate   = f"{passes/total*100:.1f}%"

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Runs",  total)
            c2.metric("✅ Pass",     passes)
            c3.metric("❌ Fail",     fails)
            c4.metric("Pass Rate",   rate)

            st.plotly_chart(plot_lj_chart(sel_hormone, df_h), use_container_width=True)

            # Mini table under chart
            with st.expander("Show data points for this hormone"):
                display = df_h[["initials","datetime","sst_value","status"]].copy()
                display.columns = ["Initials","Date & Time","SST Value","Status"]
                display["Date & Time"] = display["Date & Time"].dt.strftime("%Y-%m-%d %H:%M")
                st.dataframe(display, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 3 · Data table
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### Full QC Data Table")

    df_all = load_data()

    if df_all.empty:
        st.info("No data yet. Enter SST results in the **Enter SST Result** tab to begin.")
    else:
        col_f1, col_f2 = st.columns([2, 1])
        filter_h = col_f1.selectbox(
            "Filter by hormone",
            ["All hormones"] + list(HORMONE_LIMITS.keys()),
            key="table_filter"
        )
        filter_s = col_f2.selectbox(
            "Filter by status",
            ["All", "PASS", "FAIL"],
            key="status_filter"
        )

        df_view = df_all.copy()
        if filter_h != "All hormones":
            df_view = df_view[df_view["hormone"] == filter_h]
        if filter_s != "All":
            df_view = df_view[df_view["status"] == filter_s]

        df_view = df_view.sort_values("datetime", ascending=False).reset_index(drop=True)

        # Rename for display
        df_disp = df_view[["initials","datetime","hormone","sst_value","status","email"]].copy()
        df_disp.columns = ["Initials","Date & Time","Hormone","SST Value","Status","Email"]
        df_disp["Date & Time"] = pd.to_datetime(df_disp["Date & Time"]).dt.strftime("%Y-%m-%d %H:%M")

        def style_status(val):
            if val == "PASS":
                return "background-color: #d4edda; color: #155724; font-weight: 600"
            elif val == "FAIL":
                return "background-color: #f8d7da; color: #721c24; font-weight: 600"
            return ""

        st.dataframe(
            df_disp.style.map(style_status, subset=["Status"]),
            use_container_width=True,
            height=450,
            hide_index=True
        )

        st.caption(f"Showing **{len(df_disp)}** of **{len(df_all)}** total records.")

        csv_bytes = df_disp.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Download filtered data as CSV",
            data=csv_bytes,
            file_name=f"qc_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
