#!/usr/bin/env python3
"""
Gmail Email Summarizer

A command-line tool that connects to Gmail, fetches important unread emails,
generates AI-powered summaries, and stores them in daily YAML files.
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from typing import List, Optional

# Import application modules
from config.settings import load_config, validate_gmail_credentials, ensure_output_directory, ensure_transcript_directory
from config.search_configs import (
    SearchConfigManager, SearchConfig, SearchConfigError,
    ConfigurationNotFoundError, InvalidConfigurationError,
    QueryValidationError, CorruptedConfigFileError
)
from config.example_configs import GmailSearchHelp, ExampleConfigurations
from auth.gmail_auth import GmailAuthError
from gmail_email.fetcher import create_email_fetcher, EmailFetchError
from gmail_email.processor import EmailProcessor, EmailData
from summarization.summarizer import EmailSummarizer
from summarization.transcript_generator import TranscriptGenerator
from storage.yaml_writer import YAMLWriter
from storage.transcript_writer import TranscriptWriter
from utils.error_handling import (
    RetryableError, NonRetryableError, ErrorCategory,
    create_user_friendly_message, classify_error
)


def setup_logging(verbose: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Gmail Email Summarizer - Fetch and summarize important unread emails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run with default settings
  %(prog)s --max-emails 10                    # Process up to 10 emails
  %(prog)s --verbose                          # Enable verbose logging
  %(prog)s --test-ai                          # Test AI service connection only
  %(prog)s --search-config work-emails        # Use saved search configuration
  %(prog)s --search-query "from:boss@company.com is:unread"  # Use custom query
  %(prog)s --list-configs                     # List all saved configurations
  %(prog)s --save-config urgent "is:important newer_than:1d" "Urgent emails from today"
  %(prog)s --delete-config old-config         # Delete a saved configuration
  %(prog)s --update-config work-emails query="from:@company.com is:unread after:2024-01-01"
  %(prog)s --no-transcript                    # Disable transcript generation
  %(prog)s --transcript-only 2025-09-19       # Generate transcript from existing YAML
  %(prog)s --transcript-date 2025-09-19       # Use specific date for transcript
  %(prog)s --generate-audio                   # Generate audio for today's transcript
  %(prog)s --audio-date 2025-09-19            # Generate audio for specific date
        """
    )
    
    # Existing arguments
    parser.add_argument(
        '--max-emails',
        type=int,
        help='Maximum number of emails to process (overrides config)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--test-ai',
        action='store_true',
        help='Test AI service connection and exit'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for YAML files (overrides config)'
    )
    
    # New search configuration arguments
    parser.add_argument(
        '--search-config', '-sc',
        type=str,
        help='Use a saved search configuration by name'
    )
    
    parser.add_argument(
        '--search-query', '-sq',
        type=str,
        help='Use a custom Gmail search query directly'
    )
    
    parser.add_argument(
        '--list-configs',
        action='store_true',
        help='List all saved search configurations and exit'
    )
    
    parser.add_argument(
        '--save-config',
        nargs=3,
        metavar=('NAME', 'QUERY', 'DESCRIPTION'),
        help='Save a new search configuration with name, query, and description'
    )
    
    parser.add_argument(
        '--delete-config',
        type=str,
        metavar='NAME',
        help='Delete a saved search configuration by name'
    )
    
    parser.add_argument(
        '--update-config',
        nargs='+',
        metavar=('NAME', 'FIELD=VALUE'),
        help='Update an existing search configuration. Usage: --update-config NAME query="new query" description="new desc"'
    )
    
    parser.add_argument(
        '--help-search',
        nargs='?',
        const='all',
        metavar='OPERATOR',
        help='Show help for Gmail search operators. Use --help-search <operator> for specific help (e.g., --help-search from:)'
    )
    
    parser.add_argument(
        '--example-configs',
        action='store_true',
        help='Show example search configurations for common use cases'
    )
    
    parser.add_argument(
        '--validate-query',
        type=str,
        metavar='QUERY',
        help='Validate a Gmail search query and show suggestions'
    )
    
    # Transcript generation arguments
    parser.add_argument(
        '--no-transcript',
        action='store_true',
        help='Disable transcript generation for this run'
    )
    
    parser.add_argument(
        '--transcript-only',
        type=str,
        metavar='DATE',
        help='Generate transcript from existing YAML file for specified date (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--transcript-date',
        type=str,
        metavar='DATE',
        help='Specify date for transcript generation (YYYY-MM-DD, defaults to today)'
    )
    
    # Audio generation arguments
    parser.add_argument(
        '--generate-audio',
        action='store_true',
        help='Generate audio for today\'s transcript'
    )
    
    parser.add_argument(
        '--audio-date',
        type=str,
        metavar='DATE',
        help='Generate audio for specific date (YYYY-MM-DD)'
    )
    
    return parser.parse_args()


def test_ai_connection(config) -> bool:
    """Test AI service connection."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Testing {config.ai_provider.upper()} connection...")
        summarizer = EmailSummarizer(config)
        
        if summarizer.test_ai_connection():
            logger.info("✓ AI service connection successful")
            return True
        else:
            logger.error("✗ AI service connection failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ AI service test failed: {e}")
        return False


def list_search_configs(search_manager: SearchConfigManager) -> int:
    """List all saved search configurations.
    
    Args:
        search_manager: SearchConfigManager instance
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        configs = search_manager.list_configs()
        
        if not configs:
            print("No saved search configurations found.")
            print("Use --save-config to create your first configuration.")
            return 0
        
        print(f"Found {len(configs)} saved search configuration(s):")
        print("=" * 60)
        
        for config in configs:
            print(f"Name: {config.name}")
            print(f"Query: {config.query}")
            print(f"Description: {config.description}")
            print(f"Created: {config.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if config.last_used:
                print(f"Last used: {config.last_used.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("Last used: Never")
            
            print(f"Usage count: {config.usage_count}")
            print("-" * 40)
        
        # Show usage statistics
        stats = search_manager.get_config_stats()
        if stats.get("total_usage", 0) > 0:
            print(f"Total usage across all configs: {stats['total_usage']}")
            
            if stats.get("most_used"):
                most_used = stats["most_used"]
                print(f"Most used: {most_used['name']} ({most_used['usage_count']} times)")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to list configurations: {e}")
        return 1


def save_search_config(search_manager: SearchConfigManager, name: str, query: str, description: str) -> int:
    """Save a new search configuration.
    
    Args:
        search_manager: SearchConfigManager instance
        name: Configuration name
        query: Gmail search query
        description: Configuration description
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate arguments
        if not name or not name.strip():
            print("Error: Configuration name cannot be empty")
            return 1
        
        if not query or not query.strip():
            print("Error: Search query cannot be empty")
            return 1
        
        if not description or not description.strip():
            print("Error: Description cannot be empty")
            return 1
        
        # Clean up inputs
        name = name.strip()
        query = query.strip()
        description = description.strip()
        
        # Create and save configuration
        config = SearchConfig(
            name=name,
            query=query,
            description=description,
            created_at=datetime.now()
        )
        
        search_manager.save_config(config)
        
        print(f"✓ Successfully saved search configuration '{name}'")
        print(f"Query: {query}")
        print(f"Description: {description}")
        
        return 0
        
    except QueryValidationError as e:
        logger.warning(f"Query validation failed for config '{name}': {e}")
        print(f"Error: {e.error_message}")
        if e.suggestions:
            print("\nSuggestions:")
            for suggestion in e.suggestions:
                print(f"  - {suggestion}")
        return 1
    except InvalidConfigurationError as e:
        logger.warning(f"Invalid configuration '{name}': {e}")
        print(f"Error: {e}")
        if e.suggestions:
            print("\nSuggestions:")
            for suggestion in e.suggestions:
                print(f"  - {suggestion}")
        return 1
    except CorruptedConfigFileError as e:
        logger.error(f"Configuration file corrupted while saving '{name}': {e}")
        print(f"Error: {e}")
        print("The configuration file has been recreated. Please try again.")
        return 1
    except SearchConfigError as e:
        logger.error(f"Search configuration error saving '{name}': {e}")
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error saving configuration '{name}': {e}")
        print(f"Error: {create_user_friendly_message(e, f'saving configuration \'{name}\'')}")
        return 1


def delete_search_config(search_manager: SearchConfigManager, name: str) -> int:
    """Delete a saved search configuration.
    
    Args:
        search_manager: SearchConfigManager instance
        name: Configuration name to delete
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate argument
        if not name or not name.strip():
            print("Error: Configuration name cannot be empty")
            return 1
        
        name = name.strip()
        
        # Check if configuration exists
        config = search_manager.load_config(name)
        if not config:
            print(f"Error: Configuration '{name}' not found")
            
            # Show available configurations
            configs = search_manager.list_configs()
            if configs:
                print("\nAvailable configurations:")
                for cfg in configs:
                    print(f"  - {cfg.name}")
            else:
                print("No saved configurations found.")
            
            return 1
        
        # Show configuration details and ask for confirmation
        print(f"Configuration to delete:")
        print(f"  Name: {config.name}")
        print(f"  Query: {config.query}")
        print(f"  Description: {config.description}")
        print(f"  Usage count: {config.usage_count}")
        
        # Get confirmation (in a real CLI, this would be interactive)
        # For now, we'll proceed with deletion since this is a command-line tool
        print(f"\nDeleting configuration '{name}'...")
        
        success = search_manager.delete_config(name)
        if success:
            print(f"✓ Successfully deleted configuration '{name}'")
            return 0
        else:
            print(f"Error: Failed to delete configuration '{name}'")
            return 1
        
    except Exception as e:
        logger.error(f"Failed to delete configuration '{name}': {e}")
        print(f"Error: Failed to delete configuration - {e}")
        return 1


def update_search_config(search_manager: SearchConfigManager, name: str, query: str = None, description: str = None) -> int:
    """Update an existing search configuration.
    
    Args:
        search_manager: SearchConfigManager instance
        name: Configuration name to update
        query: New search query (optional, keeps existing if None)
        description: New description (optional, keeps existing if None)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate argument
        if not name or not name.strip():
            print("Error: Configuration name cannot be empty")
            return 1
        
        name = name.strip()
        
        # Check if configuration exists
        existing_config = search_manager.load_config(name)
        if not existing_config:
            print(f"Error: Configuration '{name}' not found")
            
            # Show available configurations
            configs = search_manager.list_configs()
            if configs:
                print("\nAvailable configurations:")
                for cfg in configs:
                    print(f"  - {cfg.name}")
            else:
                print("No saved configurations found.")
            
            return 1
        
        # Determine what to update
        new_query = query.strip() if query and query.strip() else existing_config.query
        new_description = description.strip() if description and description.strip() else existing_config.description
        
        # Validate new query if provided
        if query and query.strip():
            is_valid, error_msg = search_manager.validate_query(new_query)
            if not is_valid:
                print(f"Error: Invalid search query - {error_msg}")
                
                # Provide suggestions if available
                suggestions = search_manager.validator.suggest_corrections(new_query)
                if suggestions:
                    print("\nSuggestions:")
                    for suggestion in suggestions:
                        print(f"  - {suggestion}")
                
                return 1
        
        # Show what will be updated
        print(f"Updating configuration '{name}':")
        print(f"  Current query: {existing_config.query}")
        print(f"  New query: {new_query}")
        print(f"  Current description: {existing_config.description}")
        print(f"  New description: {new_description}")
        
        # Create updated configuration
        updated_config = SearchConfig(
            name=existing_config.name,
            query=new_query,
            description=new_description,
            created_at=existing_config.created_at,
            last_used=existing_config.last_used,
            usage_count=existing_config.usage_count
        )
        
        # Update the configuration
        success = search_manager.update_config(name, updated_config)
        if success:
            print(f"✓ Successfully updated configuration '{name}'")
            return 0
        else:
            print(f"Error: Failed to update configuration '{name}'")
            return 1
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to update configuration '{name}': {e}")
        print(f"Error: Failed to update configuration - {e}")
        return 1


def handle_config_commands(args) -> int:
    """Handle search configuration management commands.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration to get search configs file path
        config = load_config()
        search_configs_file = getattr(config, 'search_configs_file', 'search_configs.json')
        
        try:
            search_manager = SearchConfigManager(search_configs_file)
            
            # Check if search features are available
            if not search_manager.is_search_feature_available():
                logger.warning("Search configuration features are not fully available")
                print("Warning: Search configuration features may not be fully available.")
                
                # Get compatibility info for better error messages
                compat_info = search_manager.get_backward_compatibility_info()
                if 'error' in compat_info:
                    print(f"Error: {compat_info['error']}")
                    print("Search configuration management is unavailable.")
                    return 1
                
                print("Attempting to continue with limited functionality...")
            
        except CorruptedConfigFileError as e:
            logger.error(f"Configuration file is corrupted: {e}")
            print(f"Error: {e}")
            print("The configuration file has been recreated. Please try your command again.")
            return 1
        except Exception as e:
            logger.error(f"Failed to initialize search configuration manager: {e}")
            print(f"Error: Could not access search configurations - {create_user_friendly_message(e, 'initializing search configuration manager')}")
            print("Search configuration features are unavailable. The application will work with default search behavior.")
            return 1
        
        if args.list_configs:
            return list_search_configs(search_manager)
        elif args.save_config:
            name, query, description = args.save_config
            return save_search_config(search_manager, name, query, description)
        elif args.delete_config:
            return delete_search_config(search_manager, args.delete_config)
        elif args.update_config:
            return _handle_update_config(search_manager, args.update_config)
        
        return 0
        
    except SearchConfigError as e:
        logger.error(f"Search configuration error: {e}")
        print(f"Error: {e}")
        if hasattr(e, 'suggestions') and e.suggestions:
            print("\nSuggestions:")
            for suggestion in e.suggestions:
                print(f"  - {suggestion}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in configuration management: {e}")
        print(f"Error: Configuration management failed - {create_user_friendly_message(e, 'managing search configurations')}")
        print("The application will continue to work with default search behavior.")
        return 1


def _handle_update_config(search_manager: SearchConfigManager, update_args: List[str]) -> int:
    """Handle the --update-config command parsing and execution.
    
    Args:
        search_manager: SearchConfigManager instance
        update_args: List of arguments from --update-config
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if len(update_args) < 2:
        print("Error: --update-config requires at least a name and one field to update")
        print("Usage: --update-config NAME query=\"new query\" description=\"new description\"")
        return 1
    
    name = update_args[0]
    
    # Parse field=value pairs
    query = None
    description = None
    
    for arg in update_args[1:]:
        if '=' not in arg:
            print(f"Error: Invalid update argument '{arg}'. Expected format: field=value")
            return 1
        
        field, value = arg.split('=', 1)
        field = field.strip().lower()
        value = value.strip().strip('"\'')  # Remove quotes if present
        
        if field == 'query':
            query = value
        elif field == 'description':
            description = value
        else:
            print(f"Error: Unknown field '{field}'. Supported fields: query, description")
            return 1
    
    if query is None and description is None:
        print("Error: At least one field (query or description) must be specified for update")
        return 1
    
    return update_search_config(search_manager, name, query, description)


def determine_search_query(args, config) -> str:
    """Determine which search query to use based on arguments and config.
    
    Args:
        args: Parsed command-line arguments
        config: Application configuration
        
    Returns:
        Gmail search query string to use
        
    Raises:
        SearchConfigError: If configuration-related errors occur
        ValueError: If specified configuration is not found or invalid (for backward compatibility)
    """
    logger = logging.getLogger(__name__)
    
    # Priority: --search-query > --search-config > default
    if args.search_query and args.search_query.strip():
        query = args.search_query.strip()
        
        # Validate custom query if validation is enabled and search features are available
        search_configs_file = getattr(config, 'search_configs_file', 'search_configs.json')
        enable_validation = getattr(config, 'enable_search_validation', True)
        
        if enable_validation:
            try:
                search_manager = SearchConfigManager(search_configs_file)
                if search_manager.is_search_feature_available():
                    is_valid, error_msg = search_manager.validate_query(query)
                    if not is_valid:
                        suggestions = search_manager.validator.suggest_corrections(query)
                        logger.warning(f"Custom search query may be invalid: {error_msg}")
                        if suggestions:
                            logger.info(f"Query suggestions: {'; '.join(suggestions)}")
                        # Don't raise error for custom queries, just warn
                else:
                    logger.info("Search validation unavailable, skipping query validation")
            except Exception as e:
                logger.warning(f"Could not validate custom query (search features may be unavailable): {e}")
        
        logger.info(f"Using custom search query: {query}")
        return query
    
    elif args.search_config:
        search_configs_file = getattr(config, 'search_configs_file', 'search_configs.json')
        
        try:
            search_manager = SearchConfigManager(search_configs_file)
            
            # Check if search features are available
            if not search_manager.is_search_feature_available():
                logger.warning("Search configuration features are unavailable, falling back to default query")
                # Fall through to default query
            else:
                saved_config = search_manager.load_config_or_raise(args.search_config)
                
                # Update usage statistics
                try:
                    search_manager.update_usage_stats(args.search_config)
                    logger.debug(f"Updated usage statistics for configuration: {args.search_config}")
                except Exception as e:
                    logger.warning(f"Failed to update usage statistics: {e}")
                
                logger.info(f"Using saved search configuration '{args.search_config}': {saved_config.query}")
                return saved_config.query
            
        except ConfigurationNotFoundError as e:
            logger.error(str(e))
            # Convert to ValueError for backward compatibility
            raise ValueError(str(e))
        except CorruptedConfigFileError as e:
            logger.error(f"Configuration file is corrupted: {e}")
            logger.info("Falling back to default search query")
            # Fall through to default query
        except SearchConfigError as e:
            logger.error(f"Search configuration error: {e}")
            # Convert to ValueError for backward compatibility
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error loading search configuration: {e}")
            logger.info("Falling back to default search query")
            # Fall through to default query
    
    # Use default search query (fallback)
    default_query = getattr(config, 'default_search_query', 'is:unread is:important')
    logger.info(f"Using default search query: {default_query}")
    return default_query


def handle_search_help(operator: str = None) -> int:
    """Handle the --help-search command to show Gmail search operator help.
    
    Args:
        operator: Specific operator to show help for, or 'all' for all operators
        
    Returns:
        Exit code (0 for success)
    """
    try:
        if operator == 'all' or operator is None:
            help_text = GmailSearchHelp.get_operator_help()
        else:
            # Remove trailing colon if present for user convenience
            if operator.endswith(':'):
                operator = operator[:-1] + ':'
            elif not operator.endswith(':'):
                operator = operator + ':'
            
            help_text = GmailSearchHelp.get_operator_help(operator)
        
        print(help_text)
        return 0
        
    except Exception as e:
        print(f"Error displaying search help: {e}")
        return 1


def show_example_configs() -> int:
    """Handle the --example-configs command to show example configurations.
    
    Returns:
        Exit code (0 for success)
    """
    try:
        print("\nExample Gmail Search Configurations")
        print("=" * 38)
        print("\nThese are pre-defined configurations for common use cases.")
        print("Use --save-config to add any of these to your personal configurations.\n")
        
        categories = ExampleConfigurations.get_config_by_category()
        
        for category, configs in categories.items():
            if not configs:
                continue
                
            print(f"\n{category}")
            print("-" * len(category))
            
            for config in configs:
                print(f"\nName: {config.name}")
                print(f"Query: {config.query}")
                print(f"Description: {config.description}")
                print(f"Usage: --search-config {config.name}")
        
        print("\n" + "=" * 50)
        print("To save any example as your own configuration:")
        print('--save-config "my-name" "query" "description"')
        print("\nTo see help for Gmail search operators:")
        print("--help-search")
        print("\nTo validate a query before using it:")
        print('--validate-query "your query here"')
        
        return 0
        
    except Exception as e:
        print(f"Error displaying example configurations: {e}")
        return 1


def validate_search_query(query: str) -> int:
    """Handle the --validate-query command to validate a Gmail search query.
    
    Args:
        query: Gmail search query to validate
        
    Returns:
        Exit code (0 for valid query, 1 for invalid query)
    """
    try:
        from config.search_configs import QueryValidator
        
        validator = QueryValidator()
        is_valid, error_msg = validator.validate_query(query)
        
        print(f"\nQuery: {query}")
        print("=" * (len(query) + 7))
        
        if is_valid:
            print("✓ Query is valid!")
            
            # Show suggestions for improvement
            suggestions = GmailSearchHelp.get_search_suggestions(query)
            if suggestions:
                print("\nSuggestions for improvement:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            
            # Show relevant example configurations
            relevant_examples = ExampleConfigurations.get_config_suggestions_for_query(query)
            if relevant_examples:
                print("\nRelated example configurations:")
                for config in relevant_examples:
                    print(f"  • {config.name}: {config.description}")
                    print(f"    Query: {config.query}")
            
            return 0
        else:
            print(f"✗ Query is invalid: {error_msg}")
            
            # Show correction suggestions
            suggestions = validator.suggest_corrections(query)
            if suggestions:
                print("\nSuggestions:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            
            print("\nFor help with Gmail search operators, use: --help-search")
            return 1
            
    except Exception as e:
        print(f"Error validating query: {e}")
        return 1


def handle_transcript_only(date: str) -> int:
    """Handle the --transcript-only command to generate transcript from existing YAML.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            logger.info(f"Processing transcript generation for date: {date}")
        except ValueError:
            print(f"Error: Invalid date format '{date}'. Expected YYYY-MM-DD format.")
            logger.error(f"Invalid date format provided: {date}")
            return 1
        
        # Load configuration with error handling
        try:
            logger.info("Loading configuration for transcript generation...")
            config = load_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            print(f"Error: Could not load configuration - {e}")
            return 1
        
        # Check if transcript generation is enabled
        if not config.enable_transcript_generation:
            print("Transcript generation is disabled in configuration.")
            print("Set ENABLE_TRANSCRIPT_GENERATION=true in your .env file to enable it.")
            logger.info("Transcript generation is disabled in configuration")
            return 1
        
        # Ensure transcript directory exists with enhanced error handling
        try:
            if not ensure_transcript_directory(config):
                logger.error("Failed to create transcript directory")
                print(f"Error: Could not create transcript directory: {config.transcript_output_directory}")
                return 1
        except Exception as e:
            logger.error(f"Error ensuring transcript directory exists: {e}")
            print(f"Error: Could not access transcript directory - {e}")
            return 1
        
        # Initialize transcript components with enhanced error handling
        transcript_generator = None
        transcript_writer = None
        
        try:
            logger.info("Initializing transcript generator...")
            transcript_generator = TranscriptGenerator(config)
            logger.info("Transcript generator initialized successfully")
        except Exception as e:
            user_message = create_user_friendly_message(e, "initializing transcript generator")
            logger.error(f"Failed to initialize transcript generator: {user_message}")
            print(f"Error: Could not initialize transcript generator - {user_message}")
            return 1
        
        try:
            logger.info("Initializing transcript writer...")
            transcript_writer = TranscriptWriter(config.transcript_output_directory)
            logger.info("Transcript writer initialized successfully")
        except Exception as e:
            user_message = create_user_friendly_message(e, "initializing transcript writer")
            logger.error(f"Failed to initialize transcript writer: {user_message}")
            print(f"Error: Could not initialize transcript writer - {user_message}")
            return 1
        
        # Find the YAML file for the specified date
        yaml_file_path = os.path.join(config.output_directory, f"{date}.yaml")
        
        if not os.path.exists(yaml_file_path):
            print(f"Error: YAML file not found for date {date}: {yaml_file_path}")
            print(f"Please ensure the email summary file exists before generating transcript.")
            print(f"You can create it by running: python main.py --date {date}")
            logger.error(f"YAML file not found: {yaml_file_path}")
            return 1
        
        logger.info(f"Found YAML file: {yaml_file_path}")
        
        # Generate transcript with comprehensive error handling
        transcript_content = None
        try:
            logger.info(f"Generating transcript for {date}...")
            transcript_content = transcript_generator.generate_transcript(yaml_file_path, date)
            
            if not transcript_content or not transcript_content.strip():
                logger.error("Generated transcript is empty or contains only whitespace")
                print("Error: Generated transcript is empty. This may indicate an issue with the YAML file or AI service.")
                return 1
            
            logger.info(f"Generated transcript content ({len(transcript_content)} characters)")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, "generating transcript")
            logger.error(f"Transcript generation failed: {user_message}")
            print(f"Error: {user_message}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error during transcript generation: {e}")
            print(f"Error: Unexpected error during transcript generation - {e}")
            return 1
        
        # Write transcript to file with enhanced error handling
        try:
            logger.info("Writing transcript to file...")
            transcript_file_path = transcript_writer.write_transcript(transcript_content, date)
            
            # Verify the file was written successfully
            if not os.path.exists(transcript_file_path):
                logger.error(f"Transcript file was not created: {transcript_file_path}")
                print(f"Error: Transcript file was not created successfully")
                return 1
            
            logger.info(f"Transcript written successfully to: {transcript_file_path}")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, "writing transcript file")
            logger.error(f"Failed to write transcript file: {user_message}")
            print(f"Error: {user_message}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error writing transcript file: {e}")
            print(f"Error: Could not write transcript file - {e}")
            return 1
        
        # Display success message
        print("=" * 60)
        print("TRANSCRIPT GENERATION COMPLETE")
        print("=" * 60)
        print(f"Date: {date}")
        print(f"Source YAML: {yaml_file_path}")
        print(f"Transcript file: {transcript_file_path}")
        
        # Show transcript stats with error handling
        try:
            transcript_size = transcript_writer.get_transcript_size(date)
            if transcript_size:
                print(f"Transcript size: {transcript_size} bytes")
                
            # Show a preview of the transcript
            if len(transcript_content) > 100:
                preview = transcript_content[:100] + "..."
                print(f"Preview: {preview}")
            else:
                print(f"Content: {transcript_content}")
                
        except Exception as e:
            logger.debug(f"Could not get transcript stats: {e}")
            # Don't fail the operation for stats errors
        
        logger.info("Transcript generation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in transcript generation: {e}")
        print(f"Error: Transcript generation failed due to unexpected error - {e}")
        return 1


def generate_transcript_for_workflow(config, yaml_file_path: str, transcript_date: Optional[str] = None, verbose: bool = False) -> bool:
    """Generate transcript as part of the main email processing workflow.
    
    Args:
        config: Configuration object
        yaml_file_path: Path to the YAML file that was just created
        transcript_date: Optional date override for transcript generation
        verbose: Whether verbose logging is enabled
        
    Returns:
        bool: True if transcript generation succeeded, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate inputs
        if not yaml_file_path:
            logger.error("YAML file path is required for transcript generation")
            return False
        
        if not os.path.exists(yaml_file_path):
            logger.error(f"YAML file not found: {yaml_file_path}")
            return False
        
        # Determine the date for transcript generation
        if transcript_date:
            try:
                datetime.strptime(transcript_date, "%Y-%m-%d")
                date = transcript_date
                if verbose:
                    logger.info(f"Using specified transcript date: {date}")
            except ValueError:
                logger.error(f"Invalid transcript date format: {transcript_date}. Expected YYYY-MM-DD")
                return False
        else:
            # Extract date from YAML file path (e.g., email_summaries/2025-09-19.yaml)
            yaml_filename = os.path.basename(yaml_file_path)
            date = yaml_filename.replace('.yaml', '')
            try:
                datetime.strptime(date, "%Y-%m-%d")
                if verbose:
                    logger.info(f"Extracted date from filename: {date}")
            except ValueError:
                logger.error(f"Could not extract valid date from YAML filename: {yaml_filename}")
                # Try fallback to today's date
                date = datetime.now().strftime("%Y-%m-%d")
                logger.warning(f"Using today's date as fallback: {date}")
        
        if verbose:
            logger.info(f"Starting transcript generation for date: {date}")
        
        # Ensure transcript directory exists with enhanced error handling
        try:
            if not ensure_transcript_directory(config):
                logger.error("Failed to create transcript directory")
                return False
        except Exception as e:
            logger.error(f"Error ensuring transcript directory exists: {e}")
            return False
        
        # Initialize transcript components with enhanced error handling
        transcript_generator = None
        transcript_writer = None
        
        try:
            if verbose:
                logger.info("Initializing transcript generator...")
            transcript_generator = TranscriptGenerator(config)
            if verbose:
                logger.info("Transcript generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize transcript generator: {create_user_friendly_message(e, 'initializing transcript generator')}")
            return False
        
        try:
            if verbose:
                logger.info("Initializing transcript writer...")
            transcript_writer = TranscriptWriter(config.transcript_output_directory)
            if verbose:
                logger.info("Transcript writer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize transcript writer: {create_user_friendly_message(e, 'initializing transcript writer')}")
            return False
        
        # Generate transcript with comprehensive error handling
        transcript_content = None
        try:
            if verbose:
                logger.info(f"Generating transcript content from {yaml_file_path}...")
            transcript_content = transcript_generator.generate_transcript(yaml_file_path, date)
            
            if not transcript_content or not transcript_content.strip():
                logger.error("Generated transcript is empty or contains only whitespace")
                return False
            
            if verbose:
                logger.info(f"Generated transcript content ({len(transcript_content)} characters)")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, 'generating transcript')
            logger.error(f"Transcript generation failed: {user_message}")
            if verbose:
                logger.debug(f"Original error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during transcript generation: {e}")
            if verbose:
                logger.debug(f"Full error details: {e}", exc_info=True)
            return False
        
        # Write transcript to file with enhanced error handling
        try:
            if verbose:
                logger.info("Writing transcript to file...")
            transcript_file_path = transcript_writer.write_transcript(transcript_content, date)
            
            # Verify the file was written successfully
            if not os.path.exists(transcript_file_path):
                logger.error(f"Transcript file was not created: {transcript_file_path}")
                return False
            
            # Log success with file size information
            try:
                file_size = os.path.getsize(transcript_file_path)
                if verbose:
                    logger.info(f"Transcript written to: {transcript_file_path} ({file_size} bytes)")
                else:
                    logger.info(f"Transcript generated: {transcript_file_path}")
            except OSError:
                # File exists but can't get size - still a success
                logger.info(f"Transcript generated: {transcript_file_path}")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, 'writing transcript file')
            logger.error(f"Failed to write transcript file: {user_message}")
            if verbose:
                logger.debug(f"Original error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing transcript file: {e}")
            if verbose:
                logger.debug(f"Full error details: {e}", exc_info=True)
            return False
        
        # Log transcript statistics if verbose
        if verbose:
            try:
                transcript_size = transcript_writer.get_transcript_size(date)
                if transcript_size:
                    logger.info(f"Transcript file size: {transcript_size} bytes")
            except Exception as e:
                logger.debug(f"Could not get transcript size: {e}")
        
        if verbose:
            logger.info("Transcript generation workflow completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error in transcript workflow: {e}")
        if verbose:
            logger.debug(f"Full error details: {e}", exc_info=True)
        return False


def handle_audio_generation(date: str) -> int:
    """Handle the --generate-audio and --audio-date commands to generate audio from transcript.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            logger.info(f"Processing audio generation for date: {date}")
        except ValueError:
            print(f"Error: Invalid date format '{date}'. Expected YYYY-MM-DD format.")
            logger.error(f"Invalid date format provided: {date}")
            return 1
        
        # Load configuration with error handling
        try:
            logger.info("Loading configuration for audio generation...")
            config = load_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            print(f"Error: Could not load configuration - {e}")
            return 1
        
        # Check if audio generation is enabled
        if not config.enable_audio_generation:
            print("Audio generation is disabled in configuration.")
            print("Set ENABLE_AUDIO_GENERATION=true in your .env file to enable it.")
            logger.info("Audio generation is disabled in configuration")
            return 1
        
        # Ensure audio directory exists with enhanced error handling
        try:
            from config.settings import ensure_audio_directory
            if not ensure_audio_directory(config):
                logger.error("Failed to create audio directory")
                print(f"Error: Could not create audio directory: {config.audio_output_directory}")
                return 1
        except Exception as e:
            logger.error(f"Error ensuring audio directory exists: {e}")
            print(f"Error: Could not access audio directory - {e}")
            return 1
        
        # Initialize audio generator with enhanced error handling
        audio_generator = None
        
        try:
            logger.info("Initializing audio generator...")
            from audio.tts_generator import AudioGenerator
            audio_generator = AudioGenerator(config)
            logger.info("Audio generator initialized successfully")
        except Exception as e:
            user_message = create_user_friendly_message(e, "initializing audio generator")
            logger.error(f"Failed to initialize audio generator: {user_message}")
            print(f"Error: Could not initialize audio generator - {user_message}")
            return 1
        
        # Find the transcript file for the specified date
        transcript_file_path = os.path.join(config.transcript_output_directory, f"{date}.txt")
        
        if not os.path.exists(transcript_file_path):
            print(f"Error: Transcript file not found for date {date}: {transcript_file_path}")
            print(f"Please ensure the transcript file exists before generating audio.")
            print(f"You can create it by running: python main.py --transcript-only {date}")
            logger.error(f"Transcript file not found: {transcript_file_path}")
            return 1
        
        logger.info(f"Found transcript file: {transcript_file_path}")
        
        # Read transcript content
        transcript_content = None
        try:
            logger.info(f"Reading transcript content from {transcript_file_path}...")
            with open(transcript_file_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            if not transcript_content or not transcript_content.strip():
                logger.error("Transcript file is empty or contains only whitespace")
                print("Error: Transcript file is empty. This may indicate an issue with the transcript file.")
                return 1
            
            logger.info(f"Read transcript content ({len(transcript_content)} characters)")
            
        except Exception as e:
            logger.error(f"Failed to read transcript file: {e}")
            print(f"Error: Could not read transcript file - {e}")
            return 1
        
        # Generate audio file path
        audio_file_path = audio_generator.get_audio_path(date)
        
        # Check if audio file already exists
        if audio_generator.audio_exists(date):
            logger.info(f"Audio file already exists: {audio_file_path}")
            print(f"Audio file already exists: {audio_file_path}")
            print("Overwriting existing audio file...")
        
        # Generate audio with comprehensive error handling
        try:
            logger.info(f"Generating audio for {date}...")
            print(f"Generating audio from transcript ({len(transcript_content)} characters)...")
            
            generated_audio_path = audio_generator.generate_audio(transcript_content, audio_file_path)
            
            # Verify the file was created successfully
            if not os.path.exists(generated_audio_path):
                logger.error(f"Audio file was not created: {generated_audio_path}")
                print(f"Error: Audio file was not created successfully")
                return 1
            
            logger.info(f"Audio generated successfully: {generated_audio_path}")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, "generating audio")
            logger.error(f"Audio generation failed: {user_message}")
            print(f"Error: {user_message}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error during audio generation: {e}")
            print(f"Error: Unexpected error during audio generation - {e}")
            return 1
        
        # Display success message
        print("=" * 60)
        print("AUDIO GENERATION COMPLETE")
        print("=" * 60)
        print(f"Date: {date}")
        print(f"Source transcript: {transcript_file_path}")
        print(f"Audio file: {generated_audio_path}")
        
        # Show audio stats with error handling
        try:
            audio_size = audio_generator.get_audio_file_size(date)
            if audio_size:
                print(f"Audio file size: {audio_size} bytes")
                
            # Show a preview of the transcript content
            if len(transcript_content) > 100:
                preview = transcript_content[:100] + "..."
                print(f"Transcript preview: {preview}")
            else:
                print(f"Transcript content: {transcript_content}")
                
        except Exception as e:
            logger.debug(f"Could not get audio stats: {e}")
            # Don't fail the operation for stats errors
        
        logger.info("Audio generation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in audio generation: {e}")
        print(f"Error: Audio generation failed due to unexpected error - {e}")
        return 1


def generate_audio_for_workflow(config, transcript_file_path: str, audio_date: Optional[str] = None, verbose: bool = False) -> bool:
    """Generate audio as part of the main email processing workflow.
    
    Args:
        config: Configuration object
        transcript_file_path: Path to the transcript file that was just created
        audio_date: Optional date override for audio generation
        verbose: Whether verbose logging is enabled
        
    Returns:
        bool: True if audio generation succeeded, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Validate inputs
        if not transcript_file_path:
            logger.error("Transcript file path is required for audio generation")
            return False
        
        if not os.path.exists(transcript_file_path):
            logger.error(f"Transcript file not found: {transcript_file_path}")
            return False
        
        # Determine the date for audio generation
        if audio_date:
            try:
                datetime.strptime(audio_date, "%Y-%m-%d")
                date = audio_date
                if verbose:
                    logger.info(f"Using specified audio date: {date}")
            except ValueError:
                logger.error(f"Invalid audio date format: {audio_date}. Expected YYYY-MM-DD")
                return False
        else:
            # Extract date from transcript file path (e.g., transcripts/2025-09-19.txt)
            transcript_filename = os.path.basename(transcript_file_path)
            date = transcript_filename.replace('.txt', '')
            try:
                datetime.strptime(date, "%Y-%m-%d")
                if verbose:
                    logger.info(f"Extracted date from filename: {date}")
            except ValueError:
                logger.error(f"Could not extract valid date from transcript filename: {transcript_filename}")
                # Try fallback to today's date
                date = datetime.now().strftime("%Y-%m-%d")
                logger.warning(f"Using today's date as fallback: {date}")
        
        if verbose:
            logger.info(f"Starting audio generation for date: {date}")
        
        # Ensure audio directory exists with enhanced error handling
        try:
            from config.settings import ensure_audio_directory
            if not ensure_audio_directory(config):
                logger.error("Failed to create audio directory")
                return False
        except Exception as e:
            logger.error(f"Error ensuring audio directory exists: {e}")
            return False
        
        # Initialize audio generator with enhanced error handling
        audio_generator = None
        
        try:
            if verbose:
                logger.info("Initializing audio generator...")
            from audio.tts_generator import AudioGenerator
            audio_generator = AudioGenerator(config)
            if verbose:
                logger.info("Audio generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio generator: {create_user_friendly_message(e, 'initializing audio generator')}")
            return False
        
        # Read transcript content
        transcript_content = None
        try:
            if verbose:
                logger.info(f"Reading transcript content from {transcript_file_path}...")
            with open(transcript_file_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            if not transcript_content or not transcript_content.strip():
                logger.error("Transcript file is empty or contains only whitespace")
                return False
            
            if verbose:
                logger.info(f"Read transcript content ({len(transcript_content)} characters)")
            
        except Exception as e:
            logger.error(f"Failed to read transcript file: {e}")
            return False
        
        # Generate audio file path
        audio_file_path = audio_generator.get_audio_path(date)
        
        # Generate audio with comprehensive error handling
        try:
            if verbose:
                logger.info(f"Generating audio content from {transcript_file_path}...")
            generated_audio_path = audio_generator.generate_audio(transcript_content, audio_file_path)
            
            # Verify the file was created successfully
            if not os.path.exists(generated_audio_path):
                logger.error(f"Audio file was not created: {generated_audio_path}")
                return False
            
            if verbose:
                logger.info(f"Audio generated successfully: {generated_audio_path}")
            
        except (RetryableError, NonRetryableError) as e:
            user_message = create_user_friendly_message(e, 'generating audio')
            logger.error(f"Audio generation failed: {user_message}")
            if verbose:
                logger.debug(f"Original error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during audio generation: {e}")
            if verbose:
                logger.debug(f"Full error details: {e}", exc_info=True)
            return False
        
        # Log success with file size information
        try:
            file_size = os.path.getsize(generated_audio_path)
            if verbose:
                logger.info(f"Audio written to: {generated_audio_path} ({file_size} bytes)")
            else:
                logger.info(f"Audio generated: {generated_audio_path}")
        except OSError:
            # File exists but can't get size - still a success
            logger.info(f"Audio generated: {generated_audio_path}")
        
        # Log audio statistics if verbose
        if verbose:
            try:
                audio_size = audio_generator.get_audio_file_size(date)
                if audio_size:
                    logger.info(f"Audio file size: {audio_size} bytes")
            except Exception as e:
                logger.debug(f"Could not get audio size: {e}")
        
        if verbose:
            logger.info("Audio generation workflow completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error in audio workflow: {e}")
        if verbose:
            logger.debug(f"Full error details: {e}", exc_info=True)
        return False


def process_emails() -> int:
    """
    Main email processing workflow.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Handle configuration management commands first (these exit early)
        if args.list_configs or args.save_config or args.delete_config or args.update_config:
            return handle_config_commands(args)
        
        # Handle help and example commands (these also exit early)
        if args.help_search:
            return handle_search_help(args.help_search)
        
        if args.example_configs:
            return show_example_configs()
        
        if args.validate_query:
            return validate_search_query(args.validate_query)
        
        if args.transcript_only:
            return handle_transcript_only(args.transcript_only)
        
        # Handle audio generation commands
        if args.generate_audio:
            today = datetime.now().strftime("%Y-%m-%d")
            return handle_audio_generation(today)
        
        if args.audio_date:
            return handle_audio_generation(args.audio_date)
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Override config with command-line arguments if provided
        if args.max_emails:
            config.max_emails_per_run = args.max_emails
        if args.output_dir:
            config.output_directory = args.output_dir
        
        # Test AI connection if requested
        if args.test_ai:
            return 0 if test_ai_connection(config) else 1
        
        # Validate Gmail credentials
        if not validate_gmail_credentials(config):
            logger.error("Gmail credentials validation failed")
            logger.error("Please ensure credentials.json file exists in the project root")
            return 1
        
        # Ensure output directory exists
        if not ensure_output_directory(config):
            logger.error("Failed to create output directory")
            return 1
        
        # Initialize components with comprehensive error handling
        try:
            logger.info("Initializing email fetcher...")
            email_fetcher = create_email_fetcher(config.credentials_file, config.token_file)
        except (GmailAuthError, EmailFetchError, RetryableError, NonRetryableError) as e:
            logger.error(create_user_friendly_message(e, "initializing Gmail connection"))
            return 1
        
        try:
            logger.info("Initializing email processor...")
            email_processor = EmailProcessor()
        except Exception as e:
            logger.error(f"Failed to initialize email processor: {e}")
            return 1
        
        try:
            logger.info("Initializing email summarizer...")
            email_summarizer = EmailSummarizer(config)
        except (RetryableError, NonRetryableError) as e:
            logger.error(create_user_friendly_message(e, "initializing AI summarization service"))
            return 1
        
        try:
            logger.info("Initializing YAML writer...")
            yaml_writer = YAMLWriter(config.output_directory)
        except NonRetryableError as e:
            logger.error(create_user_friendly_message(e, "initializing file storage"))
            return 1
        
        # Determine search query to use
        try:
            search_query = determine_search_query(args, config)
        except ValueError as e:
            logger.error(str(e))
            return 1
        
        # Fetch emails with custom or default query
        try:
            logger.info(f"Fetching up to {config.max_emails_per_run} emails with query: {search_query}")
            raw_emails = email_fetcher.fetch_emails_with_query(search_query, config.max_emails_per_run)
            
            if not raw_emails:
                logger.info("No emails found matching the search criteria")
                # Create empty summary file
                try:
                    file_path = yaml_writer.create_empty_summary_file()
                    logger.info(f"Created empty summary file: {file_path}")
                    
                    # Generate transcript for empty email day if enabled
                    transcript_file_path = None
                    if not args.no_transcript and config.enable_transcript_generation:
                        try:
                            transcript_success = generate_transcript_for_workflow(
                                config, file_path, args.transcript_date, args.verbose
                            )
                            if transcript_success:
                                # Get transcript file path for audio generation
                                date = args.transcript_date if args.transcript_date else datetime.now().strftime("%Y-%m-%d")
                                transcript_file_path = os.path.join(config.transcript_output_directory, f"{date}.txt")
                            else:
                                logger.warning("Transcript generation failed for empty email day, but main workflow completed successfully")
                        except Exception as e:
                            logger.warning(f"Transcript generation for empty email day encountered an error: {e}")
                            logger.info("Main email processing workflow completed successfully despite transcript error")
                    elif args.no_transcript:
                        logger.info("Transcript generation skipped for empty email day due to --no-transcript flag")
                    elif not config.enable_transcript_generation:
                        logger.info("Transcript generation disabled in configuration for empty email day")
                    
                    # Generate audio for empty email day if enabled and transcript was created
                    if transcript_file_path and config.enable_audio_generation:
                        try:
                            audio_success = generate_audio_for_workflow(
                                config, transcript_file_path, args.audio_date, args.verbose
                            )
                            if not audio_success:
                                logger.warning("Audio generation failed for empty email day, but main workflow completed successfully")
                        except Exception as e:
                            logger.warning(f"Audio generation for empty email day encountered an error: {e}")
                            logger.info("Main email processing workflow completed successfully despite audio error")
                    elif not transcript_file_path and config.enable_audio_generation:
                        logger.info("Audio generation skipped for empty email day because transcript generation was not successful")
                    elif not config.enable_audio_generation:
                        logger.info("Audio generation disabled in configuration for empty email day")
                    
                    return 0
                except NonRetryableError as e:
                    logger.error(create_user_friendly_message(e, "creating empty summary file"))
                    return 1
            
            logger.info(f"Found {len(raw_emails)} emails matching search criteria")
            
        except (EmailFetchError, RetryableError, NonRetryableError) as e:
            logger.error(create_user_friendly_message(e, "fetching emails from Gmail"))
            return 1
        
        # Process emails to extract structured data
        logger.info("Processing email content...")
        processed_emails: List[EmailData] = []
        
        for i, raw_email in enumerate(raw_emails):
            try:
                # The fetcher already extracted the data, we just need to convert it to EmailData
                from email.utils import parsedate_to_datetime
                
                # Parse the date
                date_str = raw_email.get('date', '')
                try:
                    if date_str:
                        email_date = parsedate_to_datetime(date_str)
                    else:
                        email_date = datetime.now()
                except (ValueError, TypeError):
                    email_date = datetime.now()
                
                # Clean the body content using the processor
                body_content = raw_email.get('body', '')
                if body_content:
                    # Use the processor's HTML cleaning capabilities
                    cleaned_body = email_processor.clean_html_content(body_content)
                    if not cleaned_body or cleaned_body.strip() == "":
                        cleaned_body = email_processor._clean_plain_text(body_content)
                else:
                    cleaned_body = "No readable content found"
                
                # Create EmailData object with the already-extracted data
                email_data = EmailData(
                    subject=raw_email.get('subject', 'No Subject'),
                    sender=raw_email.get('sender', 'Unknown Sender'),
                    date=email_date,
                    body=cleaned_body,
                    message_id=raw_email.get('message_id', '')
                )
                
                processed_emails.append(email_data)
                logger.debug(f"Processed email {i+1}: {email_data.subject}")
            except Exception as e:
                logger.warning(f"Failed to process email {i+1}: {e}")
                continue
        
        if not processed_emails:
            logger.warning("No emails could be processed successfully")
            file_path = yaml_writer.create_empty_summary_file()
            logger.info(f"Created empty summary file: {file_path}")
            
            # Generate transcript for empty email day if enabled
            transcript_file_path = None
            if not args.no_transcript and config.enable_transcript_generation:
                try:
                    transcript_success = generate_transcript_for_workflow(
                        config, file_path, args.transcript_date, args.verbose
                    )
                    if transcript_success:
                        # Get transcript file path for audio generation
                        date = args.transcript_date if args.transcript_date else datetime.now().strftime("%Y-%m-%d")
                        transcript_file_path = os.path.join(config.transcript_output_directory, f"{date}.txt")
                    else:
                        logger.warning("Transcript generation failed for empty email day, but main workflow completed successfully")
                except Exception as e:
                    logger.warning(f"Transcript generation for empty email day encountered an error: {e}")
                    logger.info("Main email processing workflow completed successfully despite transcript error")
            elif args.no_transcript:
                logger.info("Transcript generation skipped for empty email day due to --no-transcript flag")
            elif not config.enable_transcript_generation:
                logger.info("Transcript generation disabled in configuration for empty email day")
            
            # Generate audio for empty email day if enabled and transcript was created
            if transcript_file_path and config.enable_audio_generation:
                try:
                    audio_success = generate_audio_for_workflow(
                        config, transcript_file_path, args.audio_date, args.verbose
                    )
                    if not audio_success:
                        logger.warning("Audio generation failed for empty email day, but main workflow completed successfully")
                except Exception as e:
                    logger.warning(f"Audio generation for empty email day encountered an error: {e}")
                    logger.info("Main email processing workflow completed successfully despite audio error")
            elif not transcript_file_path and config.enable_audio_generation:
                logger.info("Audio generation skipped for empty email day because transcript generation was not successful")
            elif not config.enable_audio_generation:
                logger.info("Audio generation disabled in configuration for empty email day")
            
            return 0
        
        logger.info(f"Successfully processed {len(processed_emails)} emails")
        
        # Generate AI summaries with error handling
        try:
            logger.info("Generating AI-powered summaries...")
            email_summaries = email_summarizer.batch_summarize_emails(processed_emails)
            
            if not email_summaries:
                logger.error("Failed to generate any email summaries")
                return 1
            
            logger.info(f"Generated {len(email_summaries)} email summaries")
            
        except Exception as e:
            logger.error(f"Unexpected error during AI summarization: {e}")
            logger.info("Attempting to create fallback summaries...")
            
            # Create basic fallback summaries
            email_summaries = []
            for email_data in processed_emails:
                try:
                    fallback_summary = email_summarizer._create_fallback_summary(email_data)
                    email_summaries.append(fallback_summary)
                except Exception as fallback_error:
                    logger.error(f"Failed to create fallback summary: {fallback_error}")
            
            if not email_summaries:
                logger.error("Failed to generate any summaries, including fallbacks")
                return 1
        
        # Store summaries in YAML file with error handling
        try:
            logger.info("Storing summaries in YAML file...")
            file_path = yaml_writer.write_daily_summary(email_summaries)
        except NonRetryableError as e:
            logger.error(create_user_friendly_message(e, "storing email summaries"))
            return 1
        
        # Display summary of actions taken
        logger.info("=" * 60)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Emails processed: {len(processed_emails)}")
        logger.info(f"Summaries generated: {len(email_summaries)}")
        logger.info(f"Output file: {file_path}")
        
        # Display summary statistics
        stats = yaml_writer.get_summary_stats()
        if stats.get("exists"):
            logger.info(f"File size: {stats.get('file_size', 0)} bytes")
            logger.info(f"Total emails in file: {stats.get('email_count', 0)}")
        
        # Generate transcript if enabled and not disabled by CLI flag
        transcript_file_path = None
        if not args.no_transcript and config.enable_transcript_generation:
            try:
                transcript_success = generate_transcript_for_workflow(
                    config, file_path, args.transcript_date, args.verbose
                )
                if transcript_success:
                    # Get transcript file path for audio generation
                    date = args.transcript_date if args.transcript_date else datetime.now().strftime("%Y-%m-%d")
                    transcript_file_path = os.path.join(config.transcript_output_directory, f"{date}.txt")
                else:
                    logger.warning("Transcript generation failed, but main workflow completed successfully")
            except Exception as e:
                logger.warning(f"Transcript generation encountered an error: {e}")
                logger.info("Main email processing workflow completed successfully despite transcript error")
        elif args.no_transcript:
            logger.info("Transcript generation skipped due to --no-transcript flag")
        elif not config.enable_transcript_generation:
            logger.info("Transcript generation disabled in configuration")
        
        # Generate audio if enabled and transcript was created
        if transcript_file_path and config.enable_audio_generation:
            try:
                audio_success = generate_audio_for_workflow(
                    config, transcript_file_path, args.audio_date, args.verbose
                )
                if not audio_success:
                    logger.warning("Audio generation failed, but main workflow completed successfully")
            except Exception as e:
                logger.warning(f"Audio generation encountered an error: {e}")
                logger.info("Main email processing workflow completed successfully despite audio error")
        elif not transcript_file_path and config.enable_audio_generation:
            logger.info("Audio generation skipped because transcript generation was not successful")
        elif not config.enable_audio_generation:
            logger.info("Audio generation disabled in configuration")
        
        logger.info("Gmail Email Summarizer completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except (GmailAuthError, EmailFetchError) as e:
        # These are already handled above, but catch any that slip through
        logger.error(create_user_friendly_message(e, "processing emails"))
        return 1
    except (RetryableError, NonRetryableError) as e:
        logger.error(create_user_friendly_message(e, "processing emails"))
        if e.category == ErrorCategory.AUTHENTICATION:
            logger.error("Please check your API keys and credentials")
        elif e.category == ErrorCategory.NETWORK:
            logger.error("Please check your internet connection and try again")
        elif e.category == ErrorCategory.FILE_SYSTEM:
            logger.error("Please check file permissions and available disk space")
        return 1
    except Exception as e:
        error_category = classify_error(e)
        logger.error(create_user_friendly_message(e, "processing emails"))
        logger.debug("Full error details:", exc_info=True)
        
        # Provide specific guidance based on error category
        if error_category == ErrorCategory.AUTHENTICATION:
            logger.error("This appears to be an authentication issue. Please check your credentials.")
        elif error_category == ErrorCategory.NETWORK:
            logger.error("This appears to be a network issue. Please check your connection.")
        elif error_category == ErrorCategory.FILE_SYSTEM:
            logger.error("This appears to be a file system issue. Please check permissions and disk space.")
        
        return 1


def handle_errors(func):
    """Decorator for comprehensive error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logging.getLogger(__name__).info("Process interrupted by user")
            return 1
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.debug("Full error details:", exc_info=True)
            return 1
    return wrapper


@handle_errors
def main():
    """Main entry point for the Gmail Email Summarizer."""
    # Parse arguments first to get verbose flag
    args = parse_arguments()
    
    # Setup logging with verbosity level
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Gmail Email Summarizer starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run main processing workflow
    exit_code = process_emails()
    
    if exit_code == 0:
        logger.info("Process completed successfully")
    else:
        logger.error("Process completed with errors")
    
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())