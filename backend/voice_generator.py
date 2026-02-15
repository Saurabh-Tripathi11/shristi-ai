# backend/voice_generator.py

import boto3
from google.cloud import texttospeech
import os
from typing import Dict, Optional
import json

class BharatVoiceGenerator:
    """
    Multi-dialect voice generation system for Indian content creators
    Uses AWS Polly for Hindi/English and Google TTS for regional languages
    """
    
    # Language configuration
    LANGUAGE_CONFIG = {
        'hindi': {
            'code': 'hi-IN',
            'service': 'polly',
            'voice': 'Aditi',
            'engine': None,
            'display_name': 'हिन्दी (Hindi)',
            'speakers': '500M+',
        },
        'english_indian': {
            'code': 'en-IN',
            'service': 'polly',
            'voice': 'Raveena',
            'engine': None,
            'display_name': 'Indian English',
            'speakers': '125M+',
        },
        'tamil': {
            'code': 'ta-IN',
            'service': 'google',
            'voice': 'ta-IN-Standard-A',
            'display_name': 'தமிழ் (Tamil)',
            'speakers': '70M+',
        },
        'telugu': {
            'code': 'te-IN',
            'service': 'google',
            'voice': 'te-IN-Standard-A',
            'display_name': 'తెలుగు (Telugu)',
            'speakers': '80M+',
        },
        'bengali': {
            'code': 'bn-IN',
            'service': 'google',
            'voice': 'bn-IN-Standard-A',
            'display_name': 'বাংলা (Bengali)',
            'speakers': '100M+',
        },
        'marathi': {
            'code': 'mr-IN',
            'service': 'google',
            'voice': 'mr-IN-Standard-A',
            'display_name': 'मराठी (Marathi)',
            'speakers': '80M+',
        },
        'gujarati': {
            'code': 'gu-IN',
            'service': 'google',
            'voice': 'gu-IN-Standard-A',
            'display_name': 'ગુજરાતી (Gujarati)',
            'speakers': '55M+',
        }
    }
    
    # Mood-based voice settings
    MOOD_SETTINGS = {
        'exciting': {
            'rate': 1.1,
            'pitch': 5.0,
            'volume': 3.0,
        },
        'mysterious': {
            'rate': 0.85,
            'pitch': -10.0,
            'volume': -2.0,
        },
        'educational': {
            'rate': 1.0,
            'pitch': 0.0,
            'volume': 0.0,
        },
        'casual': {
            'rate': 1.05,
            'pitch': 2.0,
            'volume': 0.0,
        },
        'dramatic': {
            'rate': 0.9,
            'pitch': -5.0,
            'volume': 2.0,
        },
        'upbeat': {
            'rate': 1.15,
            'pitch': 8.0,
            'volume': 4.0,
        }
    }
    
    def __init__(self):
        """Initialize AWS Polly and Google TTS clients"""
        # AWS Polly client
        self.polly_client = boto3.client('polly', region_name='ap-south-1')
        
        # Google TTS client
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '../credentials/google-tts-key.json')
        if os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            self.google_client = texttospeech.TextToSpeechClient()
        else:
            print(f"Warning: Google credentials not found at {credentials_path}")
            self.google_client = None
    
    def generate_voiceover(
        self, 
        text: str, 
        language: str = 'hindi',
        mood: str = 'casual',
    ) -> bytes:
        """
        Generate voice-over in specified language and mood
        
        Args:
            text: Script text to convert to speech
            language: Language code (hindi, tamil, etc.)
            mood: Voice mood (exciting, mysterious, etc.)
            
        Returns:
            Audio data as bytes
        """
        if language not in self.LANGUAGE_CONFIG:
            raise ValueError(f"Language '{language}' not supported")
        
        if mood not in self.MOOD_SETTINGS:
            raise ValueError(f"Mood '{mood}' not supported")
        
        lang_config = self.LANGUAGE_CONFIG[language]
        
        # Route to appropriate service
        if lang_config['service'] == 'polly':
            audio_data = self._generate_polly_voice(text, lang_config, mood)
        elif lang_config['service'] == 'google':
            audio_data = self._generate_google_voice(text, lang_config, mood)
        else:
            raise ValueError(f"Unknown service: {lang_config['service']}")
        
        return audio_data
    
    def _generate_polly_voice(self, text: str, lang_config: Dict, mood: str) -> bytes:
        """Generate voice using AWS Polly"""
        try:
            # Build parameters dictionary
            params = {
                'Text': text,
                'VoiceId': lang_config['voice'],
                'LanguageCode': lang_config['code'],
                'OutputFormat': 'mp3'
            }
            
            # Only add Engine parameter if it's specified and not None
            if lang_config.get('engine') is not None:
                params['Engine'] = lang_config['engine']
            
            # Call Polly
            response = self.polly_client.synthesize_speech(**params)
            
            # Read audio data
            audio_data = response['AudioStream'].read()
            print(f"✅ Generated {lang_config['display_name']} voice using AWS Polly")
            return audio_data
            
        except Exception as e:
            print(f"❌ Polly error: {str(e)}")
            raise
    
    def _generate_google_voice(
        self, 
        text: str, 
        lang_config: Dict, 
        mood: str
    ) -> bytes:
        """Generate voice using Google Cloud TTS"""
        if not self.google_client:
            raise RuntimeError("Google TTS client not initialized. Check credentials.")
        
        mood_settings = self.MOOD_SETTINGS[mood]
        
        # Set up synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Configure voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_config['code'],
            name=lang_config['voice']
        )
        
        # Configure audio with mood settings
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=mood_settings['rate'],
            pitch=mood_settings['pitch'],
            volume_gain_db=mood_settings['volume']
        )
        
        try:
            response = self.google_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            print(f"✅ Generated {lang_config['display_name']} voice using Google TTS")
            return response.audio_content
            
        except Exception as e:
            print(f"❌ Google TTS error: {str(e)}")
            raise
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for UI"""
        return [
            {
                'code': code,
                'name': config['display_name'],
                'speakers': config['speakers'],
                'service': config['service']
            }
            for code, config in self.LANGUAGE_CONFIG.items()
        ]
    
    def get_supported_moods(self) -> list:
        """Get list of supported moods for UI"""
        return list(self.MOOD_SETTINGS.keys())


# Test the voice generator
if __name__ == "__main__":
    generator = BharatVoiceGenerator()
    
    # Test script
    test_text = "नमस्ते! आज हम बात करेंगे भारत के स्ट्रीट फूड के बारे में।"
    
    print("Testing voice generation...")
    audio = generator.generate_voiceover(
        text=test_text,
        language='hindi',
        mood='exciting'
    )
    
    # Save test audio
    with open('../outputs/test_voice.mp3', 'wb') as f:
        f.write(audio)
    
    print(f"✅ Test audio saved! Size: {len(audio)} bytes")
