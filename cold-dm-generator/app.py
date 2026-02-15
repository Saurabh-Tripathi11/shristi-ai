# cold-dm-generator/app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine import ColdDMGenerator

# --- Page Config ---
st.set_page_config(
    page_title="Cold DM Generator | Bharat Creator AI",
    page_icon="📨",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    .dm-preview {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #444;
        border-radius: 16px;
        padding: 1.5rem;
        font-size: 1rem;
        line-height: 1.7;
        white-space: pre-wrap;
        color: #e0e0e0;
    }

    .research-box {
        background: linear-gradient(145deg, #0d1b2a, #1b2838);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        color: #ccc;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-header">📨 Cold DM Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Land brand deals with AI-crafted personalized outreach — powered by Amazon Bedrock + Gemini</p>', unsafe_allow_html=True)

# --- Initialize ---
@st.cache_resource
def load_generator():
    return ColdDMGenerator()

try:
    generator = load_generator()
except Exception as e:
    st.error(f"⚠️ Failed to initialize: {str(e)}")
    st.stop()

# --- Input Section ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 👤 Your Creator Profile")
    creator_name = st.text_input("Your Name", placeholder="e.g., Anvesh")
    creator_niche = st.text_input("Your Niche", placeholder="e.g., Tech & AI, Food, Fitness")
    audience_size = st.text_input("Audience Size", placeholder="e.g., 50K followers")
    audience_demographic = st.text_area(
        "Your Audience",
        placeholder="e.g., Indian developers, CS students, tech enthusiasts aged 18-30",
        height=80
    )

with col_right:
    st.markdown("### 🏢 Target Brand")
    brand_name = st.text_input("Brand Name", placeholder="e.g., boAt, Mamaearth, Zomato")
    platform = st.selectbox(
        "Platform for DM",
        options=['Instagram', 'LinkedIn', 'Twitter/X', 'Email'],
        index=0
    )
    content_idea = st.text_area(
        "Content Collaboration Idea (optional)",
        placeholder="e.g., Unboxing video + coding setup tour featuring their earbuds",
        height=80
    )
    tone = st.selectbox(
        "Tone",
        options=['Professional yet friendly', 'Casual & fun', 'Formal business', 'Bold & confident'],
        index=0
    )

auto_research = st.checkbox("🔍 Auto-research brand using Gemini (recommended)", value=True)

# --- Generate Button ---
st.markdown("---")

if st.button("🚀 Generate Cold DM", use_container_width=True):
    if not creator_name.strip() or not brand_name.strip():
        st.warning("Please fill in at least your name and the brand name!")
    else:
        with st.spinner("🔍 Researching brand..." if auto_research else "✍️ Crafting your DM..."):
            try:
                result = generator.generate_cold_dm(
                    creator_name=creator_name,
                    creator_niche=creator_niche,
                    audience_size=audience_size,
                    audience_demographic=audience_demographic,
                    brand_name=brand_name,
                    platform=platform.lower().replace('/x', ''),
                    content_idea=content_idea,
                    tone=tone.lower(),
                    auto_research=auto_research
                )

                st.success("✅ Cold DM generated!")
                st.markdown("---")

                # Brand Research
                if auto_research and result.get('brand_research'):
                    st.markdown("### 🔍 Brand Research (by Gemini)")
                    st.markdown(f'<div class="research-box">{result["brand_research"]}</div>', unsafe_allow_html=True)

                # Full DM Preview
                st.markdown("### 📨 Your Cold DM — Ready to Send")
                full_dm = result.get('full_dm', 'N/A')
                st.text_area("Copy this DM:", value=full_dm, height=250, key="dm_copy")

                # Breakdown
                st.markdown("---")
                st.markdown("### 🔍 DM Breakdown")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**🪝 Hook**")
                    st.info(result.get('hook', 'N/A'))
                    st.markdown("**💰 Value Proposition**")
                    st.info(result.get('value_proposition', 'N/A'))

                with col_b:
                    st.markdown("**💡 Pitch**")
                    st.info(result.get('pitch', 'N/A'))
                    st.markdown("**📲 Call to Action**")
                    st.info(result.get('cta', 'N/A'))

                # Extra stuff
                st.markdown("---")
                extra_cols = st.columns(3)

                with extra_cols[0]:
                    st.markdown("**📧 Email Subject Line**")
                    st.code(result.get('subject_line', 'N/A'))

                with extra_cols[1]:
                    st.markdown("**🔁 Follow-up (after 3 days)**")
                    st.text_area("Follow-up:", value=result.get('follow_up', 'N/A'), height=100, key="followup")

                with extra_cols[2]:
                    st.markdown("**💡 Tips for Better Response**")
                    st.text_area("Tips:", value=result.get('tips', 'N/A'), height=100, key="tips")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "Bharat Creator AI — Powered by Amazon Bedrock + Gemini | AI for Bharat 🇮🇳"
    "</p>",
    unsafe_allow_html=True
)
