import os
import json
import time
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import yt_dlp
import imageio_ffmpeg


# ==================================================
# API KEYS + MODELS
# ==================================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

TEXT_MODEL = "llama-3.1-8b-instant"
WHISPER_MODEL = "whisper-large-v3-turbo"

TRUSTED_DOMAINS = [
    "who.int",
    "cdc.gov",
    "nhs.uk",
    "mayoclinic.org",
    "pubmed.ncbi.nlm.nih.gov",
    "medlineplus.gov",
    "fda.gov",
    "nih.gov",
]


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="MedTrust AI",
    page_icon="🩺",
    layout="wide"
)


# ==================================================
# CSS
# ==================================================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1180px;
        }

        .hero {
            background: linear-gradient(135deg, #0f172a, #1e3a8a);
            color: white;
            padding: 28px 32px;
            border-radius: 22px;
            margin-bottom: 22px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.16);
        }

        .hero h1 {
            font-size: 2.2rem;
            margin-bottom: 10px;
            font-weight: 850;
        }

        .hero p {
            font-size: 1rem;
            line-height: 1.6;
            margin: 0;
            opacity: 0.95;
        }

        .note {
            background: #eef4ff;
            border-left: 6px solid #2563eb;
            padding: 14px 18px;
            border-radius: 14px;
            color: #1e3a8a;
            margin-bottom: 16px;
            font-size: 0.95rem;
        }

        .warning {
            background: #fff7ed;
            border-left: 6px solid #f97316;
            padding: 14px 18px;
            border-radius: 14px;
            color: #9a3412;
            margin-bottom: 18px;
            font-size: 0.95rem;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
            min-height: 135px;
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.94rem;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #111827;
            font-size: 2rem;
            font-weight: 850;
            margin-bottom: 4px;
        }

        .metric-sub {
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.4;
        }

        .pill {
            display: inline-block;
            padding: 7px 14px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.9rem;
            margin-top: 6px;
        }

        .pill-low {
            background: #dcfce7;
            color: #166534;
        }

        .pill-medium {
            background: #fef3c7;
            color: #92400e;
        }

        .pill-high {
            background: #fee2e2;
            color: #991b1b;
        }

        .small-muted {
            color: #6b7280;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HEADER
# ==================================================
st.markdown(
    """
    <div class="hero">
        <h1>🩺 MedTrust AI</h1>
        <p>
            <b>Health Misinformation & Influencer Credibility Analyzer</b><br>
            Analyze public health-related video content for misinformation risk, evidence gaps,
            manipulation signals, missing medical context, and safer user guidance.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# INPUT FIRST
# ==================================================
with st.container(border=True):
    st.subheader("🔗 Analyze Public Health Video URL")

    col_url, col_button = st.columns([5, 1])

    with col_url:
        video_url = st.text_input(
            "Video URL",
            placeholder="Paste any public video URL here...",
            label_visibility="collapsed"
        )

    with col_button:
        analyze_clicked = st.button("Analyze", use_container_width=True)

st.markdown(
    """
    <div class="note">
        <b>How it works:</b> MedTrust AI attempts to fetch public video media,
        transcribe spoken content, extract health claims, search trusted medical sources,
        and generate a Misinformation Risk Score.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="warning">
        <b>Important:</b> This is an AI-assisted risk analysis tool, not medical advice.
        URL fetching works only for public content supported by the downloader.
        Private, login-restricted, or blocked videos may fail.
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


# ==================================================
# HELPER FUNCTIONS
# ==================================================
def validate_video_url(url: str):
    url = url.strip()

    if not url:
        return False, "Please paste a video URL."

    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "Please enter a valid URL starting with http:// or https://."

    return True, "Valid URL format detected."


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


def safe_json_loads(text: str):
    cleaned_text = clean_json_response(text)
    return json.loads(cleaned_text)


def get_score_interpretation(score: int):
    if score >= 80:
        return "Low misinformation risk / more reliable"
    if score >= 50:
        return "Needs caution / missing context"
    return "High misinformation risk / unsupported or exaggerated"


def validate_final_result(result: dict) -> dict:
    defaults = {
        "content_type": "Health-related video content",
        "video_title": "",
        "platform_or_source": "",
        "creator_or_channel": "",
        "fetched_caption": "",
        "video_transcript": "",
        "combined_text_used": "",
        "extracted_health_claims": [],
        "main_health_claim": "Not clearly identified.",
        "evidence_summary": "",
        "evidence_sources_used": [],
        "risk_level": "Medium Risk",
        "misinformation_risk_score": 50,
        "score_interpretation": "Needs caution / missing context",
        "evidence_match_level": "Partial / unclear",
        "influencer_credibility_signals": [],
        "red_flags": [],
        "missing_medical_context": [],
        "why_it_may_be_misleading": "More context is needed to evaluate this claim properly.",
        "safer_explanation": "Treat this as general information and verify it with credible medical sources.",
        "recommended_user_action": "Consult a qualified healthcare professional for personal medical concerns.",
        "disclaimer": (
            "This analysis is for educational purposes only and is not medical advice. "
            "The score is an AI-assisted misinformation risk estimate, not a medically verified accuracy score."
        ),
    }

    for key, value in defaults.items():
        if key not in result or result[key] in [None, ""]:
            result[key] = value

    try:
        result["misinformation_risk_score"] = int(result["misinformation_risk_score"])
    except Exception:
        result["misinformation_risk_score"] = 50

    result["misinformation_risk_score"] = max(0, min(100, result["misinformation_risk_score"]))

    list_fields = [
        "extracted_health_claims",
        "evidence_sources_used",
        "influencer_credibility_signals",
        "red_flags",
        "missing_medical_context",
    ]

    for field in list_fields:
        if not isinstance(result[field], list):
            result[field] = [str(result[field])]

    result["score_interpretation"] = get_score_interpretation(
        result["misinformation_risk_score"]
    )

    return result


# ==================================================
# STEP 1: FETCH PUBLIC VIDEO/CAPTION
# ==================================================
def fetch_public_video_media(url: str):
    temp_dir = tempfile.mkdtemp()
    output_template = str(Path(temp_dir) / "video_media.%(ext)s")

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    ydl_opts = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        caption = (
            info.get("description")
            or info.get("title")
            or info.get("caption")
            or ""
        )

        uploader = info.get("uploader", "") or info.get("channel", "")
        title = info.get("title", "")
        webpage_url = info.get("webpage_url", url)
        extractor = info.get("extractor", "")

        media_path = None

        for file in Path(temp_dir).glob("video_media.*"):
            if file.suffix.lower() in [".mp4", ".m4a", ".mp3", ".webm", ".mov"]:
                media_path = str(file)
                break

        if media_path is None:
            return {
                "error": (
                    "Media could not be downloaded from this URL. "
                    "The content may be private, restricted, unsupported, or blocked."
                )
            }

        return {
            "media_path": media_path,
            "caption": caption,
            "uploader": uploader,
            "title": title,
            "webpage_url": webpage_url,
            "platform_or_source": extractor,
        }

    except Exception as e:
        return {
            "error": (
                "Could not fetch media/caption from this URL. "
                "This can happen if the content is private, login-restricted, region-blocked, unsupported, or blocked. "
                f"Details: {str(e)}"
            )
        }


# ==================================================
# STEP 2: TRANSCRIBE AUDIO/VIDEO
# ==================================================
def transcribe_media_file(media_path: str):
    if not GROQ_API_KEY:
        return {
            "error": "Groq API key not found. Please add GROQ_API_KEY in your .env file."
        }

    client = Groq(api_key=GROQ_API_KEY)

    try:
        with open(media_path, "rb") as media_file:
            transcription = client.audio.transcriptions.create(
                file=(Path(media_path).name, media_file.read()),
                model=WHISPER_MODEL,
                response_format="json",
                temperature=0,
            )

        return {
            "transcript": transcription.text
        }

    except Exception as e:
        return {
            "error": f"Audio transcription failed: {str(e)}"
        }


# ==================================================
# STEP 3: EXTRACT HEALTH CLAIMS
# ==================================================
def extract_health_claims(combined_text: str):
    if not GROQ_API_KEY:
        return {
            "error": "Groq API key not found."
        }

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are MedTrust AI.

Extract health-related claims from this video content.

Content:
{combined_text}

Tasks:
- Identify all health, medical, wellness, nutrition, mental health, weight loss, diagnosis, treatment, or supplement-related claims.
- Choose the main claim.
- If there is no clear health claim, say so.

Return only valid JSON:

{{
  "extracted_health_claims": [],
  "main_health_claim": "",
  "needs_more_context": true
}}
"""

    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON. No markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.1,
                max_tokens=700,
            )

            result_text = response.choices[0].message.content
            return safe_json_loads(result_text)

        except Exception as e:
            if attempt < max_retries:
                time.sleep(1)
                continue

            return {
                "error": f"Health claim extraction failed: {str(e)}"
            }


# ==================================================
# STEP 4: SEARCH TRUSTED MEDICAL SOURCES
# ==================================================
@st.cache_data(show_spinner=False)
def search_trusted_sources(main_claim: str):
    if not TAVILY_API_KEY:
        return {
            "error": "Tavily API key not found. Please add TAVILY_API_KEY in your .env file."
        }

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    query = (
        f"{main_claim} medical evidence "
        f"WHO CDC NHS Mayo Clinic PubMed MedlinePlus FDA NIH"
    )

    try:
        search_result = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=8,
            include_answer=True,
            include_raw_content=False,
            topic="general",
        )

        results = search_result.get("results", [])
        trusted_results = []

        for item in results:
            url = item.get("url", "")
            if any(domain in url for domain in TRUSTED_DOMAINS):
                trusted_results.append(
                    {
                        "title": item.get("title", "Untitled source"),
                        "url": url,
                        "content": item.get("content", ""),
                    }
                )

        if not trusted_results:
            for item in results[:5]:
                trusted_results.append(
                    {
                        "title": item.get("title", "Untitled source"),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                    }
                )

        return {
            "query": query,
            "answer": search_result.get("answer", ""),
            "results": trusted_results[:8],
        }

    except Exception as e:
        return {
            "error": f"Tavily search failed: {str(e)}"
        }


# ==================================================
# STEP 5: COMPARE CLAIM WITH EVIDENCE
# ==================================================
def compare_claim_with_evidence(
    url: str,
    title: str,
    platform_or_source: str,
    creator: str,
    caption: str,
    transcript: str,
    combined_text: str,
    claims_data: dict,
    evidence_data: dict,
):
    if not GROQ_API_KEY:
        return {
            "error": "Groq API key not found."
        }

    client = Groq(api_key=GROQ_API_KEY)

    evidence_text = ""

    for idx, source in enumerate(evidence_data.get("results", []), start=1):
        evidence_text += f"""
Source {idx}
Title: {source.get("title")}
URL: {source.get("url")}
Content: {source.get("content")}
"""

    prompt = f"""
You are MedTrust AI, a health misinformation and evidence comparison assistant.

You are given:
1. Public video URL
2. Video title/source/creator information
3. Fetched caption/description
4. Video/audio transcript
5. Combined text
6. Extracted health claims
7. Trusted-source search evidence

Your task:
- Compare the main health claim with the evidence.
- Generate a Misinformation Risk Score.
- Explain red flags and missing medical context.
- Do not give diagnosis or treatment advice.
- Do not claim final medical truth.
- Be honest if evidence is incomplete.

Scoring:
80-100 = Low misinformation risk / more reliable
50-79 = Needs caution / missing context
0-49 = High misinformation risk / unsupported or exaggerated

Risk level mapping:
80-100 = Low Risk
50-79 = Medium Risk
0-49 = High Risk

Important scoring rules:
- If evidence supports the claim but the video oversimplifies it, use 50-79.
- If the claim encourages self-diagnosis, use 50-79 unless clearly harmful.
- If the claim promotes miracle cure, rapid cure, rapid weight loss, fear-based marketing, or unsupported treatment, use 0-49.
- If the claim is awareness-based and low harm but missing citations, use 60-79.
- If evidence strongly supports the claim and there is low harm, use 80-100.

Video URL:
{url}

Platform/source:
{platform_or_source}

Creator/channel:
{creator}

Video title:
{title}

Fetched caption/description:
{caption}

Video/audio transcript:
{transcript}

Combined text:
{combined_text}

Extracted claims:
{json.dumps(claims_data, indent=2)}

Trusted-source evidence:
{evidence_text}

Return only valid JSON in this exact format:

{{
  "content_type": "Health-related video content",
  "video_title": "",
  "platform_or_source": "",
  "creator_or_channel": "",
  "fetched_caption": "",
  "video_transcript": "",
  "combined_text_used": "",
  "extracted_health_claims": [],
  "main_health_claim": "",
  "evidence_summary": "",
  "evidence_sources_used": [],
  "risk_level": "Low Risk / Medium Risk / High Risk",
  "misinformation_risk_score": 0,
  "score_interpretation": "",
  "evidence_match_level": "Strong / Partial / Weak / Not enough evidence",
  "influencer_credibility_signals": [],
  "red_flags": [],
  "missing_medical_context": [],
  "why_it_may_be_misleading": "",
  "safer_explanation": "",
  "recommended_user_action": "",
  "disclaimer": "This analysis is for educational purposes only and is not medical advice. The score is an AI-assisted misinformation risk estimate, not a medically verified accuracy score."
}}
"""

    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are MedTrust AI. Return only valid JSON. No markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.2,
                max_tokens=1600,
            )

            result_text = response.choices[0].message.content
            result = safe_json_loads(result_text)
            result = validate_final_result(result)

            result["video_title"] = title
            result["platform_or_source"] = platform_or_source
            result["creator_or_channel"] = creator
            result["fetched_caption"] = caption
            result["video_transcript"] = transcript
            result["combined_text_used"] = combined_text
            result["extracted_health_claims"] = claims_data.get("extracted_health_claims", [])
            result["main_health_claim"] = claims_data.get(
                "main_health_claim",
                result["main_health_claim"]
            )

            return result

        except Exception as e:
            if attempt < max_retries:
                time.sleep(1)
                continue

            return {
                "error": f"Evidence comparison failed: {str(e)}"
            }


# ==================================================
# FULL PIPELINE
# ==================================================
def run_pipeline(url: str):
    fetch_result = fetch_public_video_media(url)

    if "error" in fetch_result:
        return fetch_result

    media_path = fetch_result["media_path"]
    caption = fetch_result.get("caption", "")
    creator = fetch_result.get("uploader", "")
    title = fetch_result.get("title", "")
    platform_or_source = fetch_result.get("platform_or_source", "")

    transcription_result = transcribe_media_file(media_path)

    if "error" in transcription_result:
        return transcription_result

    transcript = transcription_result.get("transcript", "")

    combined_text = f"""
Video URL:
{url}

Platform/source:
{platform_or_source}

Creator/channel:
{creator}

Video title:
{title}

Fetched caption/description:
{caption}

Video/audio transcript:
{transcript}
""".strip()

    if len(combined_text.strip()) < 40:
        return {
            "error": "Not enough text was extracted from the video URL."
        }

    claims_data = extract_health_claims(combined_text)

    if "error" in claims_data:
        return claims_data

    main_claim = claims_data.get("main_health_claim", "")

    if not main_claim or main_claim.lower() in [
        "no clear health claim identified.",
        "not clearly identified.",
    ]:
        return {
            "error": "No clear health claim was detected from the video/caption."
        }

    evidence_data = search_trusted_sources(main_claim)

    if "error" in evidence_data:
        return evidence_data

    final_result = compare_claim_with_evidence(
        url=url,
        title=title,
        platform_or_source=platform_or_source,
        creator=creator,
        caption=caption,
        transcript=transcript,
        combined_text=combined_text,
        claims_data=claims_data,
        evidence_data=evidence_data,
    )

    return final_result


# ==================================================
# DISPLAY RESULT
# ==================================================
def display_result(result: dict, url: str):
    score = int(result["misinformation_risk_score"])
    risk = result["risk_level"]
    evidence_match = result["evidence_match_level"]

    if risk == "Low Risk":
        risk_class = "pill-low"
    elif risk == "Medium Risk":
        risk_class = "pill-medium"
    else:
        risk_class = "pill-high"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Misinformation Risk Score</div>
                <div class="metric-value">{score}/100</div>
                <div class="metric-sub">{result["score_interpretation"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value" style="font-size:1.45rem;">{risk}</div>
                <div class="pill {risk_class}">{risk}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Evidence Match</div>
                <div class="metric-value" style="font-size:1.35rem;">{evidence_match}</div>
                <div class="metric-sub">Compared with trusted sources</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

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

    with st.container(border=True):
        st.subheader("💬 User Feedback")

        feedback = st.radio(
            "Was this analysis useful?",
            ["👍 Useful", "👎 Not useful"],
            horizontal=True
        )

        comment = st.text_area(
            "Optional comment",
            placeholder="Example: The score and evidence summary were helpful."
        )

        if st.button("Submit Feedback"):
            st.success("Thank you! Your feedback was submitted.")


# ==================================================
# BUTTON LOGIC
# ==================================================
if analyze_clicked:
    is_valid, message = validate_video_url(video_url)

    if not is_valid:
        st.warning(message)
    else:
        with st.spinner(
            "Fetching video, transcribing audio, searching medical evidence, and calculating risk score..."
        ):
            result = run_pipeline(video_url)

        if "error" in result:
            st.error(result["error"])
            st.info(
                "If URL-only fetching fails, the video may be private, login-restricted, blocked, or unsupported."
            )
        else:
            display_result(result, video_url)

            st.session_state.analysis_history.append(
                {
                    "url": video_url,
                    "risk": result["risk_level"],
                    "score": result["misinformation_risk_score"],
                }
            )
