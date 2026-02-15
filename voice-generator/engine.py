# voice-generator/engine.py

import boto3
from google.cloud import texttospeech
import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class VoiceGenerator:
    """
    Multi-dialect voice generation for Indian content creators.
    Hybrid architecture:
      - AWS Polly (Neural) for Hindi & Indian English
      - Google Cloud TTS (Wavenet) for regional Indian languages
    """

    # Language configuration with service routing
    LANGUAGE_CONFIG = {
        'hindi': {
            'code': 'hi-IN',
            'service': 'polly',
            'voice_id': 'Kajal',
            'engine': 'neural',
            'display_name': 'हिन्दी (Hindi)',
            'speakers': '600M+',
        },
        'english': {
            'code': 'en-IN',
            'service': 'polly',
            'voice_id': 'Kajal',
            'engine': 'neural',
            'display_name': 'Indian English',
            'speakers': '125M+',
        },
        'tamil': {
            'code': 'ta-IN',
            'service': 'google',
            'voice_name': 'ta-IN-Wavenet-A',
            'display_name': 'தமிழ் (Tamil)',
            'speakers': '75M+',
        },
        'telugu': {
            'code': 'te-IN',
            'service': 'google',
            'voice_name': 'te-IN-Standard-A',
            'display_name': 'తెలుగు (Telugu)',
            'speakers': '83M+',
        },
        'bengali': {
            'code': 'bn-IN',
            'service': 'google',
            'voice_name': 'bn-IN-Wavenet-A',
            'display_name': 'বাংলা (Bengali)',
            'speakers': '100M+',
        },
        'marathi': {
            'code': 'mr-IN',
            'service': 'google',
            'voice_name': 'mr-IN-Wavenet-A',
            'display_name': 'मराठी (Marathi)',
            'speakers': '83M+',
        },
        'gujarati': {
            'code': 'gu-IN',
            'service': 'google',
            'voice_name': 'gu-IN-Wavenet-A',
            'display_name': 'ગુજરાતી (Gujarati)',
            'speakers': '55M+',
        },
        'kannada': {
            'code': 'kn-IN',
            'service': 'google',
            'voice_name': 'kn-IN-Wavenet-A',
            'display_name': 'ಕನ್ನಡ (Kannada)',
            'speakers': '44M+',
        },
        'malayalam': {
            'code': 'ml-IN',
            'service': 'google',
            'voice_name': 'ml-IN-Wavenet-A',
            'display_name': 'മലയാളം (Malayalam)',
            'speakers': '38M+',
        },
    }

    # Mood-based voice settings (applied to Google TTS; Polly uses SSML)
    MOOD_SETTINGS = {
        'exciting': {
            'rate': 1.15,
            'pitch': 5.0,
            'volume': 3.0,
            'description': '🎉 High energy, upbeat delivery',
            'polly_ssml_rate': '110%',
        },
        'mysterious': {
            'rate': 0.85,
            'pitch': -8.0,
            'volume': -2.0,
            'description': '🌙 Low, suspenseful, slow-paced',
            'polly_ssml_rate': '85%',
        },
        'educational': {
            'rate': 0.95,
            'pitch': 0.0,
            'volume': 0.0,
            'description': '📚 Clear, measured, easy to follow',
            'polly_ssml_rate': '95%',
        },
        'casual': {
            'rate': 1.05,
            'pitch': 2.0,
            'volume': 0.0,
            'description': '😊 Relaxed, conversational, natural',
            'polly_ssml_rate': '105%',
        },
        'dramatic': {
            'rate': 0.88,
            'pitch': -5.0,
            'volume': 2.0,
            'description': '🎭 Intense, powerful, commanding',
            'polly_ssml_rate': '88%',
        },
        'upbeat': {
            'rate': 1.2,
            'pitch': 8.0,
            'volume': 4.0,
            'description': '⚡ Fast, cheerful, energetic',
            'polly_ssml_rate': '120%',
        },
    }

    def __init__(self):
        """Initialize AWS Polly and Google TTS clients"""
        # AWS Polly
        self.polly = boto3.client(
            'polly',
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )

        # Google Cloud TTS
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '../credentials/google-tts-key.json')
        # Resolve relative path
        if not os.path.isabs(creds_path):
            creds_path = os.path.join(os.path.dirname(__file__), '..', creds_path)
        creds_path = os.path.abspath(creds_path)

        self.google_tts = None
        if os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
            self.google_tts = texttospeech.TextToSpeechClient()
            print(f"✅ Google TTS initialized (creds: {creds_path})")
        else:
            print(f"⚠️ Google credentials not found at {creds_path} — regional languages will be unavailable")

    def generate_voiceover(
        self,
        text: str,
        language: str = 'hindi',
        mood: str = 'casual',
    ) -> bytes:
        """
        Generate voiceover audio in the specified language and mood.

        Args:
            text: Script text to convert to speech
            language: Language key (hindi, tamil, etc.)
            mood: Voice mood (exciting, mysterious, etc.)

        Returns:
            MP3 audio data as bytes
        """
        if language not in self.LANGUAGE_CONFIG:
            raise ValueError(f"Language '{language}' not supported. Available: {list(self.LANGUAGE_CONFIG.keys())}")
        if mood not in self.MOOD_SETTINGS:
            raise ValueError(f"Mood '{mood}' not supported. Available: {list(self.MOOD_SETTINGS.keys())}")

        lang_config = self.LANGUAGE_CONFIG[language]

        if lang_config['service'] == 'polly':
            return self._generate_polly(text, lang_config, mood)
        else:
            return self._generate_google(text, lang_config, mood)

    def _generate_polly(self, text: str, lang_config: Dict, mood: str) -> bytes:
        """Generate voice using AWS Polly (Neural) with SSML for mood"""
        mood_settings = self.MOOD_SETTINGS[mood]

        # Wrap in SSML for mood control via prosody
        ssml_text = f"""<speak>
    <prosody rate="{mood_settings['polly_ssml_rate']}">
        {text}
    </prosody>
</speak>"""

        try:
            response = self.polly.synthesize_speech(
                Text=ssml_text,
                TextType='ssml',
                VoiceId=lang_config['voice_id'],
                LanguageCode=lang_config['code'],
                Engine=lang_config['engine'],
                OutputFormat='mp3'
            )

            audio = response['AudioStream'].read()
            print(f"✅ Generated {lang_config['display_name']} voice via AWS Polly ({mood} mood)")
            return audio

        except Exception as e:
            print(f"❌ Polly error: {e}")
            raise

    def _generate_google(self, text: str, lang_config: Dict, mood: str) -> bytes:
        """Generate voice using Google Cloud TTS (Wavenet) with mood settings"""
        if not self.google_tts:
            raise RuntimeError(
                "Google TTS not initialized. Check GOOGLE_APPLICATION_CREDENTIALS in .env"
            )

        mood_settings = self.MOOD_SETTINGS[mood]

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_config['code'],
            name=lang_config['voice_name']
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=mood_settings['rate'],
            pitch=mood_settings['pitch'],
            volume_gain_db=mood_settings['volume']
        )

        try:
            response = self.google_tts.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            print(f"✅ Generated {lang_config['display_name']} voice via Google TTS ({mood} mood)")
            return response.audio_content

        except Exception as e:
            print(f"❌ Google TTS error: {e}")
            raise

    def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages for UI"""
        return [
            {
                'key': key,
                'name': config['display_name'],
                'speakers': config['speakers'],
                'service': 'AWS Polly' if config['service'] == 'polly' else 'Google Cloud TTS',
            }
            for key, config in self.LANGUAGE_CONFIG.items()
        ]

    def get_supported_moods(self) -> List[Dict]:
        """Get list of supported moods for UI"""
        return [
            {'key': key, 'description': config['description']}
            for key, config in self.MOOD_SETTINGS.items()
        ]


# CLI test
if __name__ == "__main__":
    gen = VoiceGenerator()

    print("\n🎤 Testing Voice Generator...")
    print("=" * 50)

    # Test Hindi (Polly)
    hindi_text = "नमस्ते! आज हम बात करेंगे भारत के सबसे लोकप्रिय स्ट्रीट फूड के बारे में।"
    audio = gen.generate_voiceover(hindi_text, language='hindi', mood='exciting')

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'test_hindi_voice.mp3'), 'wb') as f:
        f.write(audio)
    print(f"💾 Hindi audio saved ({len(audio)} bytes)")

    # Test Tamil (Google)
    tamil_text = "வணக்கம்! இன்று நாம் இந்தியாவின் சிறந்த தெரு உணவுகளைப் பற்றி பேசுவோம்."
    try:
        audio = gen.generate_voiceover(tamil_text, language='tamil', mood='casual')
        with open(os.path.join(output_dir, 'test_tamil_voice.mp3'), 'wb') as f:
            f.write(audio)
        print(f"💾 Tamil audio saved ({len(audio)} bytes)")
    except Exception as e:
        print(f"⚠️ Tamil test skipped: {e}")

    print("=" * 50)
