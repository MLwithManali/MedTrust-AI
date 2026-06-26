import streamlit as st

from medtrust_engine import validate_video_url, cached_run_pipeline


def render_header():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">🩺 MedTrust AI</div>
            <div class="hero-subtitle">Verify health information before you trust it.</div>
            <div class="hero-text">
                Analyze public health-related videos for misinformation risk, evidence confidence,
                manipulation signals, missing medical context, and safer user guidance.
            </div>
            <br>
            <span class="pill pill-blue">AI-assisted health claim analysis</span>
            <span class="pill pill-green">Trusted medical sources</span>
            <span class="pill pill-yellow">Educational use only</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_get(result, key, default="Not available"):
    value = result.get(key, default)

    if value in [None, ""]:
        return default

    return value


def get_risk_badge(risk):
    if risk == "Low Risk":
        return "Reliable", "pill-green"

    if risk == "Medium Risk":
        return "Needs Review", "pill-yellow"

    return "High Risk", "pill-red"


def reset_current_analysis():
    st.session_state.current_result = None
    st.session_state.current_url = ""


def show_metric_card(title, value, subtitle=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_risk_card(risk):
    label, pill_class = get_risk_badge(risk)

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Risk Level</div>
            <div class="metric-value">{label}</div>
            <br>
            <span class="pill {pill_class}">{risk}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_url_input():
    with st.container(border=True):
        st.markdown("### 🔍 Analyze Health Content")

        col_url, col_button = st.columns([5, 1])

        with col_url:
            video_url = st.text_input(
                "Video URL",
                placeholder="Paste a public health-related video URL here...",
                label_visibility="collapsed",
                value=st.session_state.current_url
            )

        with col_button:
            analyze_clicked = st.button("Analyze", use_container_width=True)

    return video_url, analyze_clicked


def show_information_boxes():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("🧠 Extracts health claims from public video content.")

    with col2:
        st.info("🏥 Compares claims with trusted medical sources.")

    with col3:
        st.info("🛡️ Adds safety checks and medical disclaimers.")

    with st.expander("How MedTrust AI works"):
        st.write(
            "MedTrust AI attempts to fetch public video content, transcribe spoken audio, "
            "extract health claims, search trusted medical sources, compare evidence, "
            "and generate a misinformation risk score."
        )

    st.warning(
        "This tool is for educational purposes only and is not medical advice. "
        "Private, login-restricted, region-blocked, or unsupported videos may fail."
    )


def show_score_summary(result):
    score = int(result.get("misinformation_risk_score", 50))
    risk = result.get("risk_level", "Medium Risk")
    evidence_match = result.get("evidence_match_level", "Partial / unclear")
    interpretation = result.get("score_interpretation", "Needs caution / missing context")

    st.markdown('<div class="section-title">✅ Analysis Summary</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric_card(
            title="MedTrust Score",
            value=f"{score}/100",
            subtitle="Higher score means lower misinformation risk"
        )

    with col2:
        show_risk_card(risk)

    with col3:
        show_metric_card(
            title="Evidence Confidence",
            value=evidence_match,
            subtitle="Compared with trusted sources"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("🧠 AI Detected Claim")
        st.write(safe_get(result, "main_health_claim", "No clear health claim found."))

        st.subheader("📌 Evidence Summary")
        st.write(safe_get(result, "evidence_summary", "Evidence summary not available."))

    col_more, col_reset = st.columns(2)

    with col_more:
        if st.button("View Detailed Report", use_container_width=True):
            st.session_state.page = "page2"
            st.rerun()

    with col_reset:
        if st.button("Start New Analysis", use_container_width=True):
            reset_current_analysis()
            st.rerun()


def handle_analysis(video_url):
    is_valid, message = validate_video_url(video_url)

    if not is_valid:
        st.warning(message)
        return

    st.session_state.current_url = video_url
    st.session_state.current_result = None

    progress = st.progress(0)
    status = st.empty()

    status.write("🔍 Validating URL...")
    progress.progress(15)

    status.write("🎥 Fetching public video content...")
    progress.progress(30)

    status.write("🎙️ Transcribing audio...")
    progress.progress(50)

    status.write("🏥 Searching trusted medical evidence...")
    progress.progress(70)

    status.write("🧠 Generating health risk report...")
    progress.progress(90)

    result = cached_run_pipeline(video_url)

    progress.progress(100)
    status.empty()

    if "error" in result:
        st.error(result["error"])
        st.info(
            "If URL fetching fails, the video may be private, login-restricted, "
            "region-blocked, blocked, or unsupported by the downloader."
        )
        return

    st.session_state.current_result = result
    st.success("Analysis completed successfully.")
    st.rerun()


def show_page1(reset_app):
    render_header()

    video_url, analyze_clicked = show_url_input()
    show_information_boxes()

    if analyze_clicked:
        handle_analysis(video_url)

    if st.session_state.current_result is not None:
        show_score_summary(st.session_state.current_result)