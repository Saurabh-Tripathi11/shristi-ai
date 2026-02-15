# voice-generator/app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine import VoiceGenerator

# --- Page Config ---
st.set_page_config(
    page_title="Voice Generator | Bharat Creator AI",
    page_icon="🎤",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .lang-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .lang-card h4 { color: #38ef7d; margin: 0; }
    .lang-card p { color: #aaa; font-size: 0.85rem; margin: 0.3rem 0 0; }

    .stButton > button {
        background: linear-gradient(135deg, #11998e, #38ef7d) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-header">🎤 Voice Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-dialect voiceovers for Indian creators — AWS Polly + Google Cloud TTS</p>', unsafe_allow_html=True)

# --- Initialize ---
@st.cache_resource
def load_generator():
    return VoiceGenerator()

try:
    generator = load_generator()
except Exception as e:
    st.error(f"⚠️ Failed to initialize: {str(e)}")
    st.stop()

# --- Supported Languages ---
languages = generator.get_supported_languages()
moods = generator.get_supported_moods()

with st.expander("🌍 Supported Languages", expanded=False):
    lang_cols = st.columns(3)
    for i, lang in enumerate(languages):
        with lang_cols[i % 3]:
            st.markdown(
                f'<div class="lang-card">'
                f'<h4>{lang["name"]}</h4>'
                f'<p>{lang["speakers"]} speakers • {lang["service"]}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

# --- Input Section ---
st.markdown("### ✍️ Enter your script")

script_text = st.text_area(
    "Script text to convert to speech",
    placeholder="Type or paste your script here...\n\nExample (Hindi): नमस्ते! आज हम बात करेंगे भारत के सबसे लोकप्रिय स्ट्रीट फूड के बारे में।\nExample (Tamil): வணக்கம்! இன்று நாம் இந்தியாவின் சிறந்த தெரு உணவுகளைப் பற்றி பேசுவோம்.",
    height=150
)

col1, col2 = st.columns(2)

with col1:
    language_options = {lang['name']: lang['key'] for lang in languages}
    selected_lang_name = st.selectbox(
        "Language",
        options=list(language_options.keys()),
        index=0
    )
    selected_lang_key = language_options[selected_lang_name]

with col2:
    mood_options = {mood['description']: mood['key'] for mood in moods}
    selected_mood_name = st.selectbox(
        "Mood / Tone",
        options=list(mood_options.keys()),
        index=3  # default: casual
    )
    selected_mood_key = mood_options[selected_mood_name]

# Show which service will be used
lang_info = generator.LANGUAGE_CONFIG[selected_lang_key]
service_label = "AWS Polly (Neural)" if lang_info['service'] == 'polly' else "Google Cloud TTS (Wavenet)"
st.caption(f"🔧 Will use: **{service_label}** for {selected_lang_name}")

# --- Generate Button ---
st.markdown("---")

if st.button("🔊 Generate Voiceover", use_container_width=True):
    if not script_text.strip():
        st.warning("Please enter some text to convert to speech!")
    else:
        with st.spinner(f"🎙️ Generating {selected_lang_name} voiceover ({selected_mood_key} mood)..."):
            try:
                audio_bytes = generator.generate_voiceover(
                    text=script_text,
                    language=selected_lang_key,
                    mood=selected_mood_key
                )

                st.success(f"✅ Voiceover generated! ({len(audio_bytes):,} bytes)")

                # Audio player
                st.markdown("### 🔊 Listen")
                st.audio(audio_bytes, format='audio/mp3')

                # Download button
                st.download_button(
                    label="⬇️ Download MP3",
                    data=audio_bytes,
                    file_name=f"voiceover_{selected_lang_key}_{selected_mood_key}.mp3",
                    mime="audio/mpeg",
                    use_container_width=True
                )

                # Info
                st.markdown("---")
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.metric("Language", selected_lang_name)
                with info_cols[1]:
                    st.metric("Mood", selected_mood_key.title())
                with info_cols[2]:
                    st.metric("Service", service_label)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                    st.info("💡 Check your Google Cloud credentials or AWS configuration.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "Bharat Creator AI — AWS Polly + Google Cloud TTS | AI for Bharat 🇮🇳"
    "</p>",
    unsafe_allow_html=True
)
