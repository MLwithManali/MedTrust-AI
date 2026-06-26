# 🩺 MedTrust AI
**AI-Powered Health Misinformation and Influencer Credibility Analyzer**

MedTrust AI is an AI-powered application that analyzes public health-related social media videos and helps users understand whether the health claims are reliable, misleading, exaggerated, or missing important medical context.

The app extracts health claims from public video content, compares them with trusted medical evidence, generates a MedTrust Score, and presents a clear report with evidence summaries, red flags, missing context, safer explanations, and recommended next steps.

---

## Key Features

- Analyze public health-related video URLs
- Extract health claims from captions and transcripts
- Compare claims with trusted medical sources
- Generate a MedTrust Score out of 100
- Identify misinformation risk and red flags
- Highlight missing medical context
- Display trusted evidence sources
- Include safety checks and medical disclaimers
- Collect user feedback after analysis

---

## Screenshots

### Home Page

![Home Page](screenshots/home-page.png)

### Analysis Processing

![Analysis Processing](screenshots/analysis-processing.png)

### Analysis Summary

![Analysis Summary](screenshots/analysis-summary.png)

### Detailed Report Overview

![Detailed Report Overview](screenshots/detailed-report-overview.png)

### Risk and Source Content

![Risk and Source Content](screenshots/risk-context-source.png)

### Transcript Analysis

![Transcript Analysis](screenshots/transcript-analysis.png)

### Trusted Evidence Sources

![Trusted Evidence Sources](screenshots/trusted-evidence.png)

### Feedback Dialog

![Feedback Dialog](screenshots/feedback-dialog.png)

---

## How It Works

```text
Public Health Video URL
        ↓
Fetch Public Video Content
        ↓
Transcribe Audio
        ↓
Extract Health Claims
        ↓
Search Trusted Medical Sources
        ↓
Compare Claim With Evidence
        ↓
Generate MedTrust Score
        ↓
Display Detailed Health Evidence Report
```

---

## MedTrust Score

The MedTrust Score is an AI-assisted misinformation risk estimate.

| Score Range | Risk Level | Meaning |
|-----------:|------------|---------|
| 80–100 | Low Risk | More reliable / lower misinformation risk |
| 50–79 | Medium Risk | Needs review / missing context |
| 0–49 | High Risk | Unsupported, exaggerated, or potentially misleading |

---

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- LLM API: Groq
- Transcription: Groq Whisper
- Evidence Search: Tavily Search API
- Video Processing: yt-dlp
- Environment Management: python-dotenv
- Media Support: imageio-ffmpeg

---

## Project Structure

```text
MedTrust-AI/
│
├── app.py
├── page1.py
├── page2.py
├── medtrust_engine.py
├── requirements.txt
├── README.md
│
├── data/
│   └── sample_posts.txt
│
├── prompts/
│   └── medtrust_prompt.txt
│
└── screenshots/
    ├── home-page.png
    ├── analysis-processing.png
    ├── analysis-summary.png
    ├── detailed-report-overview.png
    ├── risk-context-source.png
    ├── transcript-analysis.png
    ├── trusted-evidence.png
    └── feedback-dialog.png
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/MLwithManali/MedTrust-AI.git
```

Move into the project folder:

```bash
cd MedTrust-AI
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

---

## Safety Features

- URL validation before analysis
- Input sanitization
- Prompt-injection safety checks
- API retry handling
- JSON response validation
- Trusted medical source filtering
- Medical disclaimers
- No diagnosis or treatment recommendations
- User-friendly error handling

---

## Example Test Claims

The repository includes sample test cases inside:

```text
data/sample_posts.txt
```

Example claims include:

- Herbal drink cures diabetes in 7 days
- Avoid all vaccines because natural immunity is better
- Weight loss tea burns belly fat overnight
- Drinking water supports hydration but is not a cure
- Consult a qualified healthcare professional before stopping medication

---

## Disclaimer

MedTrust AI is for educational and informational purposes only.

It does not provide medical diagnosis, treatment, or professional healthcare advice. Users should consult qualified healthcare professionals for personal medical concerns.

---

## Developer

**Manali Gandhi**

MSc Artificial Intelligence  
Heriot-Watt University Dubai

GitHub: [MLwithManali](https://github.com/MLwithManali)

---

## Project Status

Final prototype completed for the Building AI Applications Challenge.

Future improvements may include:

- Cloud deployment
- More platform support
- OCR from video frames
- Better influencer credibility verification
- More detailed medical evidence ranking
- User history dashboard

---

## License

This project is developed for educational purposes.
