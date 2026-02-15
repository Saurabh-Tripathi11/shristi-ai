<p align="center">
  <h1 align="center">✦ Srishti — Bharat Creator AI</h1>
  <p align="center">
    <strong>AI-Powered Content Creation Suite for Indian Creators</strong>
  </p>
  <p align="center">
    <em>Multi-Agent pipelines powered by Amazon Bedrock, Google Gemini & AWS Polly</em>
  </p>
  <p align="center">
    <a href="#modules">Modules</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a>
  </p>
</p>

---

## 🎯 What is Srishti?

**Srishti** is a modular AI platform designed specifically for **Indian content creators**. It provides 5 specialized AI tools — each with its own multi-agent pipeline — to help creators script, design, repurpose, and voice-over content for platforms like Instagram, YouTube, LinkedIn, and Twitter.

> **Built for Bharat.** Multi-language support including Hindi, Hinglish, Tamil, Telugu, Bengali, and Marathi.

---

## 📦 Modules

| Module | Description | Agents | AI Models |
|--------|-------------|--------|-----------|
| **✍️ Script Generator** | 5-agent pipeline that transforms vague ideas into viral scripts | Prompt Refiner → Researcher → Trend Analyst → Fact Checker → Script Writer | Bedrock Claude + Gemini |
| **📨 Cold DM Generator** | Craft personalized brand outreach DMs with auto-research | Brand Researcher → DM Writer | Gemini + Bedrock Claude |
| **🔄 Content Repurposer** | Convert long-form content into platform-optimized short-form pieces | Content Transformer | Bedrock Claude |
| **🎨 Image Generator** | Dual-agent thumbnail & cover page generator | Prompt Refiner → Image Generator | Bedrock Claude + Titan Image |
| **🎤 Voice Generator** | Multi-dialect voiceover with mood control | Voice Synthesizer | AWS Polly + Google Cloud TTS |

---

## 🛠️ Tech Stack

<table>
<tr>
<td><strong>Category</strong></td>
<td><strong>Technology</strong></td>
</tr>
<tr>
<td>🤖 LLMs</td>
<td>Amazon Bedrock (Claude 3.5 Sonnet), Google Gemini 2.0 Flash</td>
</tr>
<tr>
<td>🖼️ Image Gen</td>
<td>Amazon Titan Image Generator v1</td>
</tr>
<tr>
<td>🗣️ Voice / TTS</td>
<td>AWS Polly (Neural), Google Cloud Text-to-Speech (Wavenet)</td>
</tr>
<tr>
<td>🌐 Web Search</td>
<td>Gemini Google Search Grounding</td>
</tr>
<tr>
<td>🎨 Frontend</td>
<td>Streamlit (dark cinematic UI)</td>
</tr>
<tr>
<td>☁️ Cloud</td>
<td>AWS (Bedrock, S3, DynamoDB, Polly) + Google Cloud</td>
</tr>
<tr>
<td>🐍 Language</td>
<td>Python 3.10+</td>
</tr>
</table>

---

## 🏗️ Architecture

```
shristi-ai/
├── script-generator/          # 5-Agent Script Pipeline
│   ├── app.py                 #   └─ Streamlit UI
│   └── engine.py              #   └─ Multi-agent orchestrator
│
├── cold-dm-generator/         # Brand Outreach DM Generator
│   ├── app.py                 #   └─ Streamlit UI
│   └── engine.py              #   └─ Gemini research + Bedrock DM writer
│
├── content-repurposer/        # Long-form → Short-form Converter
│   ├── app.py                 #   └─ Streamlit UI
│   └── engine.py              #   └─ Multi-platform content transformer
│
├── image-generator/           # Dual-Agent Thumbnail Generator
│   ├── app.py                 #   └─ Streamlit UI
│   └── engine.py              #   └─ Claude prompt refiner + Titan image gen
│
├── voice-generator/           # Multi-Dialect Voiceover Generator
│   ├── app.py                 #   └─ Streamlit UI
│   └── engine.py              #   └─ Polly (Hindi/English) + Google TTS (regional)
│
├── backend/                   # Shared backend services
│   ├── script_generator.py    #   └─ Gemini-based script engine
│   └── voice_generator.py     #   └─ Bharat Voice Generator service
│
├── .env.example               # Environment variable template
└── .gitignore
```

### Script Generator Pipeline

```
User Input (vague idea)
    │
    ▼
┌─────────────────────────┐
│  Agent 1: Prompt Refiner │  ← Bedrock Claude
│  Vague → Master Prompt   │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────┐  ┌──────────────┐
│ Agent 2: │  │   Agent 3:   │
│Researcher│  │Trend Analyst │
│ (Gemini) │  │  (Bedrock)   │
└────┬─────┘  └──────┬───────┘
     │               │
     └───────┬───────┘
             ▼
    ┌─────────────────┐
    │ Agent 4: Fact    │  ← Bedrock Claude
    │ Checker          │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Agent 5: Script  │  ← Bedrock Claude
    │ Writer           │
    └─────────────────┘
             │
             ▼
      Final Viral Script
   (hook + script + CTA +
    caption + hashtags)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **AWS Account** with Bedrock access (Claude 3.5 Sonnet, Titan Image)
- **Google Cloud** credentials (for TTS & Gemini API)
- **AWS CLI** configured with appropriate IAM permissions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/shristi-ai.git
cd shristi-ai
```

### 2. Set Up Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install boto3 streamlit python-dotenv google-genai google-cloud-texttospeech
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# AWS Configuration
AWS_REGION=ap-south-1
AWS_BEDROCK_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-tts-key.json

# Bedrock Models
BEDROCK_MODEL_CLAUDE=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_MODEL_TITAN_IMAGE=amazon.titan-image-generator-v1

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Run Any Module

```bash
# Script Generator (5-Agent Pipeline)
streamlit run script-generator/app.py

# Cold DM Generator
streamlit run cold-dm-generator/app.py

# Content Repurposer
streamlit run content-repurposer/app.py

# Image Generator
streamlit run image-generator/app.py

# Voice Generator
streamlit run voice-generator/app.py
```

---

## 🌏 Supported Languages

| Language | Script Gen | Voice Gen | Content Repurposer |
|----------|:----------:|:---------:|:------------------:|
| English  | ✅ | ✅ | ✅ |
| Hindi    | ✅ | ✅ | ✅ |
| Hinglish | ✅ | — | ✅ |
| Tamil    | ✅ | ✅ | ✅ |
| Telugu   | ✅ | ✅ | ✅ |
| Bengali  | ✅ | ✅ | ✅ |
| Marathi  | ✅ | ✅ | ✅ |

---

## 📸 Features at a Glance

- **🧠 Multi-Agent AI** — Purpose-built agent pipelines, not simple prompt wrappers
- **🔍 Live Web Research** — Gemini Google Search grounding for real-time data
- **✅ Fact Checking** — Automated verification with confidence scoring
- **📊 Trend Analysis** — Niche-specific trend data for content optimization
- **🎨 Dark Cinematic UI** — Grok + Kimi inspired glassmorphism design
- **🇮🇳 India-First** — Built for Indian creators, platforms, and languages
- **🔁 Content Repurposing** — One script → Instagram Carousel + Twitter Thread + LinkedIn Post + YouTube Shorts
- **🎤 Multi-Dialect TTS** — Regional Indian voices with mood control (exciting, mysterious, casual, etc.)

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-module`)
3. Commit your changes (`git commit -m 'Add new module'`)
4. Push to the branch (`git push origin feature/new-module`)
5. Open a Pull Request

---

## 📄 License

This project is open-source. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Srishti</strong> — Created with ❤️ for Bharat 🇮🇳<br>
  <sub>Amazon Bedrock · Google Gemini · AWS Polly · AI for Bharat</sub>
</p>
