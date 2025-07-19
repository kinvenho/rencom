"""
Constants and configuration for the Rencom CLI
Centralized location for version numbers, URLs, and other key content
"""

# Version Information
CLI_VERSION = "1.0.3"
BACKEND_VERSION = "1.0.3"
CLI_APP_NAME = "Rencom"

# API Endpoints
API_BASE_URL = "https://rencom-backend.fly.dev"
API_HEALTH_ENDPOINT = "/health"
API_TOKENS_ENDPOINT = "/api/v1/tokens"
API_REVIEWS_ENDPOINT = "/api/v1/reviews"

# Documentation and Support URLs
GITHUB_REPO_URL = "https://github.com/rencom"
LEAD_DEVELOPER_URL = "https://renreviews.com/"
FASTAPI_DOCS_URL = "https://fastapi.tiangolo.com"
SUPABASE_DOCS_URL = "https://supabase.com/docs"
CLI_PYPI_URL = "https://pypi.org/project/rencom-cli/"

# Default Configuration
DEFAULT_SERVER_URL = "https://rencom-backend.fly.dev"
DEFAULT_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# CLI Messages
WELCOME_MESSAGE = "Command-line interface for the Rencom Reviews API"
SETUP_DESCRIPTION = "Onboard and create your API token for the Rencom API"
FORK_DESCRIPTION = "Advanced: Fork and run the codebase locally for development"
HEALTH_DESCRIPTION = "Check server health status and connectivity"

# ASCII Art (Rencom logo)
ASCII_ART = [
    "░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓██████████████▓▒░  ",
    "░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓███████▓▒░░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
    "░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░ ",
]

# Gradient Colors for ASCII Art
ASCII_GRADIENT_START = (242, 47, 70)  # F22F46 (red)
ASCII_GRADIENT_END = (255, 255, 255)  # FFFFFF (white)

# Command Descriptions
COMMAND_DESCRIPTIONS = {
    "rencom": "Displays welcome message and basic information",
    "rencom health": "Check server health status and connectivity",
    "rencom setup": "Onboard and create your API token",
    "rencom fork": "Advanced: Fork and run the codebase locally",
    "rencom token generate": "Generate new API access token",
    "rencom help": "Show this comprehensive help information",
    "rencom help --examples": "Show usage examples for all commands",
    "rencom help --support": "Show support contact information",
    "rencom help --command <cmd>": "Show detailed help for specific command"
}

# Example Descriptions
EXAMPLE_DESCRIPTIONS = {
    "rencom": "Show welcome message and version",
    "rencom --version": "Show version information",
    "rencom --help": "Show basic help information",
    "rencom health": "Check server health with default settings",
    "rencom health --verbose": "Check health with detailed output",
    "rencom health --server-url http://localhost:3000": "Check health of custom server",
    "rencom health --timeout 60": "Check health with extended timeout",
    "rencom setup": "Onboard and create your API token",
    "rencom fork": "Run interactive setup for local development",
    "rencom fork health": "Check health of local development server",
    "rencom help": "Show comprehensive help information",
    "rencom help --examples": "Show usage examples (this screen)",
    "rencom help --support": "Show support contact information",
    "rencom help --command health": "Show detailed help for health command",
    "rencom token generate": "Generate new API access token",
    "rencom token list": "List all active tokens",
    "rencom token revoke <token-id>": "Revoke specific API token",
    "rencom --debug health": "Run health check with debug output",
    "rencom --server-url https://api.example.com health": "Check remote server health",
    "rencom --verbose setup": "Run setup with verbose output"
}

# Troubleshooting Tips
TROUBLESHOOTING_TIPS = [
    "Server not responding: Check if the server is running with 'rencom health'",
    "API token issues: Run 'rencom setup' to create a new token",
    "Connection timeouts: Increase timeout with '--timeout 60' option",
    "Local development: Use 'rencom fork' for local setup",
    "Environment issues: Check your configuration with 'rencom config'"
]

# Common Issues and Solutions
COMMON_ISSUES = [
    ("Command not found", "Ensure CLI is installed: pip install rencom-cli"),
    ("Server connection failed", "Check server URL and ensure server is running"),
    ("API token invalid", "Run 'rencom setup' to create a new token"),
    ("Permission denied", "Check file permissions for config files"),
    ("Import errors", "Verify all dependencies are installed")
] 