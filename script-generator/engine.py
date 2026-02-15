# script-generator/engine.py
# Multi-Agent Script Generator — 5 Specialized AI Agents

import boto3
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from google import genai

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class MultiAgentScriptGenerator:
    """
    5-Agent Orchestrated Script Generator for Indian Content Creators.

    Pipeline:
        Agent 1 (Prompt Refiner)   → Vague prompt → detailed master prompt
        Agent 2 (Researcher)       → Web research via Gemini grounding
        Agent 3 (Trend Analyst)    → Niche + platform trend analysis
        Agent 4 (Fact Checker)     → Validates research, flags unverified claims
        Agent 5 (Script Writer)    → Final viral script from all agent outputs
    """

    # Curated Indian trend data by niche
    TRENDS_DATA = {
        'food': {
            'trending_topics': [
                'Indian street food ASMR', 'regional thali challenges', 'hidden gem dhabas',
                'homemade recipes with a twist', 'food festivals across India', 'midnight cravings'
            ],
            'hashtags': ['#streetfood', '#indianfood', '#foodie', '#foodreels', '#desikhana', '#foodblogger'],
            'optimal_format': 'Reels 15-30 seconds with sizzling audio',
            'best_time': '7-9 PM IST',
            'engagement_tip': 'Start with a sizzling close-up shot. Reveal the final dish within 3 seconds. Use trending audio.',
        },
        'tech': {
            'trending_topics': [
                'AI tools nobody talks about', 'coding tutorials for beginners', 'gadget unboxings under ₹5000',
                'tech career tips', 'productivity hacks', 'open source projects'
            ],
            'hashtags': ['#coding', '#tech', '#ai', '#learntocode', '#devlife', '#techreels'],
            'optimal_format': 'Carousel or 60-sec screen recording',
            'best_time': '9-11 AM IST',
            'engagement_tip': 'Problem-solution hook in first 2 seconds. Show real screen recordings. End with a challenge.',
        },
        'fitness': {
            'trending_topics': [
                'home workouts no equipment', 'Indian diet plans', 'transformation stories',
                'yoga for beginners', 'desi bodybuilding', 'mental health awareness'
            ],
            'hashtags': ['#fitness', '#homeworkout', '#wellness', '#fitindia', '#yoga', '#transformation'],
            'optimal_format': '15-45 sec transformation or workout clip',
            'best_time': '6-8 AM IST',
            'engagement_tip': 'Before/after hook. Use motivational music. Show real progress, not perfection.',
        },
        'education': {
            'trending_topics': [
                'study hacks for board exams', 'competitive exam tips', 'skill-based learning',
                'career guidance after 12th', 'free online courses', 'memory techniques'
            ],
            'hashtags': ['#education', '#studytips', '#learning', '#students', '#examprep', '#edutok'],
            'optimal_format': 'Carousel or 60-sec explainer',
            'best_time': '4-6 PM IST',
            'engagement_tip': 'Start with a relatable student problem. Use simple visuals. End with a save-worthy tip.',
        },
        'business': {
            'trending_topics': [
                'startup stories from India', 'side hustles for students', 'digital marketing tips',
                'entrepreneurship lessons', 'freelancing in India', 'personal branding'
            ],
            'hashtags': ['#business', '#startup', '#entrepreneur', '#sidehustle', '#hustle', '#growthmindset'],
            'optimal_format': '30-60 sec talking head with text overlay',
            'best_time': '10 AM - 12 PM IST',
            'engagement_tip': 'Share specific numbers and results. Use bold text overlays. Keep it story-driven.',
        },
        'entertainment': {
            'trending_topics': [
                'Bollywood memes', 'regional movie reviews', 'celebrity gossip',
                'stand-up comedy clips', 'behind the scenes', 'trending dialogues'
            ],
            'hashtags': ['#bollywood', '#entertainment', '#memes', '#comedy', '#trending', '#viral'],
            'optimal_format': '15-30 sec meme or sketch',
            'best_time': '8-11 PM IST',
            'engagement_tip': 'Use trending audio. Relatable humor wins. Keep punchline within 5 seconds.',
        },
        'lifestyle': {
            'trending_topics': [
                'morning routines', 'room makeovers on budget', 'travel vlogs India',
                'skincare routines', 'aesthetic daily life', 'minimalism in India'
            ],
            'hashtags': ['#lifestyle', '#aesthetic', '#dailyroutine', '#travelindia', '#skincare', '#vlog'],
            'optimal_format': '30-60 sec aesthetic montage',
            'best_time': '12-2 PM IST or 7-9 PM IST',
            'engagement_tip': 'Aesthetics matter — good lighting, smooth transitions. Use calming or trending music.',
        },
    }

    # Platform-specific specifications
    PLATFORM_SPECS = {
        'instagram': {
            'optimal_caption': '125-150 characters',
            'hashtag_count': '8-12 hashtags',
            'video_length': '15-60 seconds (Reels)',
            'tone': 'casual, emoji-friendly, Gen-Z slang ok',
            'content_types': ['Reels', 'Carousel', 'Stories', 'Static Post'],
        },
        'youtube': {
            'optimal_caption': '200-300 characters description',
            'hashtag_count': '3-5 hashtags',
            'video_length': '8-15 min (long-form) or 30-60 sec (Shorts)',
            'tone': 'informative, engaging, conversational',
            'content_types': ['Shorts', 'Long-form', 'Live'],
        },
        'linkedin': {
            'optimal_caption': '150-200 characters',
            'hashtag_count': '3-5 hashtags',
            'video_length': '30-90 seconds',
            'tone': 'professional, value-driven, thought leadership',
            'content_types': ['Post', 'Article', 'Carousel', 'Video'],
        },
        'twitter': {
            'optimal_caption': '200-280 characters',
            'hashtag_count': '1-2 hashtags',
            'video_length': '15-45 seconds',
            'tone': 'punchy, conversational, hot-take energy',
            'content_types': ['Tweet', 'Thread', 'Video Tweet'],
        },
    }

    def __init__(self):
        """Initialize Bedrock and Gemini clients"""
        # Bedrock for Agents 1, 3, 4, 5
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_CLAUDE', 'us.amazon.nova-pro-v1:0')

        # Gemini for Agent 2 (web search research)
        gemini_key = os.getenv('GEMINI_API_KEY')
        self.gemini_client = None
        if gemini_key:
            self.gemini_client = genai.Client(api_key=gemini_key)

    def _call_bedrock(self, prompt: str, max_tokens: int = 2048) -> str:
        """Call Bedrock via Converse API (model-agnostic)"""
        response = self.bedrock.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": 0.7,
            }
        )
        return response['output']['message']['content'][0]['text']

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini with Google Search grounding for real-time research"""
        if not self.gemini_client:
            return "Research unavailable — Gemini API key not configured."

        try:
            # Use Google Search tool for web-grounded research
            from google.genai import types

            response = self.gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini error: {e}")
            return f"Research error: {str(e)}"

    # ===================================================================
    # AGENT 1: PROMPT REFINER — Vague prompt → Master prompt
    # ===================================================================
    def agent_prompt_refiner(self, raw_topic: str, niche: str, platform: str,
                              duration: str, language: str, context: str = '') -> Dict:
        """
        Agent 1: Transform a vague user topic into a detailed master prompt.
        Adds specificity, angle, target points, and creative direction.
        """
        prompt = f"""You are the PROMPT REFINER agent — an expert at transforming vague content ideas into
highly specific, actionable creative briefs for viral social media content.

USER'S VAGUE INPUT: "{raw_topic}"

CONTEXT:
- Niche: {niche}
- Platform: {platform}
- Duration: {duration}
- Language: {language}
{f'- Creator notes: {context}' if context else ''}

YOUR JOB: Transform this vague idea into a razor-sharp creative brief that gives other agents
(researcher, trend analyst, script writer) exactly what they need.

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "master_prompt": "A detailed, specific version of the topic with clear angle and direction (2-3 sentences)",
  "content_angle": "The specific unique angle/perspective to take",
  "key_points": ["list", "of", "3-5", "specific", "points to cover"],
  "target_emotion": "The primary emotion to evoke (curiosity, FOMO, excitement, etc.)",
  "hook_direction": "A specific direction for the opening hook",
  "research_queries": ["2-3 specific things to research about this topic"]
}}"""

        try:
            content = self._call_bedrock(prompt)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"❌ Agent 1 (Prompt Refiner) error: {e}")
            raise

    # ===================================================================
    # AGENT 2: RESEARCHER — Web search via Gemini grounding
    # ===================================================================
    def agent_researcher(self, master_prompt: Dict) -> Dict:
        """
        Agent 2: Research the topic using Gemini with web search.
        Finds latest data, stats, facts, and trending angles.
        """
        queries = master_prompt.get('research_queries', [master_prompt.get('master_prompt', '')])
        research_prompt = f"""Research the following topic and provide FACTUAL, CURRENT information:

TOPIC: {master_prompt.get('master_prompt', '')}

SPECIFIC RESEARCH AREAS:
{chr(10).join(f'- {q}' for q in queries)}

CONTEXT: This research is for creating a viral social media script for Indian audience.

Provide:
1. 3-5 specific FACTS or STATISTICS related to this topic (with approximate dates if possible)
2. Any recent news, launches, or developments (last 6 months)
3. Popular opinions or debates around this topic in India
4. 2-3 specific examples, case studies, or real names that can be referenced

Keep it factual, specific, and concise. Max 300 words. Focus on data an Indian audience would find interesting."""

        try:
            research_text = self._call_gemini(research_prompt)
            return {
                'research_summary': research_text,
                'queries_used': queries,
                'source': 'Gemini Web Search'
            }
        except Exception as e:
            print(f"❌ Agent 2 (Researcher) error: {e}")
            return {
                'research_summary': f'Research failed: {str(e)}',
                'queries_used': queries,
                'source': 'Error'
            }

    # ===================================================================
    # AGENT 3: TREND ANALYST — Niche + platform trend analysis
    # ===================================================================
    def agent_trend_analyst(self, master_prompt: Dict, niche: str, platform: str) -> Dict:
        """
        Agent 3: Analyze current trends in the niche and platform.
        Combines curated trend data with AI analysis.
        """
        trends = self.TRENDS_DATA.get(niche.lower(), self.TRENDS_DATA['food'])
        platform_spec = self.PLATFORM_SPECS.get(platform.lower(), self.PLATFORM_SPECS['instagram'])

        prompt = f"""You are the TREND ANALYST agent — an expert in Indian social media trends and viral content patterns.

TOPIC: {master_prompt.get('master_prompt', '')}
CONTENT ANGLE: {master_prompt.get('content_angle', '')}
NICHE: {niche}
PLATFORM: {platform}

KNOWN TRENDS IN {niche.upper()} NICHE:
- Trending topics: {', '.join(trends['trending_topics'])}
- Popular hashtags: {', '.join(trends['hashtags'])}
- Optimal format: {trends['optimal_format']}
- Best posting time: {trends['best_time']}
- Engagement tip: {trends['engagement_tip']}

PLATFORM SPECS ({platform.upper()}):
- Video length: {platform_spec['video_length']}
- Caption length: {platform_spec['optimal_caption']}
- Hashtag count: {platform_spec['hashtag_count']}
- Tone: {platform_spec['tone']}
- Content types: {', '.join(platform_spec['content_types'])}

YOUR JOB: Analyze how this specific topic can ride current trends to maximize virality.

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "trending_angle": "How to position this topic to ride current trends",
  "recommended_format": "Best format for this specific content",
  "hashtags": ["10-12", "optimized", "hashtags", "mixing", "trending", "and", "niche"],
  "best_posting_time": "Specific recommended posting time with reasoning",
  "content_style": "Specific style guidelines (transitions, music type, pacing)",
  "viral_hooks": ["3 potential viral hook ideas for the first 3 seconds"],
  "engagement_strategy": "Specific engagement tactics for this content"
}}"""

        try:
            content = self._call_bedrock(prompt)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"❌ Agent 3 (Trend Analyst) error: {e}")
            raise

    # ===================================================================
    # AGENT 4: FACT CHECKER — Validates research output
    # ===================================================================
    def agent_fact_checker(self, research: Dict, master_prompt: Dict) -> Dict:
        """
        Agent 4: Validate and verify the research findings.
        Flags unverified claims, rates confidence, suggests corrections.
        """
        prompt = f"""You are the FACT CHECKER agent — your job is to review research findings and ensure
the content creator doesn't spread misinformation.

TOPIC: {master_prompt.get('master_prompt', '')}

RESEARCH FINDINGS TO VERIFY:
---
{research.get('research_summary', 'No research available')}
---

YOUR JOB:
1. Identify any claims that seem inaccurate, outdated, or unverifiable
2. Rate the overall reliability of the research
3. Suggest corrections or safer phrasings where needed
4. Highlight the strongest, most usable facts

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "overall_confidence": "high/medium/low — overall reliability of the research",
  "verified_facts": ["list of facts that seem accurate and safe to use"],
  "flagged_claims": ["any claims that should be double-checked or softened"],
  "corrections": ["suggested corrections or safer alternative phrasings"],
  "usability_score": "1-10 — how usable is this research for script writing",
  "recommendation": "Brief recommendation for the script writer on how to use this research safely"
}}"""

        try:
            content = self._call_bedrock(prompt)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"❌ Agent 4 (Fact Checker) error: {e}")
            raise

    # ===================================================================
    # AGENT 5: SCRIPT WRITER — Final viral script from all inputs
    # ===================================================================
    def agent_script_writer(self, master_prompt: Dict, research: Dict,
                             fact_check: Dict, trends: Dict,
                             platform: str, duration: str, language: str) -> Dict:
        """
        Agent 5: Write the final viral script using outputs from all other agents.
        This is the master composer that brings everything together.
        """
        prompt = f"""You are the SCRIPT WRITER agent — the final agent in a 5-agent pipeline.
You have received refined inputs from 4 other specialized agents. Your job is to write
the BEST possible viral script using all their outputs.

═══ FROM AGENT 1 (PROMPT REFINER) ═══
Master Prompt: {master_prompt.get('master_prompt', '')}
Content Angle: {master_prompt.get('content_angle', '')}
Key Points: {', '.join(master_prompt.get('key_points', []))}
Target Emotion: {master_prompt.get('target_emotion', '')}
Hook Direction: {master_prompt.get('hook_direction', '')}

═══ FROM AGENT 2 (RESEARCHER) — verified by Agent 4 ═══
{fact_check.get('recommendation', '')}
Verified Facts: {', '.join(fact_check.get('verified_facts', []))}
Research Confidence: {fact_check.get('overall_confidence', 'unknown')}

═══ FROM AGENT 3 (TREND ANALYST) ═══
Trending Angle: {trends.get('trending_angle', '')}
Recommended Format: {trends.get('recommended_format', '')}
Content Style: {trends.get('content_style', '')}
Viral Hooks: {', '.join(trends.get('viral_hooks', []))}
Engagement Strategy: {trends.get('engagement_strategy', '')}

═══ SCRIPT REQUIREMENTS ═══
- Platform: {platform}
- Duration: {duration}
- Language: {language}
- Audience: Indian creators and viewers

RULES:
1. Use the BEST viral hook from Agent 3's suggestions (or create an even better one)
2. Incorporate VERIFIED facts from Agent 2 (avoid flagged claims)
3. Follow the trending angle from Agent 3
4. Match the target emotion from Agent 1
5. If language is Hindi/Hinglish, write naturally in that language
6. Include [TIMESTAMP] markers and [VISUAL] direction notes
7. Make every second count — no filler content
8. The CTA must be specific and actionable

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "hook": "First 2-3 seconds — the viral hook with [VISUAL] cue",
  "main_content": "Main body with [TIMESTAMP] timing cues and [VISUAL] direction notes",
  "cta": "Strong, specific call to action",
  "caption": "Engaging caption with a question to boost comments",
  "hashtags": {json.dumps(trends.get('hashtags', []))},
  "best_posting_time": "{trends.get('best_posting_time', 'Peak hours')}",
  "thumbnail_idea": "Detailed thumbnail/cover description",
  "music_suggestion": "Specific music/audio recommendation",
  "engagement_strategy": "Post-publish engagement tactics"
}}"""

        try:
            content = self._call_bedrock(prompt, max_tokens=3000)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"❌ Agent 5 (Script Writer) error: {e}")
            raise

    # ===================================================================
    # ORCHESTRATOR — Runs the full 5-agent pipeline
    # ===================================================================
    def generate_script(
        self,
        topic: str,
        niche: str,
        platform: str = 'instagram',
        duration: str = '30 seconds',
        language: str = 'English',
        additional_context: str = '',
        progress_callback=None
    ) -> Dict:
        """
        Run the full 5-agent pipeline.

        Args:
            topic: Raw user topic (can be vague)
            niche: Content niche
            platform: Target platform
            duration: Video duration
            language: Script language
            additional_context: Any extra instructions
            progress_callback: Optional callback(agent_name, status, data) for UI updates

        Returns:
            Dict with final script + all agent outputs
        """
        def update(agent, status, data=None):
            if progress_callback:
                progress_callback(agent, status, data)

        result = {
            'raw_topic': topic,
            'niche': niche,
            'platform': platform,
            'agents': {}
        }

        # ── Agent 1: Prompt Refiner ──
        update('Agent 1: Prompt Refiner', 'running')
        master_prompt = self.agent_prompt_refiner(topic, niche, platform, duration, language, additional_context)
        result['agents']['prompt_refiner'] = master_prompt
        update('Agent 1: Prompt Refiner', 'done', master_prompt)

        # ── Agent 2: Researcher (Gemini) ──
        update('Agent 2: Researcher', 'running')
        research = self.agent_researcher(master_prompt)
        result['agents']['researcher'] = research
        update('Agent 2: Researcher', 'done', research)

        # ── Agent 3: Trend Analyst ──
        update('Agent 3: Trend Analyst', 'running')
        trends = self.agent_trend_analyst(master_prompt, niche, platform)
        result['agents']['trend_analyst'] = trends
        update('Agent 3: Trend Analyst', 'done', trends)

        # ── Agent 4: Fact Checker ──
        update('Agent 4: Fact Checker', 'running')
        fact_check = self.agent_fact_checker(research, master_prompt)
        result['agents']['fact_checker'] = fact_check
        update('Agent 4: Fact Checker', 'done', fact_check)

        # ── Agent 5: Script Writer ──
        update('Agent 5: Script Writer', 'running')
        script = self.agent_script_writer(master_prompt, research, fact_check, trends, platform, duration, language)
        result['script'] = script
        result['agents']['script_writer'] = script
        update('Agent 5: Script Writer', 'done', script)

        return result

    # ── Utility methods ──
    def get_available_niches(self) -> List[str]:
        return list(self.TRENDS_DATA.keys())

    def get_available_platforms(self) -> List[str]:
        return list(self.PLATFORM_SPECS.keys())

    def get_niche_info(self, niche: str) -> Optional[Dict]:
        return self.TRENDS_DATA.get(niche.lower())

    def get_platform_info(self, platform: str) -> Optional[Dict]:
        return self.PLATFORM_SPECS.get(platform.lower())


# CLI test
if __name__ == "__main__":
    gen = MultiAgentScriptGenerator()

    print("🚀 Testing 5-Agent Script Generator Pipeline...")
    print("=" * 60)

    result = gen.generate_script(
        topic="AI tools for students",
        niche="tech",
        platform="instagram",
        duration="30 seconds",
        language="Hinglish"
    )

    print(f"\n🧠 Agent 1 — Master Prompt: {result['agents']['prompt_refiner'].get('master_prompt', 'N/A')}")
    print(f"\n🔍 Agent 2 — Research: {result['agents']['researcher'].get('research_summary', 'N/A')[:200]}...")
    print(f"\n📊 Agent 3 — Trending Angle: {result['agents']['trend_analyst'].get('trending_angle', 'N/A')}")
    print(f"\n✅ Agent 4 — Confidence: {result['agents']['fact_checker'].get('overall_confidence', 'N/A')}")
    print(f"\n✍️ Agent 5 — Hook: {result['script'].get('hook', 'N/A')}")
    print("=" * 60)
