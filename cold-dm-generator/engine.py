# cold-dm-generator/engine.py

import boto3
import json
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from google import genai

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class ColdDMGenerator:
    """Generate personalized Cold DMs for brand outreach using Amazon Bedrock + Gemini for research"""

    def __init__(self):
        """Initialize Bedrock and Gemini clients"""
        # Amazon Bedrock for DM generation
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
        )
        self.model_id = os.getenv('BEDROCK_MODEL_CLAUDE', 'anthropic.claude-3-5-sonnet-20241022-v2:0')

        # Gemini for brand research (web grounding)
        gemini_key = os.getenv('GEMINI_API_KEY')
        self.gemini_client = None
        if gemini_key:
            self.gemini_client = genai.Client(api_key=gemini_key)

    def research_brand(self, brand_name: str, platform: str = '') -> str:
        """
        Use Gemini with web search grounding to research a brand's recent activity.

        Args:
            brand_name: Name of the brand to research
            platform: Platform context (instagram, linkedin, etc.)

        Returns:
            Research summary string
        """
        if not self.gemini_client:
            return f"Brand: {brand_name} (auto-research unavailable — Gemini API key not set)"

        prompt = f"""Research the brand "{brand_name}" and provide:
1. Their most recent product launch or campaign (last 3 months)
2. One specific feature or aspect of their latest product/campaign that stands out
3. Their target demographic
4. Their social media presence, especially on {platform if platform else 'social media'}

Keep it factual, concise, and specific. Max 150 words."""

        try:
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
            print(f"⚠️ Gemini research error: {e}")
            return f"Brand: {brand_name} (research unavailable)"

    def _invoke_bedrock(self, prompt: str) -> str:
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
                "maxTokens": 2048,
                "temperature": 0.7,
            }
        )

        return response['output']['message']['content'][0]['text']

    def generate_cold_dm(
        self,
        creator_name: str,
        creator_niche: str,
        audience_size: str,
        audience_demographic: str,
        brand_name: str,
        platform: str = 'instagram',
        content_idea: str = '',
        tone: str = 'professional yet friendly',
        auto_research: bool = True
    ) -> Dict:
        """
        Generate a personalized Cold DM for brand outreach.

        Args:
            creator_name: The creator's name
            creator_niche: Creator's content niche
            audience_size: Follower/subscriber count
            audience_demographic: Who the audience is
            brand_name: Target brand name
            platform: Where the DM will be sent
            content_idea: Optional specific content idea
            tone: DM tone preference
            auto_research: Whether to auto-research the brand via Gemini

        Returns:
            Dict with DM components and full message
        """
        # Step 1: Research the brand (if enabled)
        brand_research = ""
        if auto_research:
            brand_research = self.research_brand(brand_name, platform)

        # Step 2: Generate DM via Bedrock
        prompt = f"""You are an expert social media marketing consultant who helps Indian content creators 
land brand deals through compelling cold DMs.

TASK: Write a personalized cold DM from a content creator to a brand.

CREATOR PROFILE:
- Name: {creator_name}
- Niche: {creator_niche}
- Audience size: {audience_size}
- Audience demographic: {audience_demographic}
- Platform: {platform}

TARGET BRAND: {brand_name}

BRAND RESEARCH (use this info to personalize):
{brand_research if brand_research else 'No research available — make generic but professional references'}

{f'CONTENT IDEA FROM CREATOR: {content_idea}' if content_idea else ''}

DESIRED TONE: {tone}

DM STRUCTURE (follow this exact 4-part format):

1. THE HOOK (Personalized & Specific):
"Hey [Brand Name] team! Loved your recent [specific thing from research]. The way you [specific detail] was brilliant."

2. THE VALUE PROPOSITION (Data & Demographic):
Introduce yourself, your niche, audience size, and why your audience aligns with the brand.

3. THE PITCH (The Idea):
A specific content idea integrating the brand's product. Be creative and concrete.

4. THE CALL TO ACTION (Low Friction):
End with a simple, low-commitment ask. Not "let's do a deal" but "who should I send a quick proposal to?"

RULES:
- Keep total DM under 200 words (people don't read long DMs)
- Be specific, not generic — reference real things about the brand
- Sound human and genuine, not templated
- Include 1-2 relevant metrics/numbers
- The tone should match {platform} culture
- For Indian brands, mix English naturally (no forced formality)

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "hook": "The personalized opening line",
  "value_proposition": "Who you are and why they should care",
  "pitch": "The specific content collaboration idea",
  "cta": "The low-friction call to action",
  "full_dm": "The complete DM message ready to copy-paste",
  "subject_line": "If this is an email, a compelling subject line",
  "follow_up": "A suggested follow-up message if they don't respond in 3 days",
  "tips": "2-3 tips for maximizing response rate"
}}"""

        try:
            content = self._invoke_bedrock(prompt)

            # Clean JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            result = json.loads(content)
            result['brand_research'] = brand_research
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            raise
        except Exception as e:
            print(f"❌ Bedrock error: {str(e)}")
            raise


# CLI test
if __name__ == "__main__":
    generator = ColdDMGenerator()

    print("🚀 Testing Cold DM Generator...")
    print("=" * 50)

    result = generator.generate_cold_dm(
        creator_name="Anvesh",
        creator_niche="Tech & AI",
        audience_size="50K followers",
        audience_demographic="Indian developers, CS students, tech enthusiasts aged 18-30",
        brand_name="boAt",
        platform="instagram",
        content_idea="Unboxing + coding setup tour featuring their latest earbuds"
    )

    print(f"\n📨 FULL DM:\n{result.get('full_dm', 'N/A')}")
    print(f"\n📧 SUBJECT LINE:\n{result.get('subject_line', 'N/A')}")
    print(f"\n🔁 FOLLOW UP:\n{result.get('follow_up', 'N/A')}")
    print(f"\n💡 TIPS:\n{result.get('tips', 'N/A')}")
    print("=" * 50)
