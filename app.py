import streamlit as st

st.set_page_config(
    page_title="MedTrust AI",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 MedTrust AI")
st.subheader("Health Misinformation & Influencer Credibility Analyzer")

st.write(
    "MedTrust AI helps users analyze health-related social media content "
    "by identifying health claims, misinformation risks, manipulation patterns, "
    "missing medical context, and overall trust level."
)

post_text = st.text_area(
    "Paste a health-related social media post here:",
    height=200,
    placeholder="Example: This herbal drink cures diabetes in 7 days..."
)

if st.button("Analyze Post"):
    if post_text.strip() == "":
        st.warning("Please paste a health-related post first.")
    else:
        st.success("Initial prototype working successfully!")

        st.markdown("### Extracted Claim")
        st.write("The app will identify the main health claim from the post.")

        st.markdown("### Risk Level")
        st.write("The app will classify the content as Low, Medium, or High risk.")

        st.markdown("### Manipulation Signals")
        st.write("The app will detect red flags such as miracle cure claims, fear-based language, or exaggerated promises.")

        st.markdown("### Missing Medical Context")
        st.write("The app will highlight missing details such as dosage, side effects, medical evidence, or professional guidance.")

        st.markdown("### Trust Score")
        st.write("The app will generate a trust score with explanation.")

st.info("Disclaimer: MedTrust AI is not a medical diagnosis tool. It supports critical thinking and awareness.")
