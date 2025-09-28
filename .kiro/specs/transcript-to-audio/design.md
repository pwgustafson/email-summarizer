# Design Document

## Overview

This feature adds text-to-speech (TTS) functionality to the Gmail Email Summarizer, enabling users to convert generated transcript files into audio files using OpenAI's TTS API. The design integrates seamlessly with the existing modular architecture, following established patterns for AI service integration, error handling, and file management.

## Architecture

The audio generation feature follows the existing architectural patterns:

- **Modular Design**: New audio functionality is contained in a dedicated module
- **Configuration Integration**: Audio settings extend the existing Config class
- **CLI Integration**: New command-line options integrate with the existing argument parser
- **Error Handling**: Leverages the existing error handling framework with retry logic
- **File Management**: Follows established patterns for output directory management

### Integration Points

1. **Configuration Layer**: Extends `config/settings.py` with TTS-specific settings
2. **CLI Layer**: Adds new arguments to `main.py` for audio generation commands
3. **AI Service Layer**: Creates new `audio/` module that leverages OpenAI client patterns
4. **Storage Layer**: Follows existing file management patterns for audio output

## Components and Interfaces

### AudioGenerator Class

**Location**: `audio/tts_generator.py`

**Responsibilities**:
- Convert text content to audio using OpenAI TTS API
- Manage audio file creation and storage
- Handle TTS-specific error scenarios
- Provide audio generation configuration options

**Key Methods**:
```python
def __init__(self, config: Config)
def generate_audio(self, text_content: str, output_path: str) -> str
def get_audio_path(self, date: str) -> str
def audio_exists(self, date: str) -> bool
```

### Configuration Extensions

**Location**: `config/settings.py`

**New Configuration Fields**:
```python
# Audio Generation Settings
enable_audio_generation: bool = False
audio_output_directory: str = "audio_summaries"
tts_voice: str = "alloy"  # OpenAI voice options: alloy, echo, fable, onyx, nova, shimmer
tts_speed: float = 1.0    # Speed range: 0.25 to 4.0
```

### CLI Integration

**Location**: `main.py`

**New Command-Line Arguments**:
```python
--generate-audio          # Generate audio for today's transcript
--audio-date DATE         # Generate audio for specific date
```

## Data Models

### Audio File Structure

**Output Directory**: `audio_summaries/`
**File Naming**: `YYYY-MM-DD.mp3` (matches transcript naming convention)
**File Format**: MP3 (OpenAI TTS default output format)

### Configuration Schema

```python
@dataclass
class Config:
    # ... existing fields ...
    
    # Audio Generation Settings
    enable_audio_generation: bool = False
    audio_output_directory: str = "audio_summaries"
    tts_voice: str = "alloy"
    tts_speed: float = 1.0
```

## Error Handling

### Error Categories

1. **Configuration Errors**:
   - Missing OpenAI API key
   - Invalid voice or speed settings
   - Audio directory creation failures

2. **API Errors**:
   - OpenAI TTS API rate limits
   - API quota exceeded
   - Network connectivity issues
   - Invalid audio content (too long, empty, etc.)

3. **File System Errors**:
   - Audio directory permissions
   - Disk space issues
   - File write failures

### Error Handling Strategy

- **Retry Logic**: Use existing `retry_with_backoff` decorator for API calls
- **Graceful Degradation**: Continue operation if audio generation fails
- **User-Friendly Messages**: Leverage existing error message framework
- **Validation**: Validate inputs before making API calls

## Testing Strategy

### Unit Tests

**Location**: `test_audio_generator.py`

**Test Coverage**:
- Audio generation with valid inputs
- Error handling for various failure scenarios
- Configuration validation
- File path generation and validation
- Audio file existence checking

### Integration Tests

**Test Scenarios**:
- End-to-end audio generation from transcript
- CLI command integration
- Configuration loading and validation
- Error recovery and fallback behavior

### Mock Strategy

- Mock OpenAI TTS API calls for reliable testing
- Mock file system operations for error scenario testing
- Use existing test patterns from `summarization/` module

## Implementation Approach

### Phase 1: Core Audio Generation
- Create `AudioGenerator` class with basic TTS functionality
- Implement configuration extensions
- Add basic error handling and validation

### Phase 2: CLI Integration
- Add command-line arguments for audio generation
- Integrate with existing workflow in `main.py`
- Implement file management utilities

### Phase 3: Testing and Polish
- Comprehensive test coverage
- Error handling refinement
- Documentation and examples

## Dependencies

### New Dependencies
```python
# No new dependencies required - uses existing openai client
```

### Existing Dependencies Leveraged
- `openai`: For TTS API calls (already available)
- `config.settings`: For configuration management
- `utils.error_handling`: For error handling patterns
- `pathlib`, `os`: For file management (already used)

## Security Considerations

- **API Key Security**: Leverage existing OpenAI API key management
- **File Permissions**: Set appropriate permissions on audio files (similar to transcript files)
- **Input Validation**: Validate text content before sending to TTS API
- **Rate Limiting**: Implement appropriate delays to respect API limits

## Performance Considerations

- **File Size**: MP3 files will be larger than text files - monitor disk usage
- **API Latency**: TTS generation takes time - provide progress feedback
- **Rate Limits**: OpenAI TTS has rate limits - implement appropriate throttling
- **Caching**: Don't regenerate audio if file already exists (unless explicitly requested)