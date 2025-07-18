"""
Centralized error handling utilities for CLI commands
"""

import sys
import traceback
import click
from typing import Optional, Dict, Type, Callable, Any
from functools import wraps
from rich.console import Console

from cli.utils.display import print_error, print_warning, Colors

console = Console()


class CLIError(Exception):
    """Base exception for CLI-specific errors"""
    def __init__(self, message: str, exit_code: int = 1, hint: Optional[str] = None):
        self.message = message
        self.exit_code = exit_code
        self.hint = hint
        super().__init__(message)


class ValidationError(CLIError):
    """Exception for input validation errors"""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message, exit_code=2, hint=hint)


class NetworkError(CLIError):
    """Exception for network-related errors"""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message, exit_code=3, hint=hint)


class AuthenticationError(CLIError):
    """Exception for authentication-related errors"""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message, exit_code=4, hint=hint)


class ConfigurationError(CLIError):
    """Exception for configuration-related errors"""
    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message, exit_code=5, hint=hint)


# Exit code constants
class ExitCodes:
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_USAGE = 2
    NETWORK_ERROR = 3
    AUTHENTICATION_ERROR = 4
    CONFIGURATION_ERROR = 5


# Error type to exit code mapping
ERROR_EXIT_CODES: Dict[Type[Exception], int] = {
    CLIError: 1,
    ValidationError: ExitCodes.INVALID_USAGE,
    NetworkError: ExitCodes.NETWORK_ERROR,
    AuthenticationError: ExitCodes.AUTHENTICATION_ERROR,
    ConfigurationError: ExitCodes.CONFIGURATION_ERROR,
    click.ClickException: 2,
    ConnectionError: ExitCodes.NETWORK_ERROR,
    TimeoutError: ExitCodes.NETWORK_ERROR,
    PermissionError: ExitCodes.AUTHENTICATION_ERROR,
    FileNotFoundError: ExitCodes.CONFIGURATION_ERROR,
    KeyError: ExitCodes.CONFIGURATION_ERROR,
    ValueError: ExitCodes.INVALID_USAGE,
}


def get_exit_code(exception: Exception) -> int:
    """Get appropriate exit code for an exception"""
    # Check for specific CLI errors first
    if isinstance(exception, CLIError):
        return exception.exit_code
    
    # Check for click exceptions
    if isinstance(exception, click.ClickException):
        return getattr(exception, 'exit_code', ExitCodes.INVALID_USAGE)
    
    # Check mapped exception types
    for exc_type, exit_code in ERROR_EXIT_CODES.items():
        if isinstance(exception, exc_type):
            return exit_code
    
    # Default to general error
    return ExitCodes.GENERAL_ERROR


def format_error_message(exception: Exception, debug: bool = False) -> str:
    """Format error message for display"""
    if isinstance(exception, CLIError):
        return exception.message
    elif isinstance(exception, click.ClickException):
        return str(exception)
    elif isinstance(exception, ConnectionError):
        return f"Connection failed: {str(exception)}"
    elif isinstance(exception, TimeoutError):
        return f"Operation timed out: {str(exception)}"
    elif isinstance(exception, PermissionError):
        return f"Permission denied: {str(exception)}"
    elif isinstance(exception, FileNotFoundError):
        return f"File not found: {str(exception)}"
    elif isinstance(exception, ValueError):
        return f"Invalid value: {str(exception)}"
    elif isinstance(exception, KeyError):
        return f"Missing configuration: {str(exception)}"
    else:
        return f"Unexpected error: {str(exception)}"


def get_error_hint(exception: Exception) -> Optional[str]:
    """Get helpful hint for an exception"""
    if isinstance(exception, CLIError):
        return exception.hint
    elif isinstance(exception, ConnectionError):
        return "Check if the server is running and accessible"
    elif isinstance(exception, TimeoutError):
        return "Try increasing the timeout with --timeout option"
    elif isinstance(exception, PermissionError):
        return "Check file permissions or run with appropriate privileges"
    elif isinstance(exception, FileNotFoundError):
        return "Ensure the required configuration files exist"
    elif isinstance(exception, KeyError):
        return "Run 'rencom setup --interactive' to configure missing settings"
    elif isinstance(exception, ValueError):
        return "Check the format and validity of your input"
    else:
        return None


def handle_exception(exception: Exception, debug: bool = False, context: Optional[str] = None) -> int:
    """
    Handle an exception and return appropriate exit code
    
    Args:
        exception: The exception to handle
        debug: Whether to show debug information
        context: Optional context about where the error occurred
    
    Returns:
        Exit code for the error
    """
    # Handle click exceptions specially (they handle their own display)
    if isinstance(exception, click.ClickException):
        exception.show()
        return getattr(exception, 'exit_code', ExitCodes.INVALID_USAGE)
    
    # Format error message
    error_message = format_error_message(exception, debug)
    
    # Add context if provided
    if context:
        error_message = f"{context}: {error_message}"
    
    # Display error
    print_error(error_message)
    
    # Show hint if available
    hint = get_error_hint(exception)
    if hint:
        print_warning(f"Hint: {hint}")
    
    # Show debug information if requested
    if debug:
        console.print("\n[bold red]Debug Information:[/bold red]", style="red")
        console.print(f"Exception type: {type(exception).__name__}", style="dim")
        console.print(f"Exception args: {exception.args}", style="dim")
        console.print("\n[bold red]Traceback:[/bold red]", style="red")
        console.print(traceback.format_exc(), style="dim")
    
    # Get and return exit code
    exit_code = get_exit_code(exception)
    return exit_code


def safe_execute(func: Callable, *args, debug: bool = False, context: Optional[str] = None, **kwargs) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        debug: Whether to show debug information on error
        context: Optional context about the operation
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or exits with appropriate code on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        exit_code = handle_exception(e, debug=debug, context=context)
        sys.exit(exit_code)


def error_handler(context: Optional[str] = None):
    """
    Decorator for adding error handling to CLI commands
    
    Args:
        context: Optional context description for the operation
    
    Usage:
        @error_handler("Health check operation")
        def health_command():
            # Command implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get debug flag from click context if available
            debug = False
            try:
                ctx = click.get_current_context(silent=True)
                if ctx and hasattr(ctx.obj, 'debug'):
                    debug = ctx.obj.debug
            except:
                pass
            
            return safe_execute(func, *args, debug=debug, context=context, **kwargs)
        
        return wrapper
    return decorator


def validate_input(value: Any, validator: Callable[[Any], bool], error_message: str, hint: Optional[str] = None) -> Any:
    """
    Validate input value and raise ValidationError if invalid
    
    Args:
        value: Value to validate
        validator: Function that returns True if value is valid
        error_message: Error message to show if validation fails
        hint: Optional hint for fixing the validation error
    
    Returns:
        The validated value
    
    Raises:
        ValidationError: If validation fails
    """
    if not validator(value):
        raise ValidationError(error_message, hint=hint)
    return value


def validate_url(url: str) -> str:
    """Validate URL format"""
    if not url:
        raise ValidationError("URL cannot be empty", hint="Provide a valid HTTP or HTTPS URL")
    
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(
            f"Invalid URL format: {url}",
            hint="URL must start with http:// or https://"
        )
    
    return url


def validate_token(token: str) -> str:
    """Validate token format"""
    if not token:
        raise ValidationError("Token cannot be empty")
    
    if len(token) < 16:
        raise ValidationError(
            "Token is too short",
            hint="Token must be at least 16 characters long"
        )
    
    if len(token) > 128:
        raise ValidationError(
            "Token is too long",
            hint="Token must be no more than 128 characters long"
        )
    
    # Check for valid characters (alphanumeric)
    if not token.replace('-', '').replace('_', '').isalnum():
        raise ValidationError(
            "Token contains invalid characters",
            hint="Token should only contain letters, numbers, hyphens, and underscores"
        )
    
    return token


def validate_timeout(timeout: int) -> int:
    """Validate timeout value"""
    if timeout <= 0:
        raise ValidationError(
            "Timeout must be positive",
            hint="Provide a timeout value greater than 0 seconds"
        )
    
    if timeout > 300:  # 5 minutes
        raise ValidationError(
            "Timeout is too large",
            hint="Timeout should be no more than 300 seconds (5 minutes)"
        )
    
    return timeout


def validate_port(port: int) -> int:
    """Validate port number"""
    if port < 1 or port > 65535:
        raise ValidationError(
            f"Invalid port number: {port}",
            hint="Port must be between 1 and 65535"
        )
    
    return port


def validate_email(email: str) -> str:
    """Validate email format"""
    import re
    
    if not email:
        raise ValidationError("Email cannot be empty")
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError(
            f"Invalid email format: {email}",
            hint="Email must be in format: user@domain.com"
        )
    
    return email


def validate_name(name: str, min_length: int = 1, max_length: int = 100) -> str:
    """Validate name/string input"""
    if not name or not name.strip():
        raise ValidationError(
            "Name cannot be empty",
            hint=f"Provide a name between {min_length} and {max_length} characters"
        )
    
    name = name.strip()
    
    if len(name) < min_length:
        raise ValidationError(
            f"Name is too short (minimum {min_length} characters)",
            hint=f"Provide a name between {min_length} and {max_length} characters"
        )
    
    if len(name) > max_length:
        raise ValidationError(
            f"Name is too long (maximum {max_length} characters)",
            hint=f"Provide a name between {min_length} and {max_length} characters"
        )
    
    return name


def validate_file_path(path: str, must_exist: bool = False) -> str:
    """Validate file path"""
    import os
    from pathlib import Path
    
    if not path:
        raise ValidationError("File path cannot be empty")
    
    try:
        path_obj = Path(path).expanduser().resolve()
    except Exception as e:
        raise ValidationError(
            f"Invalid file path: {path}",
            hint="Provide a valid file path"
        )
    
    if must_exist and not path_obj.exists():
        raise ValidationError(
            f"File does not exist: {path}",
            hint="Ensure the file exists and is accessible"
        )
    
    return str(path_obj)


def validate_json_string(json_str: str) -> str:
    """Validate JSON string format"""
    import json
    
    if not json_str:
        raise ValidationError("JSON string cannot be empty")
    
    try:
        json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON format: {str(e)}",
            hint="Ensure the JSON is properly formatted"
        )
    
    return json_str


def validate_choice(value: str, choices: list, case_sensitive: bool = False) -> str:
    """Validate that value is one of the allowed choices"""
    if not case_sensitive:
        value = value.lower()
        choices = [choice.lower() for choice in choices]
    
    if value not in choices:
        raise ValidationError(
            f"Invalid choice: {value}",
            hint=f"Must be one of: {', '.join(choices)}"
        )
    
    return value


def validate_positive_integer(value: int, min_value: int = 1, max_value: int = None) -> int:
    """Validate positive integer within range"""
    if value < min_value:
        raise ValidationError(
            f"Value must be at least {min_value}",
            hint=f"Provide a value between {min_value} and {max_value or 'unlimited'}"
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"Value must be no more than {max_value}",
            hint=f"Provide a value between {min_value} and {max_value}"
        )
    
    return value


def validate_output_format(format_str: str) -> str:
    """Validate output format choice"""
    valid_formats = ['text', 'json', 'yaml', 'table']
    return validate_choice(format_str, valid_formats, case_sensitive=False)


def validate_log_level(level: str) -> str:
    """Validate log level choice"""
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    return validate_choice(level, valid_levels, case_sensitive=False).upper()


def validate_boolean_string(value: str) -> bool:
    """Convert string to boolean with validation"""
    if isinstance(value, bool):
        return value
    
    if not isinstance(value, str):
        raise ValidationError(
            f"Invalid boolean value: {value}",
            hint="Use true/false, yes/no, 1/0, or on/off"
        )
    
    value = value.lower().strip()
    
    if value in ('true', 'yes', '1', 'on', 'enable', 'enabled'):
        return True
    elif value in ('false', 'no', '0', 'off', 'disable', 'disabled'):
        return False
    else:
        raise ValidationError(
            f"Invalid boolean value: {value}",
            hint="Use true/false, yes/no, 1/0, or on/off"
        )


def validate_server_url(url: str) -> str:
    """Enhanced server URL validation"""
    import re
    from urllib.parse import urlparse
    
    if not url:
        raise ValidationError("Server URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValidationError(
            f"Invalid URL format: {url}",
            hint="Provide a valid URL like http://localhost:8000 or https://api.example.com"
        )
    
    if not parsed.netloc:
        raise ValidationError(
            f"Invalid URL - missing host: {url}",
            hint="Provide a valid URL like http://localhost:8000 or https://api.example.com"
        )
    
    # Validate hostname/IP
    hostname = parsed.hostname
    if not hostname:
        raise ValidationError(
            f"Invalid hostname in URL: {url}",
            hint="Provide a valid hostname or IP address"
        )
    
    # Validate port if specified
    if parsed.port is not None:
        validate_port(parsed.port)
    
    return url


def validate_config_key(key: str) -> str:
    """Validate configuration key name"""
    valid_keys = [
        'server_url', 'timeout', 'output_format', 'verbose', 'debug',
        'log_level', 'max_retries', 'retry_delay'
    ]
    
    if key not in valid_keys:
        raise ValidationError(
            f"Invalid configuration key: {key}",
            hint=f"Valid keys are: {', '.join(valid_keys)}"
        )
    
    return key


def validate_token_name(name: str) -> str:
    """Validate token name"""
    if not name:
        return name  # Empty name is allowed
    
    name = name.strip()
    
    if len(name) > 50:
        raise ValidationError(
            "Token name is too long (maximum 50 characters)",
            hint="Provide a shorter name for the token"
        )
    
    # Check for invalid characters
    import re
    if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
        raise ValidationError(
            "Token name contains invalid characters",
            hint="Token name can only contain letters, numbers, spaces, hyphens, underscores, and dots"
        )
    
    return name


def require_confirmation(message: str, default: bool = False) -> bool:
    """
    Require user confirmation for destructive operations
    
    Args:
        message: Confirmation message to display
        default: Default value if user just presses Enter
    
    Returns:
        True if user confirmed, False otherwise
    """
    try:
        return click.confirm(
            click.style(f"⚠️  {message}", fg='yellow'),
            default=default
        )
    except click.Abort:
        print_warning("Operation cancelled by user")
        return False


def check_prerequisites(checks: Dict[str, Callable[[], bool]], context: str = "Prerequisites") -> None:
    """
    Check prerequisites and raise ConfigurationError if any fail
    
    Args:
        checks: Dictionary of check name to check function
        context: Context for error messages
    
    Raises:
        ConfigurationError: If any prerequisite check fails
    """
    failed_checks = []
    
    for check_name, check_func in checks.items():
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            failed_checks.append(f"{check_name} (error: {str(e)})")
    
    if failed_checks:
        error_message = f"{context} failed: {', '.join(failed_checks)}"
        hint = "Run 'rencom setup --interactive' to configure your environment"
        raise ConfigurationError(error_message, hint=hint)