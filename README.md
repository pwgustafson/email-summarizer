# Gmail Email Summarizer

A Python command-line tool that automatically connects to your Gmail account, identifies important unread emails, and generates AI-powered daily summaries stored in structured YAML files.

## Features

- **Automated Gmail Integration**: Secure OAuth2 authentication with Gmail API ✅
- **Smart Email Filtering**: Focuses on emails marked as both important and unread ✅
- **Configuration Management**: Environment variable support with validation ✅
- **Email Content Processing**: HTML cleaning, text extraction, and data normalization ✅
- **AI-Powered Summarization**: Uses OpenAI or Claude to generate concise summaries ✅
- **Structured Storage**: Saves summaries in daily YAML files ✅
- **Command-Line Interface**: Full CLI with argument parsing and verbose logging ✅
- **Modular Architecture**: Clean, maintainable codebase with separated concerns ✅

## Current Implementation Status

This project is feature-complete and ready for use:

- ✅ **Configuration System**: Environment variable loading, validation, and AI provider selection
- ✅ **Gmail Authentication**: OAuth2 flow with secure token storage and refresh
- ✅ **Email Fetching**: Retrieval of important unread emails with content extraction and pagination
- ✅ **Email Processing**: Content extraction, HTML cleaning, and text normalization
- ✅ **AI Summarization**: OpenAI/Claude integration for email summaries with structured output
- ✅ **YAML Storage**: Daily summary file creation and management with append functionality
- ✅ **CLI Interface**: Complete command-line interface with comprehensive workflow orchestration

## Project Structure

```
gmail-email-summarizer/
├── main.py                 # Entry point and CLI interface (✅ Complete)
├── auth/
│   ├── __init__.py
│   └── gmail_auth.py      # OAuth2 authentication (✅ Complete)
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration management (✅ Complete)
├── gmail_email/
│   ├── __init__.py        # Module exports (✅ Complete)
│   ├── fetcher.py         # Gmail API integration (✅ Complete)
│   └── processor.py       # Email content processing (✅ Complete)
├── summarization/
│   ├── __init__.py
│   └── summarizer.py      # AI-powered summarization (✅ Complete)
├── storage/
│   ├── __init__.py
│   └── yaml_writer.py     # YAML file management (✅ Complete)
├── requirements.txt       # Python dependencies
├── test_basic_functionality.py  # Development testing script
├── .env.example           # Environment variable template
└── README.md             # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Gmail account
- Internet connection
- OpenAI or Claude API key (for AI summarization)

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd gmail-email-summarizer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Gmail API credentials** (detailed instructions below):
   - Follow the [Gmail API Credentials Setup](#gmail-api-credentials-setup) section
   - Download `credentials.json` and place it in the project root

5. **Configure AI service API keys** (detailed instructions below):
   - Follow the [AI Service API Key Configuration](#ai-service-api-key-configuration) section
   - Create a `.env` file with your API keys

6. **Verify installation**:
   ```bash
   python main.py --test-ai
   ```

## Gmail API Credentials Setup

### Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Gmail Email Summarizer")
4. Click "Create"

### Step 2: Enable Gmail API

1. In the Google Cloud Console, navigate to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and then "Enable"

### Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (App name, User support email, Developer contact)
   - Add your email to test users
   - Save and continue through all steps
4. For Application type, select "Desktop application"
5. Enter a name (e.g., "Gmail Email Summarizer")
6. Click "Create"

### Step 4: Download Credentials

1. Click the download button (⬇️) next to your newly created OAuth client
2. Save the file as `credentials.json` in your project root directory
3. **Important**: Keep this file secure and never commit it to version control

**Note**: You can reference `credentials.json.example` in the project for the expected file structure. Your actual credentials file should look similar but with your real values from Google Cloud Console.

### Step 5: Set OAuth Scopes

The application requires the following Gmail API scope:
- `https://www.googleapis.com/auth/gmail.readonly` (read-only access to Gmail)

This scope is automatically requested during the first authentication.

## AI Service API Key Configuration

You need an API key from either OpenAI or Claude (Anthropic) for email summarization.

### Option 1: OpenAI Setup

1. **Create OpenAI Account**:
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in to your account

2. **Generate API Key**:
   - Navigate to "API Keys" in your dashboard
   - Click "Create new secret key"
   - Copy the key (it starts with `sk-`)
   - **Important**: Store this key securely, you won't see it again

3. **Add to Environment**:
   ```bash
   # In your .env file
   OPENAI_API_KEY=sk-your-actual-api-key-here
   AI_PROVIDER=openai
   OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4 for better quality
   ```

### Option 2: Claude (Anthropic) Setup

1. **Create Anthropic Account**:
   - Go to [Anthropic Console](https://console.anthropic.com/)
   - Sign up or log in to your account

2. **Generate API Key**:
   - Navigate to "API Keys" section
   - Click "Create Key"
   - Copy the key
   - **Important**: Store this key securely

3. **Add to Environment**:
   ```bash
   # In your .env file
   CLAUDE_API_KEY=your-claude-api-key-here
   AI_PROVIDER=claude
   CLAUDE_MODEL=claude-3-haiku-20240307  # or claude-3-sonnet-20240229
   ```

### Environment Configuration File

Create a `.env` file in your project root with the following structure:

```bash
# AI Service Configuration (choose one)
# For OpenAI:
OPENAI_API_KEY=sk-your-openai-key-here
AI_PROVIDER=openai
OPENAI_MODEL=gpt-3.5-turbo

# For Claude:
# CLAUDE_API_KEY=your-claude-key-here
# AI_PROVIDER=claude
# CLAUDE_MODEL=claude-3-haiku-20240307

# Optional Configuration
MAX_EMAILS_PER_RUN=50
OUTPUT_DIRECTORY=email_summaries
MAX_TOKENS=500
TEMPERATURE=0.3
```

### API Key Security Best Practices

- **Never commit API keys to version control**
- **Use environment variables or .env files**
- **Rotate keys regularly**
- **Monitor API usage and costs**
- **Set usage limits in your AI provider dashboard**

## Security and Privacy Considerations

### Data Privacy

#### Email Content Processing
- **Local Processing**: Email content is processed locally on your machine
- **AI Service Transmission**: Email content is sent to your chosen AI service (OpenAI or Claude) for summarization
- **No Persistent Storage**: The application doesn't store raw email content permanently
- **Summary Storage**: Only AI-generated summaries are stored in YAML files

#### Third-Party Data Sharing
- **Gmail API**: Uses read-only access to your Gmail account
- **AI Services**: Email content is transmitted to OpenAI or Claude for processing
- **No Analytics**: The application doesn't send usage data to any analytics services

### Security Best Practices

#### Credential Management
```bash
# Set restrictive permissions on sensitive files
chmod 600 credentials.json
chmod 600 token.json
chmod 600 .env

# Ensure output directory is secure
chmod 700 email_summaries/
```

#### Network Security
- All API communications use HTTPS/TLS encryption
- OAuth2 tokens are stored securely and refreshed automatically
- No sensitive data is logged to console or files

#### File System Security
```bash
# Create secure output directory
mkdir -m 700 email_summaries

# Set secure permissions for summary files
find email_summaries/ -type f -exec chmod 600 {} \;
```

### Privacy Configuration

#### Minimize Data Exposure
```bash
# In your .env file, consider these privacy-focused settings:

# Limit email processing
MAX_EMAILS_PER_RUN=10

# Use more private AI models if available
AI_PROVIDER=claude  # Anthropic has different privacy policies than OpenAI

# Restrict output location
OUTPUT_DIRECTORY=/secure/path/email_summaries
```

#### Data Retention
- **Summary Files**: Stored indefinitely unless manually deleted
- **OAuth Tokens**: Stored in `token.json`, refreshed automatically
- **AI Service Logs**: Check your AI provider's data retention policies

### Compliance Considerations

#### GDPR/Privacy Regulations
- **Data Controller**: You are the data controller for your email summaries
- **Data Processing**: AI services may process your data according to their terms
- **Right to Deletion**: You can delete summary files and revoke API access at any time

#### Corporate/Enterprise Use
- **IT Policy Compliance**: Check your organization's policies on:
  - Third-party AI service usage
  - Email data processing
  - Cloud service data transmission
- **Data Classification**: Consider if your emails contain sensitive/classified information

### Recommended Security Measures

#### For Personal Use
1. **Regular Key Rotation**: Rotate API keys every 90 days
2. **Access Monitoring**: Monitor API usage in your provider dashboards
3. **Backup Security**: Encrypt backups of summary files
4. **Network Security**: Use on trusted networks only

#### For Enterprise Use
1. **VPN Usage**: Run through corporate VPN if required
2. **Audit Logging**: Enable detailed logging for compliance
3. **Data Classification**: Review email content sensitivity before processing
4. **Legal Review**: Have legal team review AI service terms of service

### Emergency Procedures

#### Compromised API Keys
```bash
# Immediately revoke compromised keys
# 1. Revoke in AI provider dashboard
# 2. Generate new keys
# 3. Update .env file
# 4. Test with: python main.py --test-ai
```

#### Compromised Gmail Access
```bash
# Revoke application access
# 1. Go to Google Account settings
# 2. Navigate to Security > Third-party apps
# 3. Remove "Gmail Email Summarizer" access
# 4. Delete token.json file
# 5. Re-authenticate when ready
```

#### Data Breach Response
1. **Assess Impact**: Determine what data may have been exposed
2. **Revoke Access**: Immediately revoke all API keys and OAuth tokens
3. **Secure Files**: Move or encrypt existing summary files
4. **Notify Stakeholders**: Inform relevant parties if required by policy
5. **Review Logs**: Check application and system logs for unauthorized access

## Usage

### Running the Application

The main application is fully functional. Run it with:

```bash
python main.py
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--max-emails N` | Process up to N emails (overrides config) | `--max-emails 10` |
| `--verbose`, `-v` | Enable verbose logging | `--verbose` |
| `--test-ai` | Test AI service connection and exit | `--test-ai` |
| `--output-dir DIR` | Specify output directory for YAML files | `--output-dir ./summaries` |

### Usage Examples

#### Basic Usage
```bash
# Run with default settings (processes up to 50 emails)
python main.py
```

#### First-Time Setup Verification
```bash
# Test your AI service connection
python main.py --test-ai

# Run with verbose logging to see detailed output
python main.py --verbose

# Process just 1 email to test the full workflow
python main.py --max-emails 1 --verbose
```

#### Daily Usage Scenarios
```bash
# Quick morning check (process up to 5 emails)
python main.py --max-emails 5

# Full daily summary with detailed logging
python main.py --verbose

# Custom output location for specific projects
python main.py --output-dir ./project_emails --max-emails 20
```

#### Automation Examples
```bash
# Cron job for daily 9 AM email summaries
# Add to crontab: 0 9 * * * /path/to/venv/bin/python /path/to/project/main.py

# Batch script for Windows (save as run_summarizer.bat)
@echo off
cd /d "C:\path\to\gmail-email-summarizer"
call venv\Scripts\activate
python main.py --max-emails 25
pause

# Shell script for Unix/Linux (save as run_summarizer.sh)
#!/bin/bash
cd /path/to/gmail-email-summarizer
source venv/bin/activate
python main.py --max-emails 25
```

#### Development and Testing
```bash
# Test basic functionality without AI processing
python test_basic_functionality.py

# Debug configuration issues
python -c "from config.settings import Config; c = Config(); print(f'AI Provider: {c.ai_provider}'); print(f'Output Dir: {c.output_directory}')"

# Test with minimal processing for debugging
python main.py --max-emails 1 --verbose --output-dir ./debug_output
```

### Testing Current Functionality

To test the implemented features, run the basic functionality test:

```bash
python test_basic_functionality.py
```

This will test:
- Configuration loading and validation
- Gmail OAuth2 authentication
- Email fetching with important/unread filtering
- Email content processing and extraction

### First-Time Setup

On first run, the tool will:
1. Open your browser for Gmail OAuth2 authentication
2. Save authentication tokens for future use
3. Test the connection to your Gmail account

### Scheduling and Automation

#### Unix/Linux/macOS (using cron)

1. **Edit your crontab**:
   ```bash
   crontab -e
   ```

2. **Add a daily job** (runs every day at 9:00 AM):
   ```bash
   0 9 * * * cd /path/to/gmail-email-summarizer && /path/to/venv/bin/python main.py >> /path/to/logs/email_summary.log 2>&1
   ```

3. **Alternative schedules**:
   ```bash
   # Every 4 hours
   0 */4 * * * cd /path/to/gmail-email-summarizer && /path/to/venv/bin/python main.py
   
   # Weekdays only at 8 AM
   0 8 * * 1-5 cd /path/to/gmail-email-summarizer && /path/to/venv/bin/python main.py
   
   # Twice daily (9 AM and 5 PM)
   0 9,17 * * * cd /path/to/gmail-email-summarizer && /path/to/venv/bin/python main.py
   ```

#### Windows (using Task Scheduler)

1. **Open Task Scheduler** (`taskschd.msc`)
2. **Create Basic Task**:
   - Name: "Gmail Email Summarizer"
   - Trigger: Daily at your preferred time
   - Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\gmail-email-summarizer`

#### Docker (for containerized deployment)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Run with docker-compose:
```yaml
version: '3.8'
services:
  email-summarizer:
    build: .
    volumes:
      - ./credentials.json:/app/credentials.json
      - ./email_summaries:/app/email_summaries
      - ./.env:/app/.env
    environment:
      - TZ=America/New_York
```

### Application Workflow

The application follows this complete workflow:

1. **Configuration Loading**: Loads settings from environment variables and validates API keys
2. **Gmail Authentication**: Authenticates with Gmail using OAuth2 (opens browser on first run)
3. **Email Fetching**: Retrieves emails marked as both important and unread
4. **Content Processing**: Extracts and cleans email content (HTML to text conversion)
5. **AI Summarization**: Generates structured summaries using OpenAI or Claude
6. **YAML Storage**: Saves summaries to daily YAML files with proper formatting

### Module Functionality

**EmailFetcher**: 
- Retrieves emails marked as both important and unread
- Handles Gmail API pagination for large result sets
- Extracts basic email metadata (subject, sender, date, body)
- Robust error handling for network issues and API limits

**EmailProcessor**:
- Processes raw Gmail API responses into structured EmailData objects
- Handles both plain text and HTML email content
- Cleans HTML using BeautifulSoup to extract readable text
- Removes common email artifacts and signatures
- Normalizes whitespace and formatting

**EmailSummarizer**:
- Integrates with OpenAI GPT models or Claude for AI-powered summarization
- Uses structured prompts to extract summaries, key points, and action items
- Handles rate limiting and API errors with fallback mechanisms
- Parses AI responses into structured EmailSummary objects
- Supports batch processing with proper delays between requests

**YAMLWriter**:
- Creates daily summary files in YYYY-MM-DD.yaml format
- Appends new summaries to existing daily files
- Handles empty summary files when no emails are found
- Maintains proper YAML structure with metadata and email counts
- Sets appropriate file permissions for security

## Data Structures

### EmailData
The EmailProcessor creates structured EmailData objects:

```python
@dataclass
class EmailData:
    subject: str        # Email subject line
    sender: str         # Sender email address
    date: datetime      # Parsed email date
    body: str          # Cleaned email content
    message_id: str    # Gmail message ID
```

### EmailSummary
The EmailSummarizer creates structured EmailSummary objects:

```python
@dataclass
class EmailSummary:
    subject: str           # Original email subject
    sender: str           # Sender email address
    date: str            # ISO format date string
    summary: str         # AI-generated concise summary
    key_points: List[str] # List of main points from email
    action_items: List[str] # List of required actions
    priority: str        # High/Medium/Low priority assessment
```

## Output Format and File Management

### YAML File Structure

Daily summary files are saved in YAML format with the following structure:

```yaml
date: "2024-01-15"
processed_at: "2024-01-15T10:30:00Z"
email_count: 2
emails:
  - subject: "Project Update Required"
    sender: "manager@company.com"
    date: "2024-01-15T09:15:00Z"
    summary: "Manager requesting status update on Q1 project deliverables with Friday deadline for initial draft."
    key_points:
      - "Q1 project deliverables need status update"
      - "Initial draft due Friday"
      - "Final presentation scheduled for next week"
    action_items:
      - "Prepare status update by Friday"
      - "Review presentation materials"
    priority: "High"
  - subject: "Team Meeting Notes"
    sender: "colleague@company.com"
    date: "2024-01-15T08:30:00Z"
    summary: "Weekly team meeting notes covering sprint progress and upcoming milestones."
    key_points:
      - "Sprint 3 completed successfully"
      - "Sprint 4 planning next week"
    action_items: []
    priority: "Medium"
```

### File Naming and Organization

- **File naming**: `YYYY-MM-DD.yaml` (e.g., `2024-01-15.yaml`)
- **Default location**: `./email_summaries/` directory
- **Multiple runs**: New emails are appended to existing daily files
- **Empty days**: Files are created even when no emails are found

### Example Directory Structure

```
email_summaries/
├── 2024-01-15.yaml    # Monday's emails
├── 2024-01-16.yaml    # Tuesday's emails
├── 2024-01-17.yaml    # Wednesday's emails (empty - no important emails)
└── 2024-01-18.yaml    # Thursday's emails
```

### Working with YAML Files

#### Reading with Python
```python
import yaml
from datetime import date

# Read today's summary
today = date.today().strftime('%Y-%m-%d')
with open(f'email_summaries/{today}.yaml', 'r') as f:
    summary = yaml.safe_load(f)
    
print(f"Processed {summary['email_count']} emails")
for email in summary['emails']:
    print(f"- {email['subject']} from {email['sender']}")
```

#### Reading with Command Line
```bash
# View today's summary
cat email_summaries/$(date +%Y-%m-%d).yaml

# Count emails processed this week
grep -h "email_count:" email_summaries/2024-01-*.yaml | awk '{sum += $2} END {print sum}'

# Find high-priority emails
grep -A 10 -B 5 "priority: \"High\"" email_summaries/*.yaml
```

### File Management Tips

#### Archiving Old Summaries
```bash
# Create monthly archives
mkdir -p archives/2024-01
mv email_summaries/2024-01-*.yaml archives/2024-01/

# Compress old archives
tar -czf archives/2024-01.tar.gz archives/2024-01/
```

#### Backup Strategies
```bash
# Simple backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf "email_summaries_backup_$DATE.tar.gz" email_summaries/

# Sync to cloud storage (example with rclone)
rclone sync email_summaries/ remote:email-summaries/
```

### Integration with Other Tools

#### Import into Spreadsheet
```python
import yaml
import pandas as pd
from glob import glob

# Combine all summaries into a DataFrame
all_emails = []
for file in glob('email_summaries/*.yaml'):
    with open(file, 'r') as f:
        data = yaml.safe_load(f)
        for email in data.get('emails', []):
            email['processed_date'] = data['date']
            all_emails.append(email)

df = pd.DataFrame(all_emails)
df.to_csv('email_summary_export.csv', index=False)
```

#### Search Across All Summaries
```bash
# Find emails from specific sender
grep -r "sender.*@company.com" email_summaries/

# Find emails with specific keywords
grep -r -i "deadline\|urgent\|asap" email_summaries/

# Find action items
grep -A 5 "action_items:" email_summaries/ | grep -v "action_items: \[\]"
```

## Configuration

The tool supports configuration through environment variables or a `.env` file:

### Required for AI Summarization
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI) - **Required**
- `CLAUDE_API_KEY`: Your Claude API key (if using Claude) - **Required**

### Optional Configuration
- `AI_PROVIDER`: Choose "openai" or "claude" (default: "openai")
- `MAX_EMAILS_PER_RUN`: Maximum emails to process per run (default: 50)
- `OUTPUT_DIRECTORY`: Directory for summary files (default: "email_summaries")
- `OPENAI_MODEL`: OpenAI model to use (default: "gpt-3.5-turbo")
- `CLAUDE_MODEL`: Claude model to use (default: "claude-3-haiku-20240307")
- `MAX_TOKENS`: Maximum tokens for AI responses (default: 500)
- `TEMPERATURE`: AI response creativity (0.0-2.0, default: 0.3)

### Gmail API Configuration
- Credentials file: `credentials.json` (required)
- Token storage: `token.json` (auto-generated)

## Requirements

- Python 3.7+
- Gmail account with API access enabled
- Internet connection
- OpenAI or Claude API key (for AI summarization features)

## Development Status

This project is actively under development following a modular implementation approach:

### Completed Modules ✅
- **Configuration Management**: Environment variable loading, validation, AI provider selection
- **Gmail Authentication**: OAuth2 flow with secure credential handling and token refresh
- **Email Fetching**: Gmail API integration with filtering for important unread emails and pagination support
- **Email Content Processing**: HTML cleaning, text extraction, and content normalization with BeautifulSoup

### In Progress ⏳
- **AI-Powered Summarization**: OpenAI and Claude API integration for generating email summaries

### Planned 📋
- **YAML Storage**: Daily summary file creation and management
- **Complete CLI Interface**: Full workflow orchestration
- **Error Handling**: Comprehensive error recovery and user feedback

### Testing

Run the test script to verify your setup:
```bash
python test_basic_functionality.py
```

This will validate your Gmail credentials and test the implemented functionality.

## Troubleshooting

### Gmail API Issues

#### "Credentials file not found"
**Problem**: Application can't find `credentials.json`
**Solutions**:
- Ensure `credentials.json` is in the project root directory
- Verify the file was downloaded from Google Cloud Console
- Check file permissions (should be readable by your user)
- Verify filename is exactly `credentials.json` (case-sensitive)

#### "Authentication failed" or "Invalid credentials"
**Problem**: OAuth2 authentication is failing
**Solutions**:
- Verify Gmail API is enabled in your Google Cloud project
- Ensure OAuth2 credentials are for "Desktop Application" type (not Web or Mobile)
- Check that your Google Cloud project has the correct OAuth consent screen configuration
- Try deleting `token.json` and re-authenticating
- Ensure your Google account has access to the Gmail API

#### "Access blocked: This app's request is invalid"
**Problem**: OAuth consent screen issues
**Solutions**:
- Configure OAuth consent screen in Google Cloud Console
- Add your email address to test users if using external user type
- Ensure all required fields are filled in the consent screen
- Wait a few minutes after making changes to OAuth settings

#### "Quota exceeded" or "Rate limit exceeded"
**Problem**: Gmail API usage limits reached
**Solutions**:
- Wait and try again later (quotas reset daily)
- Check your API usage in Google Cloud Console
- Consider implementing longer delays between API calls
- Reduce `MAX_EMAILS_PER_RUN` in your configuration

### AI Service Issues

#### "Invalid API key" (OpenAI)
**Problem**: OpenAI API key is incorrect or missing
**Solutions**:
- Verify your API key starts with `sk-` and is complete
- Check that the key is correctly set in your `.env` file
- Ensure no extra spaces or characters in the key
- Generate a new API key from OpenAI dashboard if needed
- Verify your OpenAI account has available credits

#### "Authentication failed" (Claude)
**Problem**: Claude API key issues
**Solutions**:
- Verify your Claude API key is correctly formatted
- Check that the key is properly set in your `.env` file
- Ensure your Anthropic account is in good standing
- Try generating a new API key from Anthropic console

#### "Model not found" or "Invalid model"
**Problem**: Specified AI model doesn't exist or isn't accessible
**Solutions**:
- Check available models in your AI provider's documentation
- For OpenAI: Use `gpt-3.5-turbo`, `gpt-4`, or other available models
- For Claude: Use `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`, etc.
- Verify your account has access to the specified model

#### "Rate limit exceeded" (AI Services)
**Problem**: Too many API requests in a short time
**Solutions**:
- Wait before retrying (rate limits usually reset quickly)
- Reduce the number of emails processed per run
- The application includes automatic retry logic with backoff
- Consider upgrading your AI service plan for higher limits

### Email Processing Issues

#### "No important unread emails found"
**Problem**: No emails match the filtering criteria
**Solutions**:
- This is normal behavior if you don't have emails marked as both important and unread
- Gmail automatically marks some emails as important based on your usage patterns
- You can manually mark emails as important using the Gmail interface
- Check your Gmail settings for importance markers
- Verify you have unread emails in your inbox

#### "Email content extraction failed"
**Problem**: Unable to extract readable content from emails
**Solutions**:
- The application automatically falls back to plain text if HTML parsing fails
- Check the verbose logs for specific error details
- Some emails with complex formatting may not extract perfectly
- Malformed emails are logged as warnings and skipped

#### "HTML parsing errors"
**Problem**: BeautifulSoup can't parse email HTML content
**Solutions**:
- This is usually handled automatically with fallback to plain text
- Update BeautifulSoup if you're using an old version
- Some emails with malformed HTML will be processed as plain text

### File System Issues

#### "Permission denied" when writing YAML files
**Problem**: Application can't write to output directory
**Solutions**:
- Check that the output directory exists and is writable
- Verify file permissions on the output directory
- Try running with different output directory: `--output-dir ./test_output`
- On Unix systems, check that your user owns the directory

#### "Disk space" errors
**Problem**: Not enough space to write summary files
**Solutions**:
- Free up disk space on your system
- Use a different output directory with more space
- Clean up old summary files if needed

### Installation Issues

#### "Module not found" or import errors
**Problem**: Python dependencies not installed correctly
**Solutions**:
- Ensure you're in the correct virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Try upgrading pip: `pip install --upgrade pip`
- Check Python version compatibility (requires Python 3.7+)

#### "Command not found: python"
**Problem**: Python not in PATH or not installed
**Solutions**:
- Try `python3` instead of `python`
- Verify Python installation: `python --version`
- Install Python from [python.org](https://python.org) if needed
- On macOS, consider using Homebrew: `brew install python`

### Configuration Issues

#### ".env file not loaded"
**Problem**: Environment variables not being read
**Solutions**:
- Ensure `.env` file is in the project root directory
- Check that variable names match exactly (case-sensitive)
- Verify no extra spaces around the `=` sign
- Try setting environment variables directly in your shell for testing

#### "Invalid configuration" errors
**Problem**: Configuration values are incorrect
**Solutions**:
- Check that numeric values (like `MAX_EMAILS_PER_RUN`) are valid integers
- Verify boolean values are `true` or `false` (lowercase)
- Ensure file paths exist and are accessible
- Review the configuration section for valid options

### Testing and Debugging

#### Enable verbose logging
```bash
python main.py --verbose
```

#### Test individual components
```bash
# Test AI service connection
python main.py --test-ai

# Test with limited emails
python main.py --max-emails 1 --verbose
```

#### Check configuration
```bash
python -c "from config.settings import Config; print(Config().dict())"
```

#### Verify Gmail connection
```bash
python test_basic_functionality.py
```

### Getting Help

If you're still experiencing issues:

1. **Check the logs**: Run with `--verbose` flag for detailed output
2. **Verify prerequisites**: Ensure all setup steps were completed
3. **Test components individually**: Use the test flags to isolate issues
4. **Check API status**: Verify Gmail API and AI service status pages
5. **Review configuration**: Double-check all API keys and settings

### Common Error Messages and Solutions

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `FileNotFoundError: credentials.json` | Missing Gmail credentials | Follow Gmail API setup steps |
| `Invalid API key` | Wrong or missing AI API key | Check `.env` file configuration |
| `Authentication failed` | OAuth2 issues | Re-run authentication flow |
| `No module named 'google'` | Missing dependencies | Run `pip install -r requirements.txt` |
| `Rate limit exceeded` | Too many API calls | Wait and retry, or reduce email count |
| `Permission denied` | File system permissions | Check directory permissions |

## Contributing

This project follows a specification-driven development approach. See the `.kiro/specs/` directory for detailed requirements, design, and implementation tasks.

## License

[Add your license information here]