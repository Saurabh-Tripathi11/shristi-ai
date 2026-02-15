# content-repurposer/app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine import ContentRepurposer

# --- Page Config ---
st.set_page_config(
    page_title="Content Repurposer | Bharat Creator AI",
    page_icon="🔄",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

    .platform-tab {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #f093fb, #f5576c) !important;
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
st.markdown('<h1 class="main-header">🔄 Content Repurposer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">One script → Four platforms. Maximize your content ROI — powered by Amazon Bedrock</p>', unsafe_allow_html=True)

# --- Initialize ---
@st.cache_resource
def load_repurposer():
    return ContentRepurposer()

try:
    repurposer = load_repurposer()
except Exception as e:
    st.error(f"⚠️ Failed to initialize: {str(e)}")
    st.stop()

# --- Input Section ---
st.markdown("### 📄 Paste your long-form content")

long_content = st.text_area(
    "Blog post, article, video script, newsletter, or any long-form content",
    placeholder="Paste your content here... It can be a blog post, video script, newsletter, or any long-form piece.\n\nThe AI will intelligently transform it into platform-optimized short-form content for Instagram, Twitter/X, LinkedIn, and YouTube Shorts.",
    height=250
)

col1, col2, col3 = st.columns(3)

with col1:
    target_audience = st.text_input(
        "Target Audience",
        value="Indian audience",
        placeholder="e.g., Indian developers aged 18-30"
    )

with col2:
    language = st.selectbox(
        "Output Language",
        options=['English', 'Hindi', 'Hinglish'],
        index=0
    )

with col3:
    niche = st.text_input(
        "Content Niche (optional)",
        placeholder="e.g., tech, food, fitness"
    )

# --- Output Platforms Preview ---
formats = repurposer.get_platform_formats()
with st.expander("📱 Output Formats", expanded=False):
    fmt_cols = st.columns(4)
    for i, (key, fmt) in enumerate(formats.items()):
        with fmt_cols[i]:
            st.markdown(f"**{fmt['icon']} {fmt['name']}**")
            st.caption(fmt['description'])

# --- Generate Button ---
st.markdown("---")

if st.button("🔄 Repurpose Content", use_container_width=True):
    if not long_content.strip() or len(long_content.strip()) < 50:
        st.warning("Please paste substantial content (at least 50 characters) to repurpose!")
    else:
        with st.spinner("🧠 AI is repurposing your content for 4 platforms..."):
            try:
                result = repurposer.repurpose_content(
                    long_form_content=long_content,
                    target_audience=target_audience,
                    language=language,
                    niche=niche
                )

                st.success("✅ Content repurposed for 4 platforms!")

                # Summary
                if result.get('content_summary'):
                    st.info(f"📝 **Summary**: {result['content_summary']}")
                if result.get('best_platform'):
                    st.success(f"🏆 **Best Platform**: {result['best_platform']}")

                st.markdown("---")

                # --- Tabbed Output ---
                tab_ig, tab_tw, tab_li, tab_yt = st.tabs([
                    "📸 Instagram Carousel",
                    "🐦 Twitter/X Thread",
                    "💼 LinkedIn Post",
                    "🎬 YouTube Shorts"
                ])

                # Instagram Carousel
                with tab_ig:
                    ig = result.get('instagram_carousel', {})
                    slides = ig.get('slides', [])
                    if slides:
                        st.markdown(f"**{len(slides)} slides generated**")
                        for i, slide in enumerate(slides):
                            st.markdown(f"**Slide {i+1}**")
                            st.markdown(f"> {slide}")
                            st.markdown("---")
                        st.markdown("**Caption:**")
                        st.text_area("IG Caption:", value=ig.get('caption', ''), height=80, key="ig_caption")
                        st.markdown(f"**Hashtags:** {' '.join(ig.get('hashtags', []))}")

                # Twitter Thread
                with tab_tw:
                    tw = result.get('twitter_thread', {})
                    tweets = tw.get('tweets', [])
                    if tweets:
                        st.markdown(f"**{len(tweets)}-tweet thread**")
                        for tweet in tweets:
                            st.markdown(f"> {tweet}")
                            st.caption(f"({len(tweet)} chars)")
                            st.markdown("---")
                        full_thread = '\n\n'.join(tweets)
                        st.text_area("Copy full thread:", value=full_thread, height=200, key="tw_thread")

                # LinkedIn Post
                with tab_li:
                    li = result.get('linkedin_post', {})
                    post_text = li.get('post_text', '')
                    if post_text:
                        st.text_area("LinkedIn Post:", value=post_text, height=300, key="li_post")
                        st.markdown(f"**Hashtags:** {' '.join(li.get('hashtags', []))}")
                        st.caption(f"({len(post_text)} characters)")

                # YouTube Shorts
                with tab_yt:
                    yt = result.get('youtube_shorts', {})
                    if yt.get('script'):
                        st.markdown(f"**Title:** {yt.get('title', 'N/A')}")
                        st.text_area("Shorts Script:", value=yt.get('script', ''), height=250, key="yt_script")
                        st.markdown(f"**Description:** {yt.get('description', '')}")
                        st.markdown(f"**Hashtags:** {' '.join(yt.get('hashtags', []))}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "Bharat Creator AI — Powered by Amazon Bedrock | AI for Bharat 🇮🇳"
    "</p>",
    unsafe_allow_html=True
)
