import streamlit as st
from medtrust_engine import validate_video_url, run_pipeline


def render_header():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0f172a, #1e3a8a);
            color: white;
            padding: 30px 34px;
            border-radius: 22px;
            margin-bottom: 22px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.16);
        ">
            <h1 style="font-size: 2.4rem; margin-bottom: 10px;">🩺 MedTrust AI</h1>
            <p style="font-size: 1rem; line-height: 1.6; margin: 0;">
                <b>Health Misinformation & Influencer Credibility Analyzer</b><br>
                Analyze public health-related video content for misinformation risk, evidence gaps,
                manipulation signals, missing medical context, and safer user guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_risk_style(risk):
    if risk == "Low Risk":
        return "#dcfce7", "#166534"
    if risk == "Medium Risk":
        return "#fef3c7", "#92400e"
    return "#fee2e2", "#991b1b"


def show_score_summary(result):
    score = int(result["misinformation_risk_score"])
    risk = result["risk_level"]
    evidence_match = result["evidence_match_level"]
    bg, color = get_risk_style(risk)

    st.markdown("## ✅ Analysis Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background:white;
                border:1px solid #e5e7eb;
                border-radius:16px;
                padding:25px;
                text-align:center;
                min-height:145px;
                box-shadow:0 8px 20px rgba(15,23,42,0.07);
            ">
                <div style="color:#6b7280;font-size:0.95rem;">Misinformation Risk Score</div>
                <div style="font-size:2rem;font-weight:800;margin-top:12px;">{score}/100</div>
                <div style="color:#4b5563;font-size:0.9rem;margin-top:8px;">
                    {result["score_interpretation"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background:white;
                border:1px solid #e5e7eb;
                border-radius:16px;
                padding:25px;
                text-align:center;
                min-height:145px;
                box-shadow:0 8px 20px rgba(15,23,42,0.07);
            ">
                <div style="color:#6b7280;font-size:0.95rem;">Risk Level</div>
                <div style="font-size:1.7rem;font-weight:800;margin-top:12px;">{risk}</div>
                <div style="
                    display:inline-block;
                    margin-top:10px;
                    padding:7px 15px;
                    border-radius:999px;
                    background:{bg};
                    color:{color};
                    font-weight:700;
                ">
                    {risk}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                background:white;
                border:1px solid #e5e7eb;
                border-radius:16px;
                padding:25px;
                text-align:center;
                min-height:145px;
                box-shadow:0 8px 20px rgba(15,23,42,0.07);
            ">
                <div style="color:#6b7280;font-size:0.95rem;">Evidence Match</div>
                <div style="font-size:1.7rem;font-weight:800;margin-top:12px;">{evidence_match}</div>
                <div style="color:#4b5563;font-size:0.9rem;margin-top:8px;">
                    Compared with trusted sources
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Get More Information", use_container_width=True):
        st.session_state.page = "page2"
        st.rerun()


def show_page1(reset_app):
    render_header()

    with st.container(border=True):
        st.subheader("🔗 Analyze Public Health Video URL")

        col_url, col_button = st.columns([5, 1])

        with col_url:
            video_url = st.text_input(
                "Video URL",
                placeholder="Paste any public health-related video URL here...",
                label_visibility="collapsed",
                value=st.session_state.current_url
            )

        with col_button:
            analyze_clicked = st.button("Analyze", use_container_width=True)

    st.info(
        "How it works: MedTrust AI attempts to fetch public video media, transcribe spoken content, "
        "extract health claims, search trusted medical sources, and generate a Misinformation Risk Score."
    )

    st.warning(
        "Important: This is an AI-assisted risk analysis tool, not medical advice. "
        "URL fetching works only for public content supported by the downloader. "
        "Private, login-restricted, or blocked videos may fail."
    )

    if analyze_clicked:
        is_valid, message = validate_video_url(video_url)

        if not is_valid:
            st.warning(message)
        else:
            st.session_state.current_url = video_url

            # Clear any previous result immediately so a new analysis never
            # shows stale data from an earlier URL while this one is running
            # or if this one fails.
            st.session_state.current_result = None

            with st.spinner(
                "Fetching video, transcribing audio, searching medical evidence, and calculating risk score..."
            ):
                result = run_pipeline(video_url)

            if "error" in result:
                # Keep current_result cleared (set above) so no old score
                # card lingers underneath the new error message.
                st.error(result["error"])
                st.info(
                    "If URL-only fetching fails, the video may be private, login-restricted, blocked, or unsupported."
                )
            else:
                st.session_state.current_result = result
                st.rerun()

    if st.session_state.current_result is not None:
        show_score_summary(st.session_state.current_result)
