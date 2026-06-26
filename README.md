# 🩺 MedTrust AI

**AI-Powered Health Misinformation & Influencer Credibility Analyzer**

MedTrust AI is an AI-powered application that analyzes public health-related social media videos to identify potential misinformation, compare health claims with trusted medical evidence, and generate an easy-to-understand credibility report.

The application helps users make informed decisions by highlighting evidence-based information, detecting misleading claims, identifying missing medical context, and recommending safer actions.

---

## Features

- 🔍 Analyze public health-related video URLs
- 🧠 Automatically extract health claims
- 🏥 Compare claims with trusted medical sources
- ⚠️ Detect misinformation and missing medical context
- 📊 Generate an easy-to-understand MedTrust Score
- 📑 Produce a detailed evidence report
- 🔗 Display trusted medical references
- 🛡️ Built-in safety checks and prompt injection protection
- 💬 User feedback collection

---

## 🖥️ Application Workflow

```
Video URL
      │
      ▼
Download Public Video
      │
      ▼
Audio Transcription
      │
      ▼
Health Claim Extraction
      │
      ▼
Trusted Medical Evidence Search
      │
      ▼
LLM Evidence Comparison
      │
      ▼
Risk Score Generation
      │
      ▼
Detailed Medical Evidence Report
```

---

## 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend

- Python

### AI Models

- Groq LLM

### Medical Search

- Tavily Search API

### Video Processing

- yt-dlp

### Other Libraries

- python-dotenv
- imageio-ffmpeg
- pandas

---

## 📂 Project Structure

```
MedTrust-AI
│
├── app.py
├── page1.py
├── page2.py
├── medtrust_engine.py
├── requirements.txt
├── README.md
│
├── prompts/
│   └── medtrust_prompt.txt
│
├── data/
│   └── sample_posts.txt
│
└── screenshots/
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/MLwithManali/MedTrust-AI.git
```

Move into the project

```bash
cd MedTrust-AI
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GROQ_API_KEY=YOUR_API_KEY
TAVILY_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run app.py
```

---

## 📸 Screenshots

Add your application screenshots inside the **screenshots** folder.

Example:

- Home Page
- Analysis Summary
- Detailed Report
- Evidence Sources
- Feedback Dialog

---

## 🎯 Example Output

The application generates:

- MedTrust Score
- Risk Level
- Evidence Confidence
- AI Detected Claim
- Evidence Summary
- Extracted Health Claims
- Missing Medical Context
- Trusted Evidence Sources
- Recommended Next Step
- Medical Disclaimer

---

## ⚠️ Disclaimer

MedTrust AI is designed for educational and informational purposes only.

It does **not** provide medical diagnosis, treatment, or professional healthcare advice. Users should consult qualified healthcare professionals for medical decisions.

---

## 👩‍💻 Developer

**Manali Gandhi**

MSc Artificial Intelligence

Heriot-Watt University Dubai

GitHub:
https://github.com/MLwithManali

---

## 📜 License

This project is developed for educational purposes as part of the **Building AI Applications Challenge**.
