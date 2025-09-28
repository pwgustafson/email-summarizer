# Gmail Email Summarizer

A Python command-line tool that automatically connects to your Gmail account, identifies important unread emails, and generates AI-powered daily summaries stored in structured YAML files.

## Features

- **Automated Gmail Integration**: Secure OAuth2 authentication with Gmail API ✅
- **Smart Email Filtering**: Focuses on emails marked as both important and unread ✅
- **Custom Search Configurations**: Save and manage custom Gmail search queries ✅
- **Advanced Search Operators**: Full support for Gmail search syntax with validation ✅
- **Configuration Management**: Environment variable support with validation ✅
- **Email Content Processing**: HTML cleaning, text extraction, and data normalization ✅
- **AI-Powered Summarization**: Uses OpenAI or Claude to generate concise summaries ✅
- **Structured Storage**: Saves summaries in daily YAML files ✅
- **Command-Line Interface**: Full CLI with argument parsing and verbose logging ✅
- **Backward Compatibility**: Graceful degradation and migration support ✅
- **Modular Architecture**: Clean, maintainable codebase with separated concerns ✅

## Current Implementation Status

This project is feature-complete and ready for use:

- ✅ **Configuration System**: Environment variable loading, validation, and AI provider selection
- ✅ **Gmail Authentication**: OAuth2 flow with secure token storage and refresh
- ✅ **Email Fetching**: Retrieval of important unread emails with content extraction and pagination
- ✅ **Custom Search**: Save, manage, and use custom Gmail search configurations
- ✅ **Search Validation**: Gmail search query syntax validation with helpful suggestions
- ✅ **Email Processing**: Content extraction, HTML cleaning, and text normalization
- ✅ **AI Summarization**: OpenAI/Claude integration for email summaries with structured output
- ✅ **YAML Storage**: Daily summary file creation and management with append functionality
- ✅ **CLI Interface**: Complete command-line interface with comprehensive workflow orchestration
- ✅ **Backward Compatibility**: Migration support and graceful degradation for existing users

## Project Structure

```
gmail-email-summarizer/
├── main.py                 # Entry point and CLI interface (✅ Complete)
├── auth/
│   ├── __init__.py
│   └── gmail_auth.py      # OAuth2 authentication (✅ Complete)
├── config/
│   ├── __init__.py
│   ├── settings.py        # Configuration management (✅ Complete)
│   ├── search_configs.py  # Search configuration management (✅ Complete)
│   └── example_configs.py # Example search configurations (✅ Complete)
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
├── utils/
│   ├── __init__.py
│   └── error_handling.py  # Error handling utilities (✅ Complete)
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
4. Click "Create"li

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

# Search Configuration (optional)
SEARCH_CONFIGS_FILE=search_configs.json
DEFAULT_SEARCH_QUERY=is:unread is:important
ENABLE_SEARCH_VALIDATION=true
MAX_SEARCH_RESULTS=100
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

#### Basic Options
| Option | Description | Example |
|--------|-------------|---------|
| `--max-emails N` | Process up to N emails (overrides config) | `--max-emails 10` |
| `--verbose`, `-v` | Enable verbose logging | `--verbose` |
| `--test-ai` | Test AI service connection and exit | `--test-ai` |
| `--output-dir DIR` | Specify output directory for YAML files | `--output-dir ./summaries` |

#### Search Customization Options
| Option | Description | Example |
|--------|-------------|---------|
| `--search-config NAME`, `-sc NAME` | Use a saved search configuration | `--search-config work-emails` |
| `--search-query QUERY`, `-sq QUERY` | Use a custom Gmail search query | `--search-query "from:boss@company.com is:unread"` |
| `--list-configs` | List all saved search configurations | `--list-configs` |
| `--save-config NAME QUERY DESC` | Save a new search configuration | `--save-config urgent "is:important newer_than:1d" "Urgent emails from today"` |
| `--delete-config NAME` | Delete a saved search configuration | `--delete-config old-config` |
| `--update-config NAME FIELD=VALUE` | Update an existing search configuration | `--update-config work-emails query="from:@company.com is:unread"` |

#### Search Help Options
| Option | Description | Example |
|--------|-------------|---------|
| `--help-search [OPERATOR]` | Show help for Gmail search operators | `--help-search from:` |
| `--example-configs` | Show example search configurations | `--example-configs` |
| `--validate-query QUERY` | Validate a Gmail search query | `--validate-query "from:test@example.com"` |

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

## Search Customization

The Gmail Email Summarizer includes powerful search customization features that allow you to create, save, and manage custom Gmail search queries. This enables you to focus on specific types of emails beyond the default "important and unread" filter.

### Quick Start with Search Customization

#### Using Custom Search Queries
```bash
# Use a custom search query directly
python main.py --search-query "from:manager@company.com is:unread"

# Process emails from a specific domain
python main.py --search-query "from:@company.com newer_than:2d"

# Find emails with attachments from the last week
python main.py --search-query "has:attachment newer_than:7d"
```

#### Saving and Using Search Configurations
```bash
# Save a search configuration for work emails
python main.py --save-config work-emails "from:@company.com is:unread" "Work emails from company domain"

# Use the saved configuration
python main.py --search-config work-emails

# List all saved configurations
python main.py --list-configs
```

### Gmail Search Operators

The tool supports the full range of Gmail search operators. Here are the most commonly used ones:

#### Sender and Recipient Operators
- `from:email@domain.com` - Emails from specific sender
- `to:email@domain.com` - Emails sent to specific recipient
- `cc:email@domain.com` - Emails where someone was CC'd
- `bcc:email@domain.com` - Emails where someone was BCC'd

#### Content and Subject Operators
- `subject:"meeting notes"` - Emails with specific subject
- `"exact phrase"` - Emails containing exact phrase
- `keyword1 OR keyword2` - Emails containing either keyword
- `keyword1 AND keyword2` - Emails containing both keywords

#### Date and Time Operators
- `after:2024-01-01` - Emails after specific date
- `before:2024-12-31` - Emails before specific date
- `newer_than:7d` - Emails newer than 7 days
- `older_than:1m` - Emails older than 1 month

#### Status and Properties
- `is:unread` - Unread emails
- `is:read` - Read emails
- `is:important` - Important emails
- `is:starred` - Starred emails
- `has:attachment` - Emails with attachments
- `larger:10M` - Emails larger than 10MB

#### Location Operators
- `in:inbox` - Emails in inbox
- `in:sent` - Emails in sent folder
- `in:trash` - Emails in trash
- `label:work` - Emails with specific label

### Search Configuration Management

#### Saving Search Configurations
```bash
# Basic syntax
python main.py --save-config NAME "QUERY" "DESCRIPTION"

# Examples
python main.py --save-config urgent-emails "is:important newer_than:1d" "Important emails from today"
python main.py --save-config team-updates "from:team@company.com subject:update" "Team status updates"
python main.py --save-config large-attachments "has:attachment larger:5M" "Emails with large attachments"
```

#### Listing and Managing Configurations
```bash
# List all saved configurations
python main.py --list-configs

# Delete a configuration
python main.py --delete-config old-config

# Update a configuration's query
python main.py --update-config work-emails query="from:@newcompany.com is:unread"

# Update a configuration's description
python main.py --update-config work-emails description="Updated work email filter"
```

#### Using Saved Configurations
```bash
# Use a saved configuration
python main.py --search-config work-emails

# Combine with other options
python main.py --search-config urgent-emails --max-emails 5 --verbose
```

### Example Search Configurations

#### Work and Professional
```bash
# All work emails from company domain
python main.py --save-config work-all "from:@company.com" "All emails from company"

# Urgent work emails
python main.py --save-config work-urgent "from:@company.com (subject:urgent OR subject:asap OR is:important)" "Urgent work emails"

# Meeting invitations and updates
python main.py --save-config meetings "subject:(meeting OR calendar OR invite OR reschedule)" "Meeting-related emails"

# Project-specific emails
python main.py --save-config project-alpha "subject:alpha OR subject:'project alpha'" "Project Alpha emails"
```

#### Personal and Communication
```bash
# Family emails
python main.py --save-config family "from:mom@email.com OR from:dad@email.com OR from:sister@email.com" "Family emails"

# Newsletter and subscriptions
python main.py --save-config newsletters "from:newsletter OR from:noreply OR subject:unsubscribe" "Newsletters and subscriptions"

# Social media notifications
python main.py --save-config social "from:@facebook.com OR from:@twitter.com OR from:@linkedin.com" "Social media notifications"
```

#### Time-Based Filters
```bash
# Today's important emails
python main.py --save-config today-important "is:important newer_than:1d" "Important emails from today"

# This week's unread emails
python main.py --save-config week-unread "is:unread newer_than:7d" "Unread emails from this week"

# Recent emails with attachments
python main.py --save-config recent-attachments "has:attachment newer_than:3d" "Recent emails with attachments"
```

#### Advanced Filters
```bash
# Large emails (over 1MB)
python main.py --save-config large-emails "larger:1M" "Large emails over 1MB"

# Emails from external senders (not from company domain)
python main.py --save-config external "-from:@company.com is:unread" "External emails (not from company)"

# High-priority emails with specific keywords
python main.py --save-config high-priority "is:important (subject:deadline OR subject:urgent OR subject:asap)" "High priority deadline emails"
```

### Search Query Validation

The tool includes built-in validation for Gmail search queries:

#### Validate Before Using
```bash
# Validate a query before using it
python main.py --validate-query "from:test@example.com is:unread"

# Get suggestions for invalid queries
python main.py --validate-query "form:test@example.com"  # Note the typo
```

#### Common Validation Errors and Fixes
- `form:` → `from:` (common typo)
- `too:` → `to:` (common typo)
- `subjct:` → `subject:` (common typo)
- `attachement:` → `has:attachment` (correct operator)
- `unred:` → `is:unread` (correct syntax)

### Search Help and Documentation

#### Get Help with Search Operators
```bash
# Show help for all Gmail search operators
python main.py --help-search

# Get help for specific operators
python main.py --help-search from:
python main.py --help-search date
python main.py --help-search has:
```

#### View Example Configurations
```bash
# Show pre-defined example configurations
python main.py --example-configs
```

### Advanced Search Techniques

#### Combining Multiple Criteria
```bash
# Work emails from last week with attachments
python main.py --search-query "from:@company.com newer_than:7d has:attachment"

# Important emails that aren't newsletters
python main.py --search-query "is:important -from:newsletter -subject:unsubscribe"

# Emails from specific people about specific projects
python main.py --search-query "(from:manager@company.com OR from:lead@company.com) (subject:project OR subject:deadline)"
```

#### Using Exclusion Operators
```bash
# All emails except from specific domain
python main.py --search-query "is:unread -from:@spam.com"

# Important emails but not automated messages
python main.py --search-query "is:important -from:noreply -from:donotreply"
```

#### Date Range Queries
```bash
# Emails from specific date range
python main.py --search-query "after:2024-01-01 before:2024-01-31"

# Emails from last month
python main.py --search-query "newer_than:1m older_than:1d"
```

### Configuration File Format

Search configurations are stored in `search_configs.json` with the following structure:

```json
{
  "version": "1.0",
  "configs": {
    "work-emails": {
      "name": "work-emails",
      "query": "from:@company.com is:unread",
      "description": "Work emails from company domain",
      "created_at": "2024-01-15T10:30:00",
      "last_used": "2024-01-16T09:15:00",
      "usage_count": 5
    }
  }
}
```

### Backward Compatibility

The search customization features are designed with backward compatibility in mind:

- **Existing users**: The application continues to work with default search behavior if no custom configurations are used
- **Graceful degradation**: If search configuration features are unavailable, the application falls back to default behavior
- **Migration support**: Configuration files are automatically migrated when the format is updated
- **Error handling**: Invalid configurations don't prevent the application from running

### Search Configuration Best Practices

#### Organizing Your Configurations
```bash
# Use descriptive names
python main.py --save-config work-urgent-today "from:@company.com is:important newer_than:1d" "Urgent work emails from today"

# Group related configurations with prefixes
python main.py --save-config work-all "from:@company.com" "All work emails"
python main.py --save-config work-urgent "from:@company.com is:important" "Urgent work emails"
python main.py --save-config personal-family "from:family@domain.com" "Family emails"
```

#### Performance Considerations
```bash
# Use specific date ranges to limit results
python main.py --save-config recent-important "is:important newer_than:7d" "Important emails from last week"

# Combine filters to narrow results
python main.py --save-config work-attachments "from:@company.com has:attachment newer_than:3d" "Recent work emails with attachments"
```

#### Regular Maintenance
```bash
# Review and clean up old configurations
python main.py --list-configs

# Update configurations as your needs change
python main.py --update-config old-config query="updated query here"

# Remove configurations you no longer use
python main.py --delete-config unused-config
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

### Search Configuration Options
- `SEARCH_CONFIGS_FILE`: Path to search configurations file (default: "search_configs.json")
- `DEFAULT_SEARCH_QUERY`: Default Gmail search query (default: "is:unread is:important")
- `ENABLE_SEARCH_VALIDATION`: Enable search query validation (default: true)
- `MAX_SEARCH_RESULTS`: Maximum search results to fetch (default: 100)

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

### Search Configuration Issues

#### "Search configuration not found"
**Problem**: Specified search configuration doesn't exist
**Solutions**:
- List available configurations: `python main.py --list-configs`
- Check the configuration name spelling (case-sensitive)
- Create the configuration if it doesn't exist: `python main.py --save-config name "query" "description"`
- Verify the search_configs.json file exists and is readable

#### "Invalid Gmail search query"
**Problem**: Search query syntax is incorrect
**Solutions**:
- Validate your query: `python main.py --validate-query "your query"`
- Check Gmail search operator help: `python main.py --help-search`
- Review example configurations: `python main.py --example-configs`
- Common fixes: `form:` → `from:`, `too:` → `to:`, `subjct:` → `subject:`

#### "Search configuration file corrupted"
**Problem**: search_configs.json file is damaged or invalid
**Solutions**:
- The application automatically creates a backup and recreates the file
- Check for `.backup_` files in your project directory
- Delete search_configs.json to reset (you'll lose saved configurations)
- Restore from backup if available

#### "No emails found with search query"
**Problem**: Search query returns no results
**Solutions**:
- This is normal if no emails match your criteria
- Test with a broader query: `python main.py --search-query "is:unread"`
- Check if emails exist in Gmail that match your query
- Verify date ranges aren't too restrictive
- Use `--verbose` to see the exact query being used

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

# Test search configuration features
python main.py --list-configs
python main.py --validate-query "is:unread"
python main.py --help-search

# Test custom search queries
python main.py --search-query "is:unread" --max-emails 1 --verbose
```

#### Run comprehensive tests
```bash
# Run all backward compatibility tests
python -m pytest test_backward_compatibility.py -v

# Run search configuration tests
python -m pytest test_search_configs.py -v

# Run search workflow integration tests
python -m pytest test_search_workflow_integration.py -v

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