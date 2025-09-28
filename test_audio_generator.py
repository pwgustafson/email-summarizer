"""
Tests for the AudioGenerator class and audio generation functionality.

This module tests text-to-speech conversion, error handling, file management,
and configuration validation for the audio generation feature.
"""

import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import pytest

from audio.tts_generator import AudioGenerator, AudioGenerationError
from config.settings import Config


class TestAudioGenerator:
    """Test cases for AudioGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test audio files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test configuration
        self.config = Config()
        self.config.openai_api_key = "test-api-key"
        self.config.audio_output_directory = self.temp_dir
        self.config.tts_voice = "alloy"
        self.config.tts_speed = 1.0
        self.config.enable_audio_generation = True
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_valid_config(self):
        """Test AudioGenerator initialization with valid configuration."""
        with patch('audio.tts_generator.OpenAI') as mock_openai:
            generator = AudioGenerator(self.config)
            
            assert generator.config == self.config
            mock_openai.assert_called_once_with(api_key="test-api-key")
            assert os.path.exists(self.temp_dir)
    
    def test_init_missing_api_key(self):
        """Test AudioGenerator initialization fails with missing API key."""
        self.config.openai_api_key = ""
        
        with pytest.raises(AudioGenerationError, match="OpenAI API key is required"):
            AudioGenerator(self.config)
    
    def test_init_invalid_voice(self):
        """Test AudioGenerator initialization fails with invalid voice."""
        self.config.tts_voice = "invalid_voice"
        
        with pytest.raises(AudioGenerationError, match="Invalid TTS voice"):
            AudioGenerator(self.config)
    
    def test_init_invalid_speed(self):
        """Test AudioGenerator initialization fails with invalid speed."""
        self.config.tts_speed = 5.0  # Above maximum
        
        with pytest.raises(AudioGenerationError, match="Invalid TTS speed"):
            AudioGenerator(self.config)
        
        self.config.tts_speed = 0.1  # Below minimum
        
        with pytest.raises(AudioGenerationError, match="Invalid TTS speed"):
            AudioGenerator(self.config)
    
    def test_validate_config_valid_voices(self):
        """Test configuration validation accepts all valid voices."""
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        for voice in valid_voices:
            self.config.tts_voice = voice
            with patch('audio.tts_generator.OpenAI'):
                generator = AudioGenerator(self.config)
                assert generator.config.tts_voice == voice
    
    @patch('audio.tts_generator.OpenAI')
    def test_generate_audio_success(self, mock_openai):
        """Test successful audio generation."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.iter_bytes.return_value = [b'fake_audio_data']
        mock_client.audio.speech.create.return_value = mock_response
        
        generator = AudioGenerator(self.config)
        
        # Test audio generation
        text_content = "This is a test transcript."
        output_path = os.path.join(self.temp_dir, "test.mp3")
        
        result = generator.generate_audio(text_content, output_path)
        
        # Verify API call
        mock_client.audio.speech.create.assert_called_once_with(
            model="tts-1",
            voice="alloy",
            speed=1.0,
            input=text_content
        )
        
        # Verify file creation
        assert result == output_path
        assert os.path.exists(output_path)
        
        # Verify file content
        with open(output_path, 'rb') as f:
            assert f.read() == b'fake_audio_data'
    
    @patch('audio.tts_generator.OpenAI')
    def test_generate_audio_empty_text(self, mock_openai):
        """Test audio generation fails with empty text."""
        generator = AudioGenerator(self.config)
        
        with pytest.raises(AudioGenerationError, match="Text content cannot be empty"):
            generator.generate_audio("", "output.mp3")
        
        with pytest.raises(AudioGenerationError, match="Text content cannot be empty"):
            generator.generate_audio("   ", "output.mp3")
    
    @patch('audio.tts_generator.OpenAI')
    def test_generate_audio_long_text_truncation(self, mock_openai):
        """Test audio generation truncates long text content."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.iter_bytes.return_value = [b'fake_audio_data']
        mock_client.audio.speech.create.return_value = mock_response
        
        generator = AudioGenerator(self.config)
        
        # Create text longer than 4096 characters
        long_text = "A" * 5000
        output_path = os.path.join(self.temp_dir, "test.mp3")
        
        generator.generate_audio(long_text, output_path)
        
        # Verify API was called with truncated text
        call_args = mock_client.audio.speech.create.call_args
        assert len(call_args.kwargs['input']) == 4096
        assert call_args.kwargs['input'] == "A" * 4096
    
    @patch('audio.tts_generator.OpenAI')
    def test_generate_audio_api_error(self, mock_openai):
        """Test audio generation handles API errors."""
        from utils.error_handling import NonRetryableError
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.speech.create.side_effect = Exception("API Error")
        
        generator = AudioGenerator(self.config)
        
        with pytest.raises(NonRetryableError, match="Failed to generate audio"):
            generator.generate_audio("Test text", "output.mp3")
    
    @patch('audio.tts_generator.OpenAI')
    def test_get_audio_path(self, mock_openai):
        """Test audio path generation."""
        generator = AudioGenerator(self.config)
        
        path = generator.get_audio_path("2025-09-27")
        expected_path = os.path.join(self.temp_dir, "2025-09-27.mp3")
        
        assert path == expected_path
    
    @patch('audio.tts_generator.OpenAI')
    def test_audio_exists(self, mock_openai):
        """Test audio file existence checking."""
        generator = AudioGenerator(self.config)
        
        # Test non-existent file
        assert not generator.audio_exists("2025-09-27")
        
        # Create test file
        test_path = generator.get_audio_path("2025-09-27")
        with open(test_path, 'w') as f:
            f.write("test")
        
        # Test existing file
        assert generator.audio_exists("2025-09-27")
    
    @patch('audio.tts_generator.OpenAI')
    def test_get_audio_file_size(self, mock_openai):
        """Test audio file size retrieval."""
        generator = AudioGenerator(self.config)
        
        # Test non-existent file
        assert generator.get_audio_file_size("2025-09-27") is None
        
        # Create test file with known content
        test_path = generator.get_audio_path("2025-09-27")
        test_content = "test content"
        with open(test_path, 'w') as f:
            f.write(test_content)
        
        # Test existing file
        size = generator.get_audio_file_size("2025-09-27")
        assert size == len(test_content)
    
    @patch('audio.tts_generator.OpenAI')
    def test_delete_audio(self, mock_openai):
        """Test audio file deletion."""
        generator = AudioGenerator(self.config)
        
        # Test deleting non-existent file
        assert not generator.delete_audio("2025-09-27")
        
        # Create test file
        test_path = generator.get_audio_path("2025-09-27")
        with open(test_path, 'w') as f:
            f.write("test")
        
        assert os.path.exists(test_path)
        
        # Test deleting existing file
        assert generator.delete_audio("2025-09-27")
        assert not os.path.exists(test_path)
    
    @patch('audio.tts_generator.OpenAI')
    def test_delete_audio_permission_error(self, mock_openai):
        """Test audio file deletion handles permission errors."""
        generator = AudioGenerator(self.config)
        
        # Create test file
        test_path = generator.get_audio_path("2025-09-27")
        with open(test_path, 'w') as f:
            f.write("test")
        
        # Mock os.remove to raise permission error
        with patch('os.remove', side_effect=OSError("Permission denied")):
            with pytest.raises(AudioGenerationError, match="Failed to delete audio file"):
                generator.delete_audio("2025-09-27")
    
    def test_directory_creation_error(self):
        """Test AudioGenerator handles directory creation errors."""
        # Use an invalid path that cannot be created
        self.config.audio_output_directory = "/invalid/path/that/cannot/be/created"
        
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            with pytest.raises(AudioGenerationError, match="Failed to create audio directory"):
                AudioGenerator(self.config)


def test_config_audio_settings():
    """Test that Config class properly handles audio settings."""
    config = Config()
    
    # Test default values
    assert config.enable_audio_generation is False
    assert config.audio_output_directory == "audio_summaries"
    assert config.tts_voice == "alloy"
    assert config.tts_speed == 1.0
    
    # Test environment variable loading
    with patch.dict(os.environ, {
        'ENABLE_AUDIO_GENERATION': 'true',
        'AUDIO_OUTPUT_DIRECTORY': 'custom_audio',
        'TTS_VOICE': 'nova',
        'TTS_SPEED': '1.5'
    }):
        config = Config()
        assert config.enable_audio_generation is True
        assert config.audio_output_directory == "custom_audio"
        assert config.tts_voice == "nova"
        assert config.tts_speed == 1.5


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])