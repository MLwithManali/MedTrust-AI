import time
import streamlit as st


def render_header():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">🩺 MedTrust AI</div>
            <div class="hero-subtitle">Full health evidence report</div>
            <div class="hero-text">
                Review the detected claim, risk score, trusted evidence, red flags,
                missing medical context, and safer user guidance.
            </div>
            <br>
            <span class="pill pill-blue">Evidence report</span>
            <span class="pill pill-green">Trusted sources</span>
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


def format_latency(seconds):
    try:
        seconds = float(seconds)
        if seconds >= 60:
            return f"{int(seconds // 60)} min {int(seconds % 60)} sec"
        return f"{seconds:.1f} sec"
    except Exception:
        return "N/A"


def show_list(items, empty_message, icon="•"):
    if isinstance(items, list) and len(items) > 0:
        for item in items:
            st.write(f"{icon} {item}")
    else:
        st.write(empty_message)


def reset_to_page1():
    st.session_state.page = "page1"
    st.session_state.current_result = None
    st.session_state.current_url = ""


def save_feedback(feedback, comment):
    if st.session_state.current_result is None:
        return

    st.session_state.analysis_history.append(
        {
            "url": st.session_state.current_url,
            "risk": st.session_state.current_result.get("risk_level", ""),
            "score": st.session_state.current_result.get("misinformation_risk_score", ""),
            "evidence_match": st.session_state.current_result.get("evidence_match_level", ""),
            "latency_seconds": st.session_state.current_result.get("latency_seconds", ""),
            "feedback": feedback,
            "comment": comment,
        }
    )


@st.dialog("Feedback")
def feedback_popup():
    st.write("Please share your feedback before starting a new analysis.")

    feedback = st.radio(
        "Was this analysis useful?",
        ["👍 Useful", "👎 Not useful"],
        horizontal=True
    )

    comment = st.text_area(
        "Optional comment",
        placeholder="Example: The score and evidence summary were helpful."
    )

    col_submit, col_skip = st.columns(2)

    with col_submit:
        if st.button("Submit Feedback", use_container_width=True):
            save_feedback(feedback, comment)
            st.success("Thank you! Feedback submitted.")
            time.sleep(1)
            reset_to_page1()
            st.rerun()

    with col_skip:
        if st.button("Skip", use_container_width=True):
            reset_to_page1()
            st.rerun()


def show_navigation_buttons(reset_app):
    col_back, col_new = st.columns(2)

    with col_back:
        if st.button("← Back to Summary", use_container_width=True):
            st.session_state.page = "page1"
            st.rerun()

    with col_new:
        if st.button("Start New Analysis", use_container_width=True):
            reset_app()
            st.rerun()


def get_risk_badge(risk_level):
    if risk_level == "Low Risk":
        return "🟢 Reliable", "pill-green"

    if risk_level == "Medium Risk":
        return "🟡 Needs Review", "pill-yellow"

    return "🔴 High Risk", "pill-red"


def show_report_overview(result):
    score = safe_get(result, "misinformation_risk_score", 50)
    risk_level = safe_get(result, "risk_level", "Medium Risk")
    evidence = safe_get(result, "evidence_match_level", "Partial / unclear")
    risk_label, risk_class = get_risk_badge(risk_level)

    st.markdown('<div class="section-title">📄 Full Detailed Report</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">MedTrust Score</div>
                <div class="metric-value">{score}/100</div>
                <div class="metric-subtitle">Higher score = lower misinformation risk</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value">{risk_label}</div>
                <br>
                <span class="pill {risk_class}">{risk_level}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Evidence Confidence</div>
                <div class="metric-value">{evidence}</div>
                <div class="metric-subtitle">Compared with trusted sources</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Processing Time</div>
                <div class="metric-value">{format_latency(result.get("latency_seconds", "N/A"))}</div>
                <div class="metric-subtitle">Status: completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def show_main_claim_and_evidence(result):
    with st.container(border=True):
        st.subheader("🧠 AI Detected Claim")
        st.write(
            safe_get(
                result,
                "main_health_claim",
                "No clear health claim identified."
            )
        )

        st.subheader("📌 Evidence Summary")
        st.write(
            safe_get(
                result,
                "evidence_summary",
                "Evidence summary not available."
            )
        )


def show_risk_and_context(result):
    with st.container(border=True):
        st.subheader("⚠️ Risk & Context")

        st.markdown("**Extracted Health Claims**")
        show_list(
            result.get("extracted_health_claims", []),
            "No separate claims listed.",
            "•"
        )

        st.markdown("**Red Flags**")
        show_list(
            result.get("red_flags", []),
            "No major manipulation red flags detected.",
            "⚠️"
        )

        st.markdown("**Missing Medical Context**")
        show_list(
            result.get("missing_medical_context", []),
            "No major missing context detected.",
            "🔍"
        )

        st.markdown("**Creator Credibility**")
        show_list(
            result.get("influencer_credibility_signals", []),
            "No clear creator credibility signals detected.",
            "👤"
        )


def show_extracted_content(result, url):
    with st.container(border=True):
        st.subheader("🎥 Source Content")

        st.markdown("**Video URL**")
        st.write(url)

        st.markdown("**Title / Source / Creator**")
        st.write(f"Title: {safe_get(result, 'video_title')}")
        st.write(f"Source: {safe_get(result, 'platform_or_source')}")
        st.write(f"Creator: {safe_get(result, 'creator_or_channel')}")

        with st.expander("View Caption / Description"):
            st.write(
                safe_get(
                    result,
                    "fetched_caption",
                    "No caption fetched."
                )
            )

        with st.expander("View Transcript"):
            st.write(
                safe_get(
                    result,
                    "video_transcript",
                    "No transcript extracted."
                )
            )


def show_evidence_sources(result):
    with st.container(border=True):
        st.subheader("🏥 Trusted Evidence Sources")

        sources = result.get("evidence_sources_used", [])

        if not sources:
            st.write("No strong source links returned.")
            return

        for source in sources:
            if isinstance(source, dict):
                title = source.get("title", "Evidence source")
                url = source.get("url", "")

                if url:
                    st.markdown(f"- 🏥 [{title}]({url})")
                else:
                    st.write(f"🏥 {title}")

            else:
                source_text = str(source)

                if source_text.startswith("http"):
                    st.markdown(f"- 🏥 [Evidence Source]({source_text})")
                else:
                    st.write(f"🏥 {source_text}")


def show_explanation_and_action(result):
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.subheader("🔍 Analysis")
            st.write(
                safe_get(
                    result,
                    "why_it_may_be_misleading",
                    "More context is needed to evaluate this claim properly."
                )
            )

        with st.container(border=True):
            st.subheader("✅ Safer Explanation")
            st.write(
                safe_get(
                    result,
                    "safer_explanation",
                    "Treat this as general information and verify it with credible medical sources."
                )
            )

    with col_b:
        with st.container(border=True):
            st.subheader("📍 Recommended Next Step")
            st.write(
                safe_get(
                    result,
                    "recommended_user_action",
                    "Consult a qualified healthcare professional for personalized medical guidance."
                )
            )

        with st.container(border=True):
            st.subheader("⚖️ Medical Disclaimer")
            st.write(
                safe_get(
                    result,
                    "disclaimer",
                    "This analysis is for educational purposes only and is not medical advice."
                )
            )


def show_safety_status(result):
    prompt_flag = bool(result.get("prompt_injection_detected", False))

    with st.container(border=True):
        st.subheader("🛡️ Safety Checks")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("URL validated")

        with col2:
            st.success("Trusted sources checked")

        with col3:
            if prompt_flag:
                st.warning("Security review needed")
            else:
                st.success("Prompt-injection check passed")


def show_page2(reset_app):
    result = st.session_state.current_result
    url = st.session_state.current_url

    if result is None:
        st.warning("No analysis result found. Please run an analysis first.")

        if st.button("Go to Summary Page", use_container_width=True):
            reset_app()
            st.rerun()

        return

    render_header()
    show_navigation_buttons(reset_app)

    show_report_overview(result)
    show_main_claim_and_evidence(result)

    left, right = st.columns(2)

    with left:
        show_risk_and_context(result)

    with right:
        show_extracted_content(result, url)

    show_evidence_sources(result)
    show_explanation_and_action(result)
    show_safety_status(result)

    st.divider()

    if st.button("Complete Analysis", use_container_width=True):
        feedback_popup()