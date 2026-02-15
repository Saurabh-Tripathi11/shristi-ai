# content-repurposer/engine.py

import boto3
import json
import os
from dotenv import load_dotenv
from typing import Dict

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class ContentRepurposer:
    """
    Repurpose long-form content into platform-optimized short-form pieces.
    Uses Amazon Bedrock (Claude 3.5 Sonnet) for intelligent content transformation.
    
    One script → Instagram Carousel + Twitter Thread + LinkedIn Post + YouTube Shorts Script
    """

    PLATFORM_FORMATS = {
        'instagram_carousel': {
            'name': 'Instagram Carousel',
            'icon': '📸',
            'description': '5-8 slide text cards with hook on slide 1, value in middle, CTA on last slide',
            'constraints': 'Each slide: max 100 words. Use emojis. Slide 1 = bold hook. Last slide = CTA.',
        },
        'twitter_thread': {
            'name': 'Twitter/X Thread',
            'icon': '🐦',
            'description': 'Numbered tweet thread (5-10 tweets)',
            'constraints': 'Each tweet: max 280 characters. Tweet 1 = hook. Use numbering (1/, 2/, etc.). Last tweet = CTA + retweet ask.',
        },
        'linkedin_post': {
            'name': 'LinkedIn Post',
            'icon': '💼',
            'description': 'Professional long-form post with formatting',
            'constraints': 'Max 1300 characters. Professional tone. Use line breaks for readability. Start with a bold statement. Include 3-5 relevant hashtags at end.',
        },
        'youtube_shorts': {
            'name': 'YouTube Shorts Script',
            'icon': '🎬',
            'description': '30-60 second video script with timing cues',
            'constraints': 'Max 60 seconds. Include [TIMESTAMP] markers. Hook in first 3 sec. Visual direction notes in [VISUAL]. End with subscribe CTA.',
        },
    }

    def __init__(self):
        """Initialize Bedrock client"""
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_CLAUDE', 'anthropic.claude-3-5-sonnet-20241022-v2:0')

    def _invoke_bedrock(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call Bedrock model using Converse API (model-agnostic)"""
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

    def repurpose_content(
        self,
        long_form_content: str,
        target_audience: str = 'Indian audience',
        language: str = 'English',
        niche: str = '',
    ) -> Dict:
        """
        Transform long-form content into multiple platform-specific formats.

        Args:
            long_form_content: The original long-form content (article, blog, script, etc.)
            target_audience: Who the content is for
            language: Output language
            niche: Content niche for better optimization

        Returns:
            Dict with repurposed content for each platform
        """
        platforms_info = ""
        for key, spec in self.PLATFORM_FORMATS.items():
            platforms_info += f"""
{spec['icon']} {spec['name']} ({key}):
- Format: {spec['description']}
- Constraints: {spec['constraints']}
"""

        prompt = f"""You are an expert social media content strategist for Indian creators.

TASK: Take the following long-form content and repurpose it into 4 platform-optimized short-form pieces.

ORIGINAL CONTENT:
---
{long_form_content}
---

TARGET AUDIENCE: {target_audience}
LANGUAGE: {language}
{f'NICHE: {niche}' if niche else ''}

PLATFORM SPECIFICATIONS:
{platforms_info}

RULES:
1. Each format must be complete and ready to post — not a summary
2. Tailor the tone and style for each platform's culture
3. Preserve the core message but adapt the delivery
4. For Indian audience, use culturally relevant references where appropriate
5. If language is Hindi/Hinglish, write naturally in that language
6. Each piece should be independently valuable (someone shouldn't need the original to understand)
7. The Instagram carousel should have clear slide separations
8. The Twitter thread should have proper numbering
9. The LinkedIn post should maintain professional credibility
10. The YouTube Shorts script should have real timing and visual cues

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "instagram_carousel": {{
    "slides": ["Slide 1 text", "Slide 2 text", "..."],
    "caption": "Caption to accompany the carousel",
    "hashtags": ["hashtag1", "hashtag2"]
  }},
  "twitter_thread": {{
    "tweets": ["1/ Tweet one text", "2/ Tweet two text", "..."],
    "hashtags": ["hashtag1", "hashtag2"]
  }},
  "linkedin_post": {{
    "post_text": "Full LinkedIn post text with formatting",
    "hashtags": ["hashtag1", "hashtag2"]
  }},
  "youtube_shorts": {{
    "script": "Full script with [00:00] timestamps and [VISUAL] cues",
    "title": "Short attention-grabbing title",
    "description": "Video description",
    "hashtags": ["hashtag1", "hashtag2"]
  }},
  "content_summary": "One-line summary of the original content",
  "best_platform": "Which platform this content would perform best on and why"
}}"""

        try:
            content = self._invoke_bedrock(prompt, max_tokens=4096)

            # Clean JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            raise
        except Exception as e:
            print(f"❌ Bedrock error: {str(e)}")
            raise

    def get_platform_formats(self) -> Dict:
        """Get platform format specs for UI"""
        return self.PLATFORM_FORMATS


# CLI test
if __name__ == "__main__":
    repurposer = ContentRepurposer()

    test_content = """
    Artificial Intelligence is transforming how Indian content creators work. From automated video editing 
    to AI-generated scripts, the tools available today can save creators hours of work every week. 
    In India, where content creation is becoming a viable career for millions, these AI tools are 
    particularly impactful. Creators who adopt AI tools early are seeing 3x growth in their output 
    while maintaining quality. The key areas where AI helps most are: script writing, thumbnail design, 
    analytics prediction, and audience engagement. However, the challenge remains in making these tools 
    accessible in regional Indian languages and affordable for small creators.
    """

    print("🔄 Testing Content Repurposer...")
    print("=" * 50)

    result = repurposer.repurpose_content(
        long_form_content=test_content,
        target_audience="Indian content creators aged 18-35",
        niche="tech"
    )

    print(f"\n📝 Summary: {result.get('content_summary', 'N/A')}")
    print(f"\n🏆 Best Platform: {result.get('best_platform', 'N/A')}")
    print(f"\n📸 IG Carousel Slides: {len(result.get('instagram_carousel', {}).get('slides', []))}")
    print(f"\n🐦 Twitter Thread Tweets: {len(result.get('twitter_thread', {}).get('tweets', []))}")
    print("=" * 50)
