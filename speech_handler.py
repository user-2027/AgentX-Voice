"""STT/TTS handler for voice processing."""
import io
import logging
from typing import Optional, Tuple
from google.cloud import speech
from google.cloud import texttospeech
from config import config

logger = logging.getLogger(__name__)


class SpeechHandler:
    """Speech processing handler."""
    
    def __init__(self):
        self.speech_client: Optional[speech.SpeechClient] = None
        self.tts_client: Optional[texttospeech.TextToSpeechClient] = None
        
        if config.ENABLE_STT_TTS and config.GCP_PROJECT_ID:
            try:
                self._initialize_clients()
            except Exception as e:
                logger.warning(f"GCP Speech services initialization failed: {e}")
                logger.info("Speech services will run in mock mode")
        else:
            logger.info("Speech services running in mock mode (GCP not configured)")
    
    def _initialize_clients(self):
        """Initialize GCP Speech and TTS clients."""
        if config.GCP_PROJECT_ID:
            self.speech_client = speech.SpeechClient()
            self.tts_client = texttospeech.TextToSpeechClient()
            logger.info("GCP Speech services initialized")
    
    def speech_to_text(self, audio_content: bytes, language_code: str = None) -> Tuple[str, float]:
        """
        Convert speech audio to text.
        
        Args:
            audio_content: Audio content as bytes
            language_code: Language code (defaults to config)
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        if not self.speech_client:
            # Mock mode - return placeholder
            logger.warning("Speech-to-Text in mock mode - returning placeholder")
            return "This is a mock transcription of the audio input. Please configure GCP Speech-to-Text for actual transcription.", 0.7
        
        try:
            language_code = language_code or config.SPEECH_LANGUAGE_CODE
            
            # Configure recognition
            audio = speech.RecognitionAudio(content=audio_content)
            config_speech = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.SPEECH_SAMPLE_RATE,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )
            
            # Perform recognition
            response = self.speech_client.recognize(
                config=config_speech,
                audio=audio
            )
            
            if not response.results:
                return "", 0.0
            
            # Get best result
            best_result = response.results[0]
            transcript = best_result.alternatives[0].transcript
            confidence = best_result.alternatives[0].confidence
            
            logger.info(f"Speech-to-Text: {transcript[:50]}... (confidence: {confidence:.2%})")
            return transcript, confidence or 0.8
            
        except Exception as e:
            logger.error(f"Error in speech-to-text: {e}")
            return "", 0.0
    
    def text_to_speech(self, text: str, language_code: str = None, voice_name: str = None) -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            language_code: Language code (defaults to config)
            voice_name: Voice name (defaults to config)
            
        Returns:
            Audio content as bytes (WAV format) or None on error
        """
        if not self.tts_client:
            # Mock mode - return empty audio
            logger.warning("Text-to-Speech in mock mode - returning empty audio")
            return b""  # Empty audio bytes in mock mode
        
        try:
            language_code = language_code or config.SPEECH_LANGUAGE_CODE
            voice_name = voice_name or config.TTS_VOICE_NAME
            
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=getattr(
                    texttospeech.SsmlVoiceGender,
                    config.TTS_VOICE_GENDER,
                    texttospeech.SsmlVoiceGender.NEUTRAL
                )
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.SPEECH_SAMPLE_RATE
            )
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            logger.info(f"Text-to-Speech: Generated audio for text length {len(text)}")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Check if speech services are properly configured."""
        return (
            config.ENABLE_STT_TTS and
            self.speech_client is not None and
            self.tts_client is not None
        )


# Global speech handler instance
speech_handler = SpeechHandler()

