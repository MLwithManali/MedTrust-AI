import streamlit as st

from page1 import show_page1
from page2 import show_page2


# ==================================================
# APP CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="MedTrust AI",
    page_icon="🩺",
    layout="wide"
)


# ==================================================
# APP STYLING
# ==================================================
st.markdown(
    """
    <style>
        :root {
            --primary: #0f4c81;
            --primary-dark: #0f172a;
            --primary-soft: #eaf6f6;
            --success: #16a34a;
            --warning: #f59e0b;
            --danger: #dc2626;
            --text: #1f2937;
            --muted: #6b7280;
            --bg: #f6fbff;
            --card: #ffffff;
            --border: #dbeafe;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        .stApp {
            background: linear-gradient(
                180deg,
                #f6fbff 0%,
                #f8fafc 45%,
                #eefaf6 100%
            );
            color: var(--text);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1350px;
        }

        .main-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 28px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        }

        .hero-card {
            width: 100%;
            background: linear-gradient(135deg, #0f172a, #0f4c81);
            color: white;
            padding: 42px 46px;
            border-radius: 28px;
            margin-bottom: 28px;
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.18);
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 850;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .hero-text {
            font-size: 1.05rem;
            line-height: 1.7;
            opacity: 0.96;
            max-width: 1050px;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 30px 24px;
            text-align: center;
            min-height: 165px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.96rem;
            margin-bottom: 12px;
        }

        .metric-value {
            font-size: 2.25rem;
            font-weight: 850;
            color: #111827;
        }

        .metric-subtitle {
            color: #4b5563;
            font-size: 0.92rem;
            margin-top: 10px;
        }

        .pill {
            display: inline-block;
            padding: 7px 15px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.9rem;
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .pill-blue {
            background: #dbeafe;
            color: #1d4ed8;
        }

        .pill-green {
            background: #dcfce7;
            color: #166534;
        }

        .pill-yellow {
            background: #fef3c7;
            color: #92400e;
        }

        .pill-red {
            background: #fee2e2;
            color: #991b1b;
        }

        .section-title {
            font-size: 1.8rem;
            font-weight: 850;
            margin-top: 18px;
            margin-bottom: 18px;
        }

        .stButton > button {
            border-radius: 14px;
            font-weight: 750;
            min-height: 44px;
        }

        input {
            border-radius: 14px !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================
def initialize_session_state():
    default_values = {
        "page": "page1",
        "current_url": "",
        "current_result": None,
        "analysis_history": [],
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# ==================================================
# APP RESET
# ==================================================
def reset_app():
    st.session_state.page = "page1"
    st.session_state.current_url = ""
    st.session_state.current_result = None


# ==================================================
# PAGE ROUTING
# ==================================================
def route_pages():
    if st.session_state.page == "page1":
        show_page1(reset_app)

    elif st.session_state.page == "page2":
        show_page2(reset_app)

    else:
        reset_app()
        st.rerun()


route_pages()