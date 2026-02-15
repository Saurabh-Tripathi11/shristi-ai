# backend/script_generator.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
from typing import Dict, List

# Load environment variables
load_dotenv()

class ScriptGenerator:
    """Generate viral scripts using Google Gemini (new SDK)"""
    
    # Curated trend data
    TRENDS_DATA = {
        'food': {
            'trending_topics': ['Indian street food', 'regional cuisine', 'food festivals', 'homemade recipes'],
            'hashtags': ['#streetfood', '#indianfood', '#foodie', '#foodreels'],
            'optimal_format': 'Reels 15-30 seconds',
            'best_time': '7-9 PM IST',
            'engagement_tip': 'Start with sizzling shot, show final product at 3 sec mark'
        },
        'tech': {
            'trending_topics': ['AI tools', 'coding tutorials', 'gadget reviews', 'career tips'],
            'hashtags': ['#coding', '#tech', '#ai', '#learntocode'],
            'optimal_format': 'Carousel or 60-sec video',
            'best_time': '9-11 AM IST',
            'engagement_tip': 'Problem-solution hook, show screen recording'
        },
        'fitness': {
            'trending_topics': ['home workouts', 'nutrition', 'transformation stories', 'yoga'],
            'hashtags': ['#fitness', '#homeworkout', '#wellness', '#fitindia'],
            'optimal_format': '15-45 sec transformation video',
            'best_time': '6-8 AM IST',
            'engagement_tip': 'Before/after hook, motivational music'
        },
        'education': {
            'trending_topics': ['study tips', 'exam preparation', 'skill learning', 'career guidance'],
            'hashtags': ['#education', '#studytips', '#learning', '#students'],
            'optimal_format': 'Carousel or 60-sec explainer',
            'best_time': '4-6 PM IST',
            'engagement_tip': 'Start with relatable problem'
        },
        'business': {
            'trending_topics': ['startup stories', 'side hustles', 'marketing tips', 'entrepreneurship'],
            'hashtags': ['#business', '#startup', '#entrepreneur', '#sidehustle'],
            'optimal_format': '30-60 sec talking head',
            'best_time': '10 AM - 12 PM IST',
            'engagement_tip': 'Share specific numbers/results'
        }
    }
    
    PLATFORM_SPECS = {
        'instagram': {
            'optimal_caption': '125-150 characters',
            'hashtag_count': '5-8',
            'video_length': '15-60 seconds',
            'tone': 'casual, emoji-friendly'
        },
        'youtube': {
            'optimal_caption': '200-300 characters',
            'hashtag_count': '3-5',
            'video_length': '8-15 minutes for long-form, 30-60 sec for Shorts',
            'tone': 'informative, engaging'
        },
        'linkedin': {
            'optimal_caption': '150-200 characters',
            'hashtag_count': '3-5',
            'video_length': '30-90 seconds',
            'tone': 'professional, value-driven'
        },
        'twitter': {
            'optimal_caption': '200-250 characters',
            'hashtag_count': '1-2',
            'video_length': '15-45 seconds',
            'tone': 'punchy, conversational'
        }
    }
    
    def __init__(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_script(
        self,
        topic: str,
        niche: str,
        platform: str = 'instagram',
        duration: str = '30 seconds'
    ) -> Dict:
        """Generate viral script with captions and hashtags"""
        
        trends = self.TRENDS_DATA.get(niche.lower(), self.TRENDS_DATA['food'])
        platform_spec = self.PLATFORM_SPECS.get(platform.lower(), self.PLATFORM_SPECS['instagram'])
        
        prompt = f"""You are an expert content creator for Indian social media.

TASK: Create a viral {platform} script about: {topic}

CONTEXT:
- Niche: {niche}
- Platform: {platform}
- Duration: {duration}
- Target audience: Indian creators and viewers

CURRENT TRENDS IN {niche.upper()}:
- Trending topics: {', '.join(trends['trending_topics'])}
- Trending hashtags: {', '.join(trends['hashtags'])}
- Optimal format: {trends['optimal_format']}
- Best posting time: {trends['best_time']}
- Engagement tip: {trends['engagement_tip']}

PLATFORM REQUIREMENTS:
- Video length: {platform_spec['video_length']}
- Caption length: {platform_spec['optimal_caption']} characters
- Hashtag count: {platform_spec['hashtag_count']}
- Tone: {platform_spec['tone']}

OUTPUT ONLY VALID JSON (no markdown, no explanation):
{{
  "hook": "First 3 seconds - attention grabber",
  "main_content": "Main body of script with timing cues",
  "cta": "Call to action at end",
  "caption": "Engaging caption (with question to boost comments)",
  "hashtags": ["list", "of", "hashtags"],
  "best_posting_time": "optimal time to post",
  "thumbnail_idea": "description for thumbnail"
}}

Generate ONLY the JSON, nothing else:"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            content = response.text.strip()
            
            # Clean JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            
            print(f"✅ Generated script for {niche} on {platform}")
            return result
            
        except Exception as e:
            print(f"❌ Gemini error: {str(e)}")
            raise
    
    def get_available_niches(self) -> List[str]:
        return list(self.TRENDS_DATA.keys())
    
    def get_available_platforms(self) -> List[str]:
        return list(self.PLATFORM_SPECS.keys())


# Test
if __name__ == "__main__":
    generator = ScriptGenerator()
    
    print("Testing script generation with NEW Gemini SDK...")
    
    script = generator.generate_script(
        topic="Best street food in Mumbai",
        niche="food",
        platform="instagram",
        duration="30 seconds"
    )
    
    print("\n" + "="*50)
    print("GENERATED SCRIPT:")
    print("="*50)
    print(f"\n🎬 HOOK:\n{script['hook']}")
    print(f"\n📝 MAIN CONTENT:\n{script['main_content']}")
    print(f"\n📢 CTA:\n{script['cta']}")
    print(f"\n✍️ CAPTION:\n{script['caption']}")
    print(f"\n🏷️ HASHTAGS:\n{' '.join(script['hashtags'])}")
    print(f"\n⏰ BEST TIME:\n{script['best_posting_time']}")
    print(f"\n🖼️ THUMBNAIL:\n{script['thumbnail_idea']}")
    print("\n" + "="*50)
