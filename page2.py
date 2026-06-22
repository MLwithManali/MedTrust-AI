import time
import streamlit as st


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
                <b>Full Detailed Report</b><br>
                Evidence, extracted transcript, red flags, missing context, and safer user guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def reset_to_page1():
    st.session_state.page = "page1"
    st.session_state.current_result = None
    st.session_state.current_url = ""


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
            if st.session_state.current_result is not None:
                st.session_state.analysis_history.append(
                    {
                        "url": st.session_state.current_url,
                        "risk": st.session_state.current_result["risk_level"],
                        "score": st.session_state.current_result["misinformation_risk_score"],
                        "feedback": feedback,
                        "comment": comment,
                    }
                )

            st.success("Thank you! Feedback submitted.")
            time.sleep(1)
            reset_to_page1()
            st.rerun()

    with col_skip:
        if st.button("Skip", use_container_width=True):
            reset_to_page1()
            st.rerun()


def show_page2(reset_app):
    result = st.session_state.current_result
    url = st.session_state.current_url

    render_header()

    if st.button("← Back to Page 1 Summary", use_container_width=True):
        st.session_state.page = "page1"
        st.rerun()

    st.markdown("## 📄 Full Detailed Report")

    with st.container(border=True):
        st.subheader("🧠 Main Health Claim")
        st.write(result["main_health_claim"])

        st.subheader("📌 Evidence Summary")
        st.write(result["evidence_summary"])

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.subheader("📝 Extracted Video Content")

            st.markdown("**Video URL**")
            st.write(url)

            st.markdown("**Title / Source / Creator**")
            st.write(f"Title: {result['video_title'] or 'Not available'}")
            st.write(f"Source: {result['platform_or_source'] or 'Not available'}")
            st.write(f"Creator: {result['creator_or_channel'] or 'Not available'}")

            st.markdown("**Fetched Caption / Description**")
            st.write(result["fetched_caption"] if result["fetched_caption"] else "No caption fetched.")

            st.markdown("**Video / Audio Transcript**")
            st.write(result["video_transcript"] if result["video_transcript"] else "No transcript extracted.")

    with right:
        with st.container(border=True):
            st.subheader("⚠️ Risk & Context")

            st.markdown("**Extracted Health Claims**")
            if result["extracted_health_claims"]:
                for claim in result["extracted_health_claims"]:
                    st.write(f"• {claim}")
            else:
                st.write("No separate claims listed.")

            st.markdown("**Red Flags**")
            if result["red_flags"]:
                for flag in result["red_flags"]:
                    st.write(f"⚠️ {flag}")
            else:
                st.write("No major manipulation red flags detected.")

            st.markdown("**Missing Medical Context**")
            if result["missing_medical_context"]:
                for item in result["missing_medical_context"]:
                    st.write(f"🔍 {item}")
            else:
                st.write("No major missing context detected.")

            st.markdown("**Influencer Credibility Signals**")
            if result["influencer_credibility_signals"]:
                for item in result["influencer_credibility_signals"]:
                    st.write(f"👤 {item}")
            else:
                st.write("No clear influencer credibility signals detected.")

    with st.container(border=True):
        st.subheader("🔗 Evidence Sources Used")
        if result["evidence_sources_used"]:
            for source in result["evidence_sources_used"]:
                st.write(f"🔗 {source}")
        else:
            st.write("No strong source links returned.")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.subheader("❓ Why It May Be Misleading")
            st.write(result["why_it_may_be_misleading"])

        with st.container(border=True):
            st.subheader("✅ Safer Explanation")
            st.write(result["safer_explanation"])

    with col_b:
        with st.container(border=True):
            st.subheader("📍 Recommended User Action")
            st.write(result["recommended_user_action"])

        with st.container(border=True):
            st.subheader("⚖️ Disclaimer")
            st.write(result["disclaimer"])

    st.divider()

    if st.button("Finish", use_container_width=True):
        feedback_popup()
