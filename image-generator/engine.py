# image-generator/engine.py

import boto3
import json
import os
import base64
from dotenv import load_dotenv
from typing import Dict, Optional
from datetime import datetime

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class ImageGenerator:
    """
    Dual-Agent Cover Page / Thumbnail Generator.
    
    Agent 1 (Prompt Refiner): Uses Bedrock Claude to transform a basic user prompt
    into an optimized image generation prompt with specific details.
    
    Agent 2 (Image Generator): Uses Amazon Titan Image Generator to create the image
    from the refined prompt.
    """

    STYLE_PRESETS = {
        'modern': {
            'description': 'Clean, contemporary design with bold typography and vibrant gradients',
            'keywords': 'modern, minimal, gradient background, bold text, clean layout, professional',
        },
        'minimalist': {
            'description': 'Simple, elegant design with lots of whitespace',
            'keywords': 'minimalist, whitespace, simple, elegant, clean, subtle colors',
        },
        'bold': {
            'description': 'Eye-catching with strong colors and large text',
            'keywords': 'bold, vibrant colors, large text, eye-catching, dramatic, high contrast',
        },
        'cinematic': {
            'description': 'Movie-poster style with dramatic lighting',
            'keywords': 'cinematic, dramatic lighting, movie poster, film grain, moody, atmospheric',
        },
        'neon': {
            'description': 'Neon glow effects on dark background',
            'keywords': 'neon, glow, dark background, cyberpunk, futuristic, electric colors',
        },
        'vintage': {
            'description': 'Retro aesthetic with warm tones',
            'keywords': 'vintage, retro, warm tones, film grain, nostalgic, classic',
        },
        'indian': {
            'description': 'Incorporating Indian cultural elements and colors',
            'keywords': 'Indian, desi, rangoli patterns, saffron, cultural, vibrant, traditional motifs',
        },
    }

    def __init__(self):
        """Initialize Bedrock clients for both agents"""
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
        )
        self.claude_model = os.getenv('BEDROCK_MODEL_CLAUDE', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        self.titan_model = os.getenv('BEDROCK_MODEL_TITAN_IMAGE', 'amazon.titan-image-generator-v1')

    def _invoke_claude(self, prompt: str) -> str:
        """Agent 1: Call Bedrock model for prompt refinement (Converse API)"""
        response = self.bedrock.converse(
            modelId=self.claude_model,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1024,
                "temperature": 0.7,
            }
        )

        return response['output']['message']['content'][0]['text']

    def _invoke_titan(self, prompt: str, negative_prompt: str = '', width: int = 1024, height: int = 1024) -> bytes:
        """Agent 2: Call Titan Image Generator"""
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                **({"negativeText": negative_prompt} if negative_prompt else {})
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "width": width,
                "height": height,
                "cfgScale": 8.0,
            }
        })

        response = self.bedrock.invoke_model(
            modelId=self.titan_model,
            contentType='application/json',
            accept='application/json',
            body=body
        )

        result = json.loads(response['body'].read())
        image_b64 = result['images'][0]
        return base64.b64decode(image_b64)

    def refine_prompt(self, raw_prompt: str, style: str = 'modern') -> Dict:
        """
        Agent 1: Refine a basic user prompt into an optimized image generation prompt.

        Args:
            raw_prompt: Basic user description of what they want
            style: Visual style preset

        Returns:
            Dict with refined_prompt, negative_prompt, and reasoning
        """
        style_info = self.STYLE_PRESETS.get(style, self.STYLE_PRESETS['modern'])

        prompt = f"""You are an expert prompt engineer specializing in AI image generation.

TASK: Refine the following basic prompt into an optimized, detailed prompt for Amazon Titan Image Generator.

USER'S BASIC PROMPT: "{raw_prompt}"

DESIRED STYLE: {style} — {style_info['description']}
STYLE KEYWORDS: {style_info['keywords']}

CONTEXT: This image is for a social media content creator's thumbnail or cover page.
It should be scroll-stopping and visually stunning.

RULES:
1. Add specific visual details: colors, composition, lighting, perspective
2. Include artistic style references
3. Specify quality modifiers (high quality, detailed, professional)
4. Include the style keywords naturally
5. Keep the prompt under 200 words but highly descriptive
6. Do NOT include any text/words in the image prompt (Titan struggles with text)
7. Focus on visual elements that make great thumbnails

OUTPUT ONLY VALID JSON (no markdown, no code fences):
{{
  "refined_prompt": "The optimized, detailed image generation prompt",
  "negative_prompt": "Things to avoid in the image (blurry, low quality, text, watermark, etc.)",
  "reasoning": "Brief explanation of what you improved and why"
}}"""

        try:
            content = self._invoke_claude(prompt)

            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            return json.loads(content)

        except Exception as e:
            print(f"❌ Prompt refinement error: {e}")
            raise

    def generate_image(
        self,
        raw_prompt: str,
        style: str = 'modern',
        width: int = 1024,
        height: int = 1024,
        auto_refine: bool = True
    ) -> Dict:
        """
        Full dual-agent pipeline: Refine prompt → Generate image.

        Args:
            raw_prompt: Basic user description
            style: Visual style preset
            width: Image width
            height: Image height
            auto_refine: Whether to use Agent 1 for prompt refinement

        Returns:
            Dict with image_bytes, raw_prompt, refined_prompt, and metadata
        """
        result = {
            'raw_prompt': raw_prompt,
            'style': style,
            'width': width,
            'height': height,
        }

        # Agent 1: Refine the prompt
        if auto_refine:
            print("🤖 Agent 1: Refining prompt...")
            refinement = self.refine_prompt(raw_prompt, style)
            refined_prompt = refinement['refined_prompt']
            negative_prompt = refinement.get('negative_prompt', '')
            result['refined_prompt'] = refined_prompt
            result['negative_prompt'] = negative_prompt
            result['refinement_reasoning'] = refinement.get('reasoning', '')
        else:
            refined_prompt = raw_prompt
            negative_prompt = 'blurry, low quality, watermark, text, words, letters'
            result['refined_prompt'] = raw_prompt
            result['negative_prompt'] = negative_prompt

        # Agent 2: Generate the image
        print("🎨 Agent 2: Generating image with Titan...")
        image_bytes = self._invoke_titan(refined_prompt, negative_prompt, width, height)
        result['image_bytes'] = image_bytes
        result['image_size'] = len(image_bytes)

        print(f"✅ Image generated! ({len(image_bytes):,} bytes)")
        return result

    def save_image(self, image_bytes: bytes, filename: str = None) -> str:
        """Save generated image to outputs directory"""
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(output_dir, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cover_{timestamp}.png"

        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        print(f"💾 Image saved: {filepath}")
        return filepath

    def get_style_presets(self) -> Dict:
        """Get available style presets for UI"""
        return self.STYLE_PRESETS

    def get_size_options(self) -> list:
        """Get available image size options"""
        return [
            {'label': 'Square (1024×1024)', 'width': 1024, 'height': 1024},
            {'label': 'Landscape (1280×768)', 'width': 1280, 'height': 768},
            {'label': 'Portrait (768×1280)', 'width': 768, 'height': 1280},
            {'label': 'YouTube Thumbnail (1280×720)', 'width': 1280, 'height': 720},
            {'label': 'Instagram Post (1080×1080)', 'width': 1024, 'height': 1024},
            {'label': 'Instagram Story (1080×1920)', 'width': 768, 'height': 1280},
        ]


# CLI test
if __name__ == "__main__":
    gen = ImageGenerator()

    print("🎨 Testing Dual-Agent Image Generator...")
    print("=" * 50)

    result = gen.generate_image(
        raw_prompt="A tech tutorial cover page about learning Python programming",
        style="modern"
    )

    print(f"\n📝 Raw Prompt: {result['raw_prompt']}")
    print(f"\n✨ Refined Prompt: {result['refined_prompt']}")
    print(f"\n🚫 Negative Prompt: {result['negative_prompt']}")
    print(f"\n💡 Reasoning: {result.get('refinement_reasoning', 'N/A')}")
    print(f"\n📦 Image Size: {result['image_size']:,} bytes")

    filepath = gen.save_image(result['image_bytes'])
    print(f"\n💾 Saved to: {filepath}")
    print("=" * 50)
