# script-generator/app.py
# Multi-Agent Script Generator — Streamlit UI
# Redesigned: Grok + Kimi inspired dark cinematic UI

import streamlit as st
import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine import MultiAgentScriptGenerator

# --- Page Config ---
st.set_page_config(
    page_title="Srishti — AI Script Generator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Load background image as base64 ---
def get_bg_image():
    img_path = os.path.join(os.path.dirname(__file__), 'srishti_bg.jpg')
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_base64 = get_bg_image()
bg_css = f"""
    background-image: url("data:image/jpeg;base64,{bg_base64}");
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    background-attachment: fixed;
""" if bg_base64 else "background: #0a0a14;"

# --- Custom CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── GLOBAL RESETS ── */
    .stApp {{
        {bg_css}
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e4e4e7;
    }}

    /* Hide streamlit defaults */
    #MainMenu, header, footer {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 760px !important;
    }}

    /* ── HERO SECTION ── */
    .hero-container {{
        text-align: center;
        padding: 3rem 0 1.5rem 0;
    }}
    .hero-title {{
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        line-height: 1.1;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        color: rgba(161,161,170,0.7);
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    .hero-sparkle {{
        font-size: 1.4rem;
        color: rgba(255,255,255,0.15);
        margin-top: 1rem;
    }}

    /* ── GLASS CARD ── */
    .glass-card {{
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.2rem;
    }}
    .glass-card-sm {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }}

    /* ── SECTION LABEL ── */
    .section-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: rgba(161,161,170,0.5);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }}

    /* ── FORM STYLING (AGGRESSIVE DARK MODE) ── */
    /* Text areas */
    .stTextArea textarea,
    .stTextArea [data-baseweb="textarea"],
    .stTextArea div[data-baseweb] textarea {{
        background: rgba(255,255,255,0.05) !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        color: #e4e4e7 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        caret-color: #fbbf24 !important;
    }}
    .stTextArea > div > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    /* Text inputs */
    .stTextInput input,
    .stTextInput [data-baseweb="input"],
    .stTextInput div[data-baseweb] input {{
        background: rgba(255,255,255,0.05) !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        color: #e4e4e7 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        caret-color: #fbbf24 !important;
    }}
    .stTextInput > div > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    /* Force dark on all baseweb wrappers */
    [data-baseweb="textarea"], [data-baseweb="input"],
    [data-baseweb="base-input"] {{
        background-color: rgba(255,255,255,0.05) !important;
        border-color: rgba(255,255,255,0.1) !important;
    }}
    /* Focus states */
    .stTextArea textarea:focus,
    .stTextInput input:focus,
    [data-baseweb="textarea"]:focus-within,
    [data-baseweb="input"]:focus-within {{
        border-color: rgba(234,179,8,0.5) !important;
        box-shadow: 0 0 0 2px rgba(234,179,8,0.15) !important;
    }}
    /* Placeholders */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {{
        color: rgba(161,161,170,0.35) !important;
    }}

    /* Select boxes */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.05) !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        color: #e4e4e7 !important;
    }}
    .stSelectbox [data-baseweb="select"] {{
        background: transparent !important;
    }}
    /* Dropdown menu */
    [data-baseweb="popover"], [data-baseweb="menu"],
    ul[role="listbox"] {{
        background: #1a1a2e !important;
        background-color: #1a1a2e !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }}
    [data-baseweb="menu"] li,
    ul[role="listbox"] li {{
        background: transparent !important;
        color: #e4e4e7 !important;
    }}
    [data-baseweb="menu"] li:hover,
    ul[role="listbox"] li:hover {{
        background: rgba(234,179,8,0.15) !important;
    }}
    /* Labels */
    .stSelectbox label, .stTextArea label, .stTextInput label {{
        color: rgba(228,228,231,0.6) !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.3px !important;
    }}

    /* ── BUTTON ── */
    .stButton > button {{
        background: linear-gradient(135deg, rgba(234,179,8,0.9), rgba(202,138,4,0.9)) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(234,179,8,0.3) !important;
    }}
    .stButton > button:hover {{
        box-shadow: 0 6px 30px rgba(234,179,8,0.5) !important;
        transform: translateY(-1px);
    }}

    /* ── PIPELINE AGENT STATUS ── */
    .agent-status-row {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.7rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.4rem;
        transition: all 0.3s ease;
    }}
    .agent-waiting {{
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
    }}
    .agent-running {{
        background: rgba(234,179,8,0.08);
        border: 1px solid rgba(234,179,8,0.2);
        animation: agent-pulse 2s ease-in-out infinite;
    }}
    .agent-done {{
        background: rgba(34,197,94,0.06);
        border: 1px solid rgba(34,197,94,0.15);
    }}
    .agent-error {{
        background: rgba(239,68,68,0.06);
        border: 1px solid rgba(239,68,68,0.15);
    }}
    @keyframes agent-pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    .agent-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }}
    .dot-waiting {{ background: rgba(161,161,170,0.3); }}
    .dot-running {{ background: #eab308; box-shadow: 0 0 8px rgba(234,179,8,0.6); animation: dot-blink 1s infinite; }}
    .dot-done {{ background: #22c55e; }}
    .dot-error {{ background: #ef4444; }}
    @keyframes dot-blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.3; }}
    }}

    .agent-name {{
        font-size: 0.85rem;
        font-weight: 500;
        color: rgba(228,228,231,0.8);
        flex: 1;
    }}
    .agent-badge {{
        font-size: 0.65rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 8px;
        letter-spacing: 0.5px;
    }}
    .badge-waiting {{ background: rgba(161,161,170,0.1); color: rgba(161,161,170,0.5); }}
    .badge-running {{ background: rgba(234,179,8,0.15); color: #fbbf24; }}
    .badge-done {{ background: rgba(34,197,94,0.12); color: #4ade80; }}
    .badge-error {{ background: rgba(239,68,68,0.12); color: #f87171; }}

    /* ── EXPANDER STYLING ── */
    .streamlit-expanderHeader {{
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        color: #e4e4e7 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }}
    .streamlit-expanderContent {{
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 0 0 14px 14px !important;
    }}

    /* ── DIVIDERS ── */
    hr {{
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.06) !important;
        margin: 1.5rem 0 !important;
    }}

    /* ── METRIC CARDS ── */
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 0.8rem 1rem;
    }}
    [data-testid="stMetricLabel"] {{
        color: rgba(161,161,170,0.6) !important;
        font-size: 0.75rem !important;
    }}
    [data-testid="stMetricValue"] {{
        color: #e4e4e7 !important;
        font-size: 1rem !important;
    }}

    /* ── SUCCESS / ERROR ── */
    .stSuccess {{
        background: rgba(34,197,94,0.08) !important;
        border: 1px solid rgba(34,197,94,0.15) !important;
        border-radius: 14px !important;
        color: #bbf7d0 !important;
    }}
    .stAlert {{
        border-radius: 14px !important;
    }}
    .stInfo {{
        background: rgba(234,179,8,0.08) !important;
        border: 1px solid rgba(234,179,8,0.15) !important;
        border-radius: 14px !important;
    }}

    /* ── CODE BLOCKS ── */
    .stCodeBlock {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
    }}

    /* ── TEXT AREA (script output) ── */
    .stTextArea [data-baseweb="textarea"] {{
        background: rgba(255,255,255,0.03) !important;
        border-radius: 12px !important;
    }}

    /* ── CONFIDENCE BADGES ── */
    .confidence-high {{ color: #4ade80; font-weight: 700; }}
    .confidence-medium {{ color: #fbbf24; font-weight: 700; }}
    .confidence-low {{ color: #f87171; font-weight: 700; }}

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.08); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.15); }}

    /* ── FOOTER ── */
    .footer-text {{
        text-align: center;
        color: rgba(161,161,170,0.3);
        font-size: 0.75rem;
        letter-spacing: 1px;
        padding: 2rem 0 1rem 0;
    }}
    .footer-text a {{ color: rgba(234,179,8,0.5); text-decoration: none; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Srishti</div>
    <div class="hero-subtitle">5-Agent AI Script Generator</div>
    <div class="hero-sparkle">✦</div>
</div>
""", unsafe_allow_html=True)

# --- Initialize ---
@st.cache_resource
def load_generator():
    return MultiAgentScriptGenerator()

try:
    generator = load_generator()
except Exception as e:
    st.error(f"Failed to initialize: {str(e)}")
    st.stop()

# ═══════════════════════════════════════════
# PIPELINE INFO (collapsed)
# ═══════════════════════════════════════════
with st.expander("How the pipeline works", expanded=False):
    agents_info = [
        ("Prompt Refiner", "Transforms vague ideas into master prompts", "Bedrock"),
        ("Researcher", "Web search for latest facts & data", "Gemini"),
        ("Trend Analyst", "Analyzes niche & platform trends", "Bedrock"),
        ("Fact Checker", "Validates all claims before scripting", "Bedrock"),
        ("Script Writer", "Writes the final viral script", "Bedrock"),
    ]
    for i, (name, desc, model) in enumerate(agents_info, 1):
        st.markdown(f"**Agent {i}: {name}** — {desc} `{model}`")

# ═══════════════════════════════════════════
# INPUT SECTION
# ═══════════════════════════════════════════
st.markdown('<div class="section-label">What do you want to create?</div>', unsafe_allow_html=True)

raw_topic = st.text_area(
    "Describe your video idea",
    placeholder="Best street food in Mumbai you MUST try...\n\nBe vague — Agent 1 will refine it.",
    height=90,
    label_visibility="collapsed"
)

col1, col2 = st.columns(2)
with col1:
    niche = st.selectbox("Niche", options=[n.title() for n in generator.get_available_niches()], index=1)
    platform = st.selectbox("Platform", options=[p.title() for p in generator.get_available_platforms()])
with col2:
    duration_map = {'15 seconds': '15 seconds', '30 seconds': '30 seconds', '60 seconds': '60 seconds', '90 seconds': '90 seconds', '3 minutes': '3 minutes'}
    duration = st.selectbox("Duration", options=list(duration_map.keys()), index=1)
    language = st.selectbox("Language", options=['English', 'Hindi', 'Hinglish', 'Tamil', 'Telugu', 'Bengali', 'Marathi'])

additional_context = st.text_input(
    "Instructions (optional)",
    placeholder="Include a funny intro, target college students...",
    label_visibility="visible"
)

# --- Trend Insights ---
niche_info = generator.get_niche_info(niche.lower())
if niche_info:
    with st.expander(f"Trend insights — {niche}", expanded=False):
        st.markdown(f"**Trending:** {', '.join(niche_info['trending_topics'])}")
        st.markdown(f"**Hashtags:** {' '.join(niche_info['hashtags'])}")
        st.markdown(f"**Best time:** {niche_info['best_time']}")
        st.caption(f"💡 {niche_info['engagement_tip']}")

# ═══════════════════════════════════════════
# GENERATE BUTTON
# ═══════════════════════════════════════════
st.markdown("")  # spacer
if st.button("✦  Generate Script", use_container_width=True):
    if not raw_topic.strip():
        st.warning("Enter a topic to begin.")
    else:
        # --- Agent Pipeline Visualization ---
        pipeline_container = st.container()
        agent_placeholders = {}
        agent_defs = [
            ('Agent 1', 'Prompt Refiner'),
            ('Agent 2', 'Researcher'),
            ('Agent 3', 'Trend Analyst'),
            ('Agent 4', 'Fact Checker'),
            ('Agent 5', 'Script Writer'),
        ]

        def render_agent(ph, num, name, status='waiting', detail=''):
            status_map = {
                'waiting': ('dot-waiting', 'agent-waiting', 'badge-waiting', 'Waiting'),
                'running': ('dot-running', 'agent-running', 'badge-running', 'Running'),
                'done':    ('dot-done', 'agent-done', 'badge-done', 'Done'),
                'error':   ('dot-error', 'agent-error', 'badge-error', 'Error'),
            }
            dot_cls, row_cls, badge_cls, badge_text = status_map[status]
            if detail:
                badge_text = detail
            ph.markdown(f"""
            <div class="agent-status-row {row_cls}">
                <div class="agent-dot {dot_cls}"></div>
                <div class="agent-name">{num} — {name}</div>
                <div class="agent-badge {badge_cls}">{badge_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with pipeline_container:
            st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
            for num, name in agent_defs:
                agent_placeholders[num] = st.empty()
                render_agent(agent_placeholders[num], num, name, 'waiting')

        try:
            # Agent 1
            render_agent(agent_placeholders['Agent 1'], 'Agent 1', 'Prompt Refiner', 'running', 'Refining...')
            result = {'agents': {}}
            master_prompt = generator.agent_prompt_refiner(raw_topic, niche.lower(), platform.lower(), duration, language, additional_context)
            result['agents']['prompt_refiner'] = master_prompt
            render_agent(agent_placeholders['Agent 1'], 'Agent 1', 'Prompt Refiner', 'done')

            # Agent 2
            render_agent(agent_placeholders['Agent 2'], 'Agent 2', 'Researcher', 'running', 'Searching web...')
            research = generator.agent_researcher(master_prompt)
            result['agents']['researcher'] = research
            render_agent(agent_placeholders['Agent 2'], 'Agent 2', 'Researcher', 'done')

            # Agent 3
            render_agent(agent_placeholders['Agent 3'], 'Agent 3', 'Trend Analyst', 'running', 'Analyzing...')
            trends = generator.agent_trend_analyst(master_prompt, niche.lower(), platform.lower())
            result['agents']['trend_analyst'] = trends
            render_agent(agent_placeholders['Agent 3'], 'Agent 3', 'Trend Analyst', 'done')

            # Agent 4
            render_agent(agent_placeholders['Agent 4'], 'Agent 4', 'Fact Checker', 'running', 'Verifying...')
            fact_check = generator.agent_fact_checker(research, master_prompt)
            result['agents']['fact_checker'] = fact_check
            render_agent(agent_placeholders['Agent 4'], 'Agent 4', 'Fact Checker', 'done')

            # Agent 5
            render_agent(agent_placeholders['Agent 5'], 'Agent 5', 'Script Writer', 'running', 'Writing...')
            script = generator.agent_script_writer(master_prompt, research, fact_check, trends, platform.lower(), duration, language)
            result['script'] = script
            render_agent(agent_placeholders['Agent 5'], 'Agent 5', 'Script Writer', 'done')

            st.success("All 5 agents completed successfully.")
            st.markdown("---")

            # ═══════════════════════════════════════════
            # AGENT OUTPUTS
            # ═══════════════════════════════════════════
            st.markdown('<div class="section-label">Agent Outputs</div>', unsafe_allow_html=True)

            with st.expander("Agent 1 — Master Prompt", expanded=True):
                mp = result['agents']['prompt_refiner']
                st.markdown(f"**Prompt:** {mp.get('master_prompt', 'N/A')}")
                st.markdown(f"**Angle:** {mp.get('content_angle', 'N/A')}")
                st.markdown(f"**Emotion:** {mp.get('target_emotion', 'N/A')}")
                if mp.get('key_points'):
                    for kp in mp['key_points']:
                        st.markdown(f"• {kp}")

            with st.expander("Agent 2 — Research", expanded=False):
                research_data = result['agents']['researcher']
                st.markdown(f"**Source:** {research_data.get('source', 'N/A')}")
                st.markdown(research_data.get('research_summary', 'No research available'))

            with st.expander("Agent 3 — Trend Analysis", expanded=False):
                trend_data = result['agents']['trend_analyst']
                st.markdown(f"**Trending Angle:** {trend_data.get('trending_angle', 'N/A')}")
                st.markdown(f"**Format:** {trend_data.get('recommended_format', 'N/A')}")
                st.markdown(f"**Style:** {trend_data.get('content_style', 'N/A')}")
                if trend_data.get('viral_hooks'):
                    st.markdown("**Viral Hooks:**")
                    for i, hook in enumerate(trend_data['viral_hooks'], 1):
                        st.markdown(f"{i}. {hook}")

            with st.expander("Agent 4 — Fact Check", expanded=False):
                fc = result['agents']['fact_checker']
                confidence = fc.get('overall_confidence', 'unknown')
                badge_class = 'high' if confidence == 'high' else ('medium' if confidence == 'medium' else 'low')
                st.markdown(f"**Confidence:** <span class='confidence-{badge_class}'>{confidence.upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"**Usability:** {fc.get('usability_score', 'N/A')}/10")
                st.markdown(f"**Recommendation:** {fc.get('recommendation', 'N/A')}")
                if fc.get('verified_facts'):
                    for fact in fc['verified_facts']:
                        st.markdown(f"✓ {fact}")
                if fc.get('flagged_claims'):
                    st.markdown("**Flagged:**")
                    for flag in fc['flagged_claims']:
                        st.markdown(f"⚠ {flag}")

            # ═══════════════════════════════════════════
            # FINAL SCRIPT
            # ═══════════════════════════════════════════
            st.markdown("---")
            st.markdown('<div class="section-label">Final Script</div>', unsafe_allow_html=True)

            if result.get('script'):
                s = result['script']

                # Hook
                st.markdown("#### The Hook")
                st.info(s.get('hook', 'N/A'))

                # Main Script
                st.markdown("#### Script")
                st.text_area("Script", value=s.get('main_content', ''), height=200, key="main_script", label_visibility="collapsed")

                # CTA
                st.markdown("#### Call to Action")
                st.success(s.get('cta', 'N/A'))

                # Caption + Hashtags
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("#### Caption")
                    caption_text = s.get('caption', 'N/A')
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem 1rem;font-size:0.9rem;color:#e4e4e7;word-wrap:break-word;">{caption_text}</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown("#### Hashtags")
                    hashtags = s.get('hashtags', [])
                    hashtag_text = ' '.join(hashtags) if isinstance(hashtags, list) else str(hashtags)
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem 1rem;font-size:0.9rem;color:#e4e4e7;word-wrap:break-word;">{hashtag_text}</div>', unsafe_allow_html=True)

                # Metadata
                meta_cols = st.columns(4)
                with meta_cols[0]:
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem;"><div style="font-size:0.7rem;color:rgba(161,161,170,0.6);margin-bottom:4px;">Best Time</div><div style="font-size:0.85rem;color:#e4e4e7;word-wrap:break-word;">{s.get("best_posting_time", "N/A")}</div></div>', unsafe_allow_html=True)
                with meta_cols[1]:
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem;"><div style="font-size:0.7rem;color:rgba(161,161,170,0.6);margin-bottom:4px;">Music</div><div style="font-size:0.85rem;color:#e4e4e7;word-wrap:break-word;">{s.get("music_suggestion", "N/A")}</div></div>', unsafe_allow_html=True)
                with meta_cols[2]:
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem;"><div style="font-size:0.7rem;color:rgba(161,161,170,0.6);margin-bottom:4px;">Thumbnail</div><div style="font-size:0.85rem;color:#e4e4e7;word-wrap:break-word;">{s.get("thumbnail_idea", "N/A")}</div></div>', unsafe_allow_html=True)
                with meta_cols[3]:
                    st.markdown('<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:0.8rem;"><div style="font-size:0.7rem;color:rgba(161,161,170,0.6);margin-bottom:4px;">Agents</div><div style="font-size:0.85rem;color:#e4e4e7;">5 / 5</div></div>', unsafe_allow_html=True)

                # Engagement Strategy
                if s.get('engagement_strategy'):
                    st.markdown("#### Engagement Strategy")
                    st.markdown(s['engagement_strategy'])

        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            st.caption("Check your AWS/Gemini credentials and try again.")

# ═══════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════
st.markdown("""
<div class="footer-text">
    Srishti by Bharat Creator AI  ·  Amazon Bedrock + Gemini  ·  AI for Bharat 🇮🇳
</div>
""", unsafe_allow_html=True)
