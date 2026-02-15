# image-generator/app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine import ImageGenerator

# --- Page Config ---
st.set_page_config(
    page_title="Image Generator | Bharat Creator AI",
    page_icon="🎨",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #f5576c 100%);
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

    .agent-box {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #444;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .agent-box h4 { color: #a18cd1; }

    .style-chip {
        display: inline-block;
        background: linear-gradient(135deg, #a18cd1, #fbc2eb);
        color: #1a1a2e;
        padding: 6px 16px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #a18cd1, #f5576c) !important;
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
st.markdown('<h1 class="main-header">🎨 Cover Page Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dual-Agent AI: Prompt Refiner + Titan Image Generator — powered by Amazon Bedrock</p>', unsafe_allow_html=True)

# --- How it works ---
with st.expander("🧠 How the Dual-Agent System Works", expanded=False):
    col_a1, col_arrow, col_a2 = st.columns([4, 1, 4])
    with col_a1:
        st.markdown("**🤖 Agent 1 — Prompt Refiner (Claude)**")
        st.markdown("Takes your basic description and transforms it into a detailed, optimized image generation prompt with specific visual details, colors, composition, and style.")
    with col_arrow:
        st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>→</h1>", unsafe_allow_html=True)
    with col_a2:
        st.markdown("**🎨 Agent 2 — Image Generator (Titan)**")
        st.markdown("Takes the refined prompt and generates a stunning cover page / thumbnail using Amazon Titan Image Generator.")

# --- Initialize ---
@st.cache_resource
def load_generator():
    return ImageGenerator()

try:
    generator = load_generator()
except Exception as e:
    st.error(f"⚠️ Failed to initialize: {str(e)}")
    st.stop()

# --- Input Section ---
st.markdown("### 🖼️ Describe your cover page")

raw_prompt = st.text_area(
    "What should the cover image look like?",
    placeholder="e.g., A tech tutorial cover about learning Python programming with a futuristic coding theme\n\nor: A food blog cover showing colorful Indian street food with a festive vibe",
    height=100
)

col1, col2, col3 = st.columns(3)

with col1:
    styles = generator.get_style_presets()
    style_options = {f"{v['description'][:40]}...": k for k, v in styles.items()}
    style_names = {k: f"{k.title()} — {v['description']}" for k, v in styles.items()}
    selected_style = st.selectbox(
        "Visual Style",
        options=list(styles.keys()),
        format_func=lambda x: f"{x.title()} — {styles[x]['description'][:50]}",
        index=0
    )

with col2:
    sizes = generator.get_size_options()
    size_options = {s['label']: s for s in sizes}
    selected_size_label = st.selectbox(
        "Image Size",
        options=[s['label'] for s in sizes],
        index=0
    )
    selected_size = size_options[selected_size_label]

with col3:
    auto_refine = st.checkbox("✨ Use Agent 1 (Prompt Refiner)", value=True)
    st.caption("Recommended — Claude refines your prompt for better results")

# --- Generate Button ---
st.markdown("---")

if st.button("🎨 Generate Cover Image", use_container_width=True):
    if not raw_prompt.strip():
        st.warning("Please describe what your cover page should look like!")
    else:
        with st.spinner("🤖 Agent 1 is refining your prompt..." if auto_refine else "🎨 Generating image..."):
            try:
                result = generator.generate_image(
                    raw_prompt=raw_prompt,
                    style=selected_style,
                    width=selected_size['width'],
                    height=selected_size['height'],
                    auto_refine=auto_refine
                )

                st.success("✅ Cover image generated!")
                st.markdown("---")

                # Show the dual-agent process
                if auto_refine:
                    st.markdown("### 🤖 Agent 1: Prompt Refinement")
                    ref_col1, ref_col2 = st.columns(2)

                    with ref_col1:
                        st.markdown("**Your Prompt (raw):**")
                        st.code(result['raw_prompt'], language=None)

                    with ref_col2:
                        st.markdown("**Refined Prompt (by Claude):**")
                        st.code(result['refined_prompt'], language=None)

                    if result.get('refinement_reasoning'):
                        st.info(f"💡 **Why**: {result['refinement_reasoning']}")

                    st.markdown("---")

                # Show the generated image
                st.markdown("### 🎨 Agent 2: Generated Image")
                st.image(result['image_bytes'], caption="Generated Cover Page", use_container_width=True)

                # Download button
                st.download_button(
                    label="⬇️ Download Image",
                    data=result['image_bytes'],
                    file_name=f"cover_{selected_style}.png",
                    mime="image/png",
                    use_container_width=True
                )

                # Metadata
                st.markdown("---")
                meta_cols = st.columns(4)
                with meta_cols[0]:
                    st.metric("Style", selected_style.title())
                with meta_cols[1]:
                    st.metric("Size", selected_size_label)
                with meta_cols[2]:
                    st.metric("File Size", f"{result['image_size'] / 1024:.0f} KB")
                with meta_cols[3]:
                    st.metric("Agent Pipeline", "Dual-Agent" if auto_refine else "Direct")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Check your AWS Bedrock configuration. Make sure Titan Image Generator access is enabled.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "Bharat Creator AI — Powered by Amazon Bedrock + Titan Image | AI for Bharat 🇮🇳"
    "</p>",
    unsafe_allow_html=True
)
