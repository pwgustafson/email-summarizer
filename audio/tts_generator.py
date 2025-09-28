"""
Text-to-speech audio generation using OpenAI TTS API.

This module provides functionality to convert transcript text content into audio files
using OpenAI's text-to-speech API, with comprehensive error handling and file management.
"""

import os
from pathlib import Path
from typing import Optional
import logging

from openai import OpenAI
from utils.error_handling import retry_with_backoff, RetryConfig, RetryableError, NonRetryableError
from config.settings import Config


logger = logging.getLogger(__name__)


class AudioGenerationError(Exception):
    """Custom exception for audio generation errors."""
    pass


class AudioGenerator:
    """
    Handles text-to-speech conversion using OpenAI TTS API.
    
    Provides methods to convert text content to audio files with proper
    error handling, file management, and configuration validation.
    """
    
    def __init__(self, config: Config):
        """
        Initialize AudioGenerator with configuration.
        
        Args:
            config: Configuration object containing TTS settings
            
        Raises:
            AudioGenerationError: If configuration is invalid
        """
        self.config = config
        self._validate_config()
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.openai_api_key)
        
        # Ensure audio output directory exists
        self._ensure_audio_directory()
    
    def _validate_config(self) -> None:
        """
        Validate TTS configuration settings.
        
        Raises:
            AudioGenerationError: If configuration is invalid
        """
        if not self.config.openai_api_key:
            raise AudioGenerationError("OpenAI API key is required for audio generation")
        
        # Validate voice option
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if self.config.tts_voice not in valid_voices:
            raise AudioGenerationError(
                f"Invalid TTS voice '{self.config.tts_voice}'. "
                f"Valid options: {', '.join(valid_voices)}"
            )
        
        # Validate speed range
        if not (0.25 <= self.config.tts_speed <= 4.0):
            raise AudioGenerationError(
                f"Invalid TTS speed '{self.config.tts_speed}'. "
                "Speed must be between 0.25 and 4.0"
            )
        
        # Validate audio output directory
        if not self.config.audio_output_directory:
            raise AudioGenerationError("Audio output directory must be specified")
    
    def _ensure_audio_directory(self) -> None:
        """
        Create audio output directory if it doesn't exist.
        
        Raises:
            AudioGenerationError: If directory cannot be created
        """
        try:
            audio_dir = Path(self.config.audio_output_directory)
            audio_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Audio directory ensured: {audio_dir}")
        except OSError as e:
            raise AudioGenerationError(f"Failed to create audio directory: {e}")
    
    @retry_with_backoff(config=RetryConfig(max_attempts=3, base_delay=1.0))
    def generate_audio(self, text_content: str, output_path: str) -> str:
        """
        Convert text content to audio file using OpenAI TTS API.
        
        Args:
            text_content: Text content to convert to speech
            output_path: Full path where audio file should be saved
            
        Returns:
            str: Path to the generated audio file
            
        Raises:
            AudioGenerationError: If audio generation fails
        """
        if not text_content or not text_content.strip():
            raise AudioGenerationError("Text content cannot be empty")
        
        # Validate text length (OpenAI TTS has a 4096 character limit)
        if len(text_content) > 4096:
            logger.warning(f"Text content is {len(text_content)} characters, truncating to 4096")
            text_content = text_content[:4096]
        
        try:
            logger.info(f"Generating audio for {len(text_content)} characters of text")
            
            # Make TTS API call
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.config.tts_voice,
                speed=self.config.tts_speed,
                input=text_content
            )
            
            # Save audio file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as audio_file:
                for chunk in response.iter_bytes():
                    audio_file.write(chunk)
            
            logger.info(f"Audio file generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            # Convert to appropriate error type for retry logic
            if hasattr(e, 'status_code'):
                if e.status_code == 429:  # Rate limit
                    raise RetryableError(f"OpenAI TTS API rate limit exceeded: {str(e)}")
                elif e.status_code >= 500:  # Server errors
                    raise RetryableError(f"OpenAI TTS API server error: {str(e)}")
                elif e.status_code == 401:  # Auth errors
                    raise NonRetryableError(f"OpenAI TTS API authentication failed: {str(e)}")
                else:
                    raise NonRetryableError(f"OpenAI TTS API error: {str(e)}")
            else:
                # Network or other errors - make retryable
                error_str = str(e).lower()
                if any(indicator in error_str for indicator in ['connection', 'timeout', 'network']):
                    raise RetryableError(f"Network error during audio generation: {str(e)}")
                else:
                    raise NonRetryableError(f"Failed to generate audio: {str(e)}")
    
    def get_audio_path(self, date: str) -> str:
        """
        Generate audio file path for a given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            str: Full path to audio file
        """
        filename = f"{date}.mp3"
        return os.path.join(self.config.audio_output_directory, filename)
    
    def audio_exists(self, date: str) -> bool:
        """
        Check if audio file exists for a given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            bool: True if audio file exists, False otherwise
        """
        audio_path = self.get_audio_path(date)
        return os.path.exists(audio_path)
    
    def get_audio_file_size(self, date: str) -> Optional[int]:
        """
        Get the size of an audio file in bytes.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            int: File size in bytes, or None if file doesn't exist
        """
        audio_path = self.get_audio_path(date)
        try:
            return os.path.getsize(audio_path)
        except OSError:
            return None
    
    def delete_audio(self, date: str) -> bool:
        """
        Delete audio file for a given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            bool: True if file was deleted, False if it didn't exist
            
        Raises:
            AudioGenerationError: If deletion fails
        """
        audio_path = self.get_audio_path(date)
        
        if not os.path.exists(audio_path):
            return False
        
        try:
            os.remove(audio_path)
            logger.info(f"Deleted audio file: {audio_path}")
            return True
        except OSError as e:
            raise AudioGenerationError(f"Failed to delete audio file {audio_path}: {e}")