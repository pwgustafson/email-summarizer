"""Configuration management for Gmail Email Summarizer.

This module handles loading and validation of configuration settings,
including environment variables for API keys and other settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
import logging

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


@dataclass
class Config:
    """Configuration settings for the Gmail Email Summarizer application."""
    
    # Gmail API settings
    credentials_file: str = "credentials.json"
    token_file: str = "token.json"
    
    # Output settings
    output_directory: str = "email_summaries"
    max_emails_per_run: int = 5
    
    # AI Summarization Settings
    ai_provider: str = "openai"  # "openai" or "claude"
    openai_api_key: str = field(default="")
    openai_model: str = "gpt-3.5-turbo"
    claude_api_key: str = field(default="")
    claude_model: str = "claude-3-haiku-20240307"
    max_tokens: int = 500
    temperature: float = 0.3
    
    # Search Configuration Settings
    search_configs_file: str = "search_configs.json"
    default_search_query: str = "is:unread is:important"
    enable_search_validation: bool = True
    max_search_results: int = 100
    
    # Transcript Generation Settings
    enable_transcript_generation: bool = True
    transcript_output_directory: str = "transcripts"
    transcript_max_tokens: int = 1000
    transcript_temperature: float = 0.7
    
    # Audio Generation Settings
    enable_audio_generation: bool = False
    audio_output_directory: str = "audio_summaries"
    tts_voice: str = "alloy"  # OpenAI voice options: alloy, echo, fable, onyx, nova, shimmer
    tts_speed: float = 1.0    # Speed range: 0.25 to 4.0
    
    def __post_init__(self):
        """Load environment variables and validate configuration after initialization."""
        self._load_from_environment()
        self._validate_configuration()
    
    def _load_from_environment(self):
        """Load configuration values from environment variables."""
        # Load API keys from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", self.claude_api_key)
        
        # Load other optional settings from environment
        self.ai_provider = os.getenv("AI_PROVIDER", self.ai_provider).lower()
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.claude_model = os.getenv("CLAUDE_MODEL", self.claude_model)
        self.output_directory = os.getenv("OUTPUT_DIRECTORY", self.output_directory)
        
        # Load search configuration settings from environment
        self.search_configs_file = os.getenv("SEARCH_CONFIGS_FILE", self.search_configs_file)
        self.default_search_query = os.getenv("DEFAULT_SEARCH_QUERY", self.default_search_query)
        
        # Load transcript configuration settings from environment
        self.transcript_output_directory = os.getenv("TRANSCRIPT_OUTPUT_DIRECTORY", self.transcript_output_directory)
        
        # Load audio configuration settings from environment
        self.audio_output_directory = os.getenv("AUDIO_OUTPUT_DIRECTORY", self.audio_output_directory)
        self.tts_voice = os.getenv("TTS_VOICE", self.tts_voice)
        
        # Load TTS speed with validation
        try:
            self.tts_speed = float(os.getenv("TTS_SPEED", str(self.tts_speed)))
        except ValueError as e:
            logging.warning(f"Invalid TTS_SPEED environment variable: {e}")
        
        # Load numeric settings with validation
        try:
            self.max_emails_per_run = int(os.getenv("MAX_EMAILS_PER_RUN", str(self.max_emails_per_run)))
            self.max_tokens = int(os.getenv("MAX_TOKENS", str(self.max_tokens)))
            self.temperature = float(os.getenv("TEMPERATURE", str(self.temperature)))
            self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", str(self.max_search_results)))
            self.transcript_max_tokens = int(os.getenv("TRANSCRIPT_MAX_TOKENS", str(self.transcript_max_tokens)))
            self.transcript_temperature = float(os.getenv("TRANSCRIPT_TEMPERATURE", str(self.transcript_temperature)))
        except ValueError as e:
            logging.warning(f"Invalid numeric environment variable: {e}")
        
        # Load boolean settings with validation
        try:
            enable_search_validation_env = os.getenv("ENABLE_SEARCH_VALIDATION")
            if enable_search_validation_env is not None:
                self.enable_search_validation = enable_search_validation_env.lower() in ("true", "1", "yes", "on")
            
            enable_transcript_generation_env = os.getenv("ENABLE_TRANSCRIPT_GENERATION")
            if enable_transcript_generation_env is not None:
                self.enable_transcript_generation = enable_transcript_generation_env.lower() in ("true", "1", "yes", "on")
            
            enable_audio_generation_env = os.getenv("ENABLE_AUDIO_GENERATION")
            if enable_audio_generation_env is not None:
                self.enable_audio_generation = enable_audio_generation_env.lower() in ("true", "1", "yes", "on")
        except Exception as e:
            logging.warning(f"Invalid boolean environment variable: {e}")
    
    def _validate_configuration(self):
        """Validate configuration settings and raise errors for invalid values."""
        # Validate AI provider
        if self.ai_provider not in ["openai", "claude"]:
            raise ValueError(f"Invalid AI provider: {self.ai_provider}. Must be 'openai' or 'claude'")
        
        # Validate API keys based on provider
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider. Set OPENAI_API_KEY environment variable.")
        
        if self.ai_provider == "claude" and not self.claude_api_key:
            raise ValueError("Claude API key is required when using Claude provider. Set CLAUDE_API_KEY environment variable.")
        
        # Validate numeric ranges
        if self.max_emails_per_run <= 0:
            raise ValueError("max_emails_per_run must be greater than 0")
        
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")
        
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        if self.max_search_results <= 0:
            raise ValueError("max_search_results must be greater than 0")
        
        if self.transcript_max_tokens <= 0:
            raise ValueError("transcript_max_tokens must be greater than 0")
        
        if not 0.0 <= self.transcript_temperature <= 2.0:
            raise ValueError("transcript_temperature must be between 0.0 and 2.0")
        
        # Validate file paths
        if not self.credentials_file:
            raise ValueError("credentials_file cannot be empty")
        
        if not self.token_file:
            raise ValueError("token_file cannot be empty")
        
        if not self.output_directory:
            raise ValueError("output_directory cannot be empty")
        
        if not self.search_configs_file:
            raise ValueError("search_configs_file cannot be empty")
        
        if not self.transcript_output_directory:
            raise ValueError("transcript_output_directory cannot be empty")
        
        # Validate search settings
        if not self.default_search_query:
            raise ValueError("default_search_query cannot be empty")
        
        # Basic validation of default search query format
        if not isinstance(self.default_search_query, str):
            raise ValueError("default_search_query must be a string")
        
        # Validate that enable_search_validation is boolean
        if not isinstance(self.enable_search_validation, bool):
            raise ValueError("enable_search_validation must be a boolean value")
        
        # Validate that enable_transcript_generation is boolean
        if not isinstance(self.enable_transcript_generation, bool):
            raise ValueError("enable_transcript_generation must be a boolean value")
        
        # Validate audio generation settings
        if not isinstance(self.enable_audio_generation, bool):
            raise ValueError("enable_audio_generation must be a boolean value")
        
        if not self.audio_output_directory:
            raise ValueError("audio_output_directory cannot be empty")
        
        # Validate TTS voice option
        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if self.tts_voice not in valid_voices:
            raise ValueError(f"Invalid TTS voice '{self.tts_voice}'. Valid options: {', '.join(valid_voices)}")
        
        # Validate TTS speed range
        if not 0.25 <= self.tts_speed <= 4.0:
            raise ValueError(f"TTS speed must be between 0.25 and 4.0, got {self.tts_speed}")
    
    def get_api_key(self) -> str:
        """Get the appropriate API key based on the configured provider."""
        if self.ai_provider == "openai":
            return self.openai_api_key
        elif self.ai_provider == "claude":
            return self.claude_api_key
        else:
            raise ValueError(f"Unknown AI provider: {self.ai_provider}")
    
    def get_model_name(self) -> str:
        """Get the appropriate model name based on the configured provider."""
        if self.ai_provider == "openai":
            return self.openai_model
        elif self.ai_provider == "claude":
            return self.claude_model
        else:
            raise ValueError(f"Unknown AI provider: {self.ai_provider}")


def load_config() -> Config:
    """Load and return a validated configuration instance.
    
    Returns:
        Config: A validated configuration instance with settings loaded from
                environment variables and defaults.
    
    Raises:
        ValueError: If configuration validation fails.
    """
    try:
        config = Config()
        logging.info(f"Configuration loaded successfully. AI Provider: {config.ai_provider}")
        return config
    except ValueError as e:
        logging.error(f"Configuration validation failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error loading configuration: {e}")
        raise ValueError(f"Failed to load configuration: {e}")


def validate_gmail_credentials(config: Config) -> bool:
    """Validate that Gmail API credentials file exists.
    
    Args:
        config: Configuration instance to validate
        
    Returns:
        bool: True if credentials file exists, False otherwise
    """
    if not os.path.exists(config.credentials_file):
        logging.error(f"Gmail credentials file not found: {config.credentials_file}")
        return False
    
    logging.info(f"Gmail credentials file found: {config.credentials_file}")
    return True


def ensure_output_directory(config: Config) -> bool:
    """Ensure the output directory exists, creating it if necessary.
    
    Args:
        config: Configuration instance containing output directory path
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(config.output_directory, exist_ok=True)
        logging.info(f"Output directory ready: {config.output_directory}")
        return True
    except OSError as e:
        logging.error(f"Failed to create output directory {config.output_directory}: {e}")
        return False


def ensure_transcript_directory(config: Config) -> bool:
    """Ensure the transcript output directory exists, creating it if necessary.
    
    Args:
        config: Configuration instance containing transcript output directory path
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(config.transcript_output_directory, exist_ok=True)
        logging.info(f"Transcript output directory ready: {config.transcript_output_directory}")
        return True
    except OSError as e:
        logging.error(f"Failed to create transcript output directory {config.transcript_output_directory}: {e}")
        return False


def ensure_audio_directory(config: Config) -> bool:
    """Ensure the audio output directory exists, creating it if necessary.
    
    Args:
        config: Configuration instance containing audio output directory path
        
    Returns:
        bool: True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(config.audio_output_directory, exist_ok=True)
        logging.info(f"Audio output directory ready: {config.audio_output_directory}")
        return True
    except OSError as e:
        logging.error(f"Failed to create audio output directory {config.audio_output_directory}: {e}")
        return False