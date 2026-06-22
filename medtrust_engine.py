import os
import json
import time
import shutil
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import yt_dlp
import imageio_ffmpeg


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


def cleanup_temp_dir(temp_dir: str):
    """Best-effort cleanup of downloaded media so /tmp doesn't fill up."""
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)


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
        extractor = info.get("extractor", "")

        media_path = None

        for file in Path(temp_dir).glob("video_media.*"):
            if file.suffix.lower() in [".mp4", ".m4a", ".mp3", ".webm", ".mov"]:
                media_path = str(file)
                break

        if media_path is None:
            cleanup_temp_dir(temp_dir)
            return {
                "error": (
                    "Media could not be downloaded from this URL. "
                    "The content may be private, restricted, unsupported, or blocked."
                )
            }

        return {
            "media_path": media_path,
            "temp_dir": temp_dir,
            "caption": caption,
            "uploader": uploader,
            "title": title,
            "platform_or_source": extractor,
        }

    except Exception as e:
        cleanup_temp_dir(temp_dir)
        return {
            "error": (
                "Could not fetch media/caption from this URL. "
                "This can happen if the content is private, login-restricted, region-blocked, unsupported, or blocked. "
                f"Details: {str(e)}"
            )
        }


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

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "Return only valid JSON. No markdown."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=700,
            )

            return safe_json_loads(response.choices[0].message.content)

        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue

            return {"error": f"Health claim extraction failed: {str(e)}"}


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
        return {"error": f"Tavily search failed: {str(e)}"}


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
        return {"error": "Groq API key not found."}

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

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "You are MedTrust AI. Return only valid JSON. No markdown."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1600,
            )

            result = safe_json_loads(response.choices[0].message.content)
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
            if attempt < 2:
                time.sleep(1)
                continue

            return {"error": f"Evidence comparison failed: {str(e)}"}


def run_pipeline(url: str):
    fetch_result = fetch_public_video_media(url)

    if "error" in fetch_result:
        return fetch_result

    media_path = fetch_result["media_path"]
    temp_dir = fetch_result.get("temp_dir", "")
    caption = fetch_result.get("caption", "")
    creator = fetch_result.get("uploader", "")
    title = fetch_result.get("title", "")
    platform_or_source = fetch_result.get("platform_or_source", "")

    try:
        transcription_result = transcribe_media_file(media_path)

        if "error" in transcription_result:
            return transcription_result

        transcript = transcription_result.get("transcript", "")
    finally:
        # Always clean up the downloaded media file/temp dir once we're
        # done reading it, whether transcription succeeded or failed.
        cleanup_temp_dir(temp_dir)

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
        return {"error": "Not enough text was extracted from the video URL."}

    claims_data = extract_health_claims(combined_text)

    if "error" in claims_data:
        return claims_data

    main_claim = claims_data.get("main_health_claim", "")

    if not main_claim or main_claim.lower() in [
        "no clear health claim identified.",
        "not clearly identified.",
    ]:
        return {"error": "No clear health claim was detected from the video/caption."}

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
