#!/usr/bin/env python3
"""
Configuration management commands for Rencom CLI
"""

import click
import yaml
from typing import Dict, Any
from pathlib import Path

from cli.utils.config import (
    get_config, save_config, create_default_config, get_config_info,
    CLIConfig, config_manager
)
from cli.utils.display import print_success, print_error, print_info
from cli.utils.error_handler import (
    validate_server_url, validate_timeout, validate_output_format,
    validate_boolean_string, validate_config_key, ValidationError
)


@click.group()
def config():
    """Manage CLI configuration settings"""
    pass


@config.command()
def show():
    """Show current configuration"""
    try:
        config_info = get_config_info()
        current_config = config_info['current_config']
        
        click.echo("Current CLI Configuration:")
        click.echo("=" * 40)
        
        # Display configuration values
        for key, value in current_config.items():
            click.echo(f"{key:15}: {value}")
        
        click.echo()
        click.echo("Configuration Details:")
        click.echo(f"Config file: {config_info['config_file']}")
        click.echo(f"File exists: {config_info['config_file_exists']}")
        click.echo(f"Config dir:  {config_info['config_dir']}")
        
        # Show environment overrides if any
        env_overrides = config_info['env_overrides']
        if env_overrides:
            click.echo()
            click.echo("Environment Variable Overrides:")
            for key, value in env_overrides.items():
                click.echo(f"  {key}: {value}")
        
    except Exception as e:
        print_error(f"Failed to show configuration: {e}")
        raise click.Abort()


@config.command()
@click.option('--server-url', help='Set server URL')
@click.option('--timeout', type=int, help='Set request timeout in seconds')
@click.option('--output-format', type=click.Choice(['text', 'json']), help='Set output format')
@click.option('--verbose/--no-verbose', default=None, help='Enable/disable verbose output')
@click.option('--debug/--no-debug', default=None, help='Enable/disable debug mode')
def set(server_url, timeout, output_format, verbose, debug):
    """Set configuration values"""
    try:
        # Load current configuration
        current_config = get_config()
        
        # Update values that were provided (with validation)
        updated = False
        if server_url is not None:
            validated_url = validate_server_url(server_url)
            current_config.server_url = validated_url
            updated = True
            print_info(f"Set server_url to: {validated_url}")
        
        if timeout is not None:
            validated_timeout = validate_timeout(timeout)
            current_config.timeout = validated_timeout
            updated = True
            print_info(f"Set timeout to: {validated_timeout}")
        
        if output_format is not None:
            validated_format = validate_output_format(output_format)
            current_config.output_format = validated_format
            updated = True
            print_info(f"Set output_format to: {validated_format}")
        
        if verbose is not None:
            current_config.verbose = verbose
            updated = True
            print_info(f"Set verbose to: {verbose}")
        
        if debug is not None:
            current_config.debug = debug
            updated = True
            print_info(f"Set debug to: {debug}")
        
        if not updated:
            click.echo("No configuration values were provided to set.")
            click.echo("Use --help to see available options.")
            return
        
        # Save updated configuration
        save_config(current_config)
        print_success("Configuration updated successfully!")
        
    except Exception as e:
        print_error(f"Failed to update configuration: {e}")
        raise click.Abort()


@config.command()
@click.option('--force', is_flag=True, help='Overwrite existing configuration file')
def init(force):
    """Initialize configuration file with default values"""
    try:
        config_file = config_manager.get_config_file()
        
        if config_file.exists() and not force:
            click.echo(f"Configuration file already exists: {config_file}")
            click.echo("Use --force to overwrite existing configuration.")
            return
        
        create_default_config()
        print_success(f"Configuration file created: {config_file}")
        
    except Exception as e:
        print_error(f"Failed to initialize configuration: {e}")
        raise click.Abort()


@config.command()
def path():
    """Show configuration file and directory paths"""
    try:
        config_info = get_config_info()
        
        click.echo("Configuration Paths:")
        click.echo("=" * 30)
        click.echo(f"Config directory: {config_info['config_dir']}")
        click.echo(f"Config file:      {config_info['config_file']}")
        click.echo(f"File exists:      {config_info['config_file_exists']}")
        
    except Exception as e:
        print_error(f"Failed to show configuration paths: {e}")
        raise click.Abort()


@config.command()
@click.confirmation_option(prompt='Are you sure you want to reset configuration to defaults?')
def reset():
    """Reset configuration to default values"""
    try:
        # Create default configuration
        default_config = CLIConfig()
        save_config(default_config)
        print_success("Configuration reset to default values!")
        
    except Exception as e:
        print_error(f"Failed to reset configuration: {e}")
        raise click.Abort()


@config.command()
def validate():
    """Validate current configuration"""
    try:
        # Validate configuration file specifically
        validation_result = config_manager.validate_config_file()
        
        if validation_result['valid']:
            print_success("Configuration is valid!")
            
            # Show the validated configuration
            click.echo()
            click.echo("Validated Configuration:")
            for key, value in validation_result['config_data'].items():
                click.echo(f"  {key}: {value}")
                
            # Show warnings if any
            if validation_result['warnings']:
                click.echo()
                click.echo("Warnings:")
                for warning in validation_result['warnings']:
                    click.echo(f"  ⚠️  {warning}")
        else:
            print_error("Configuration validation failed!")
            
            # Show errors
            if validation_result['errors']:
                click.echo()
                click.echo("Errors:")
                for error in validation_result['errors']:
                    click.echo(f"  ❌ {error}")
            
            # Show warnings if any
            if validation_result['warnings']:
                click.echo()
                click.echo("Warnings:")
                for warning in validation_result['warnings']:
                    click.echo(f"  ⚠️  {warning}")
            
            raise click.Abort()
            
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        raise click.Abort()


@config.command()
def repair():
    """Repair configuration file by fixing invalid entries"""
    try:
        # First validate to see what's wrong
        validation_result = config_manager.validate_config_file()
        
        if validation_result['valid']:
            print_success("Configuration is already valid - no repair needed!")
            return
        
        click.echo("Configuration issues found:")
        for error in validation_result['errors']:
            click.echo(f"  ❌ {error}")
        
        # Ask for confirmation
        if not click.confirm("Attempt to repair configuration file?"):
            click.echo("Repair cancelled.")
            return
        
        # Attempt repair
        if config_manager.repair_config():
            print_success("Configuration repaired successfully!")
            
            # Validate again to confirm
            new_validation = config_manager.validate_config_file()
            if new_validation['valid']:
                click.echo()
                click.echo("Repaired Configuration:")
                for key, value in new_validation['config_data'].items():
                    click.echo(f"  {key}: {value}")
            else:
                print_error("Repair was not completely successful. Some issues remain.")
        else:
            print_error("Failed to repair configuration file.")
            raise click.Abort()
            
    except Exception as e:
        print_error(f"Failed to repair configuration: {e}")
        raise click.Abort()


@config.command()
@click.argument('key')
@click.argument('value')
def update(key, value):
    """Update a single configuration value"""
    try:
        # Validate configuration key
        validated_key = validate_config_key(key)
        
        # Convert and validate value based on key type
        if key == 'server_url':
            converted_value = validate_server_url(value)
        elif key == 'timeout':
            try:
                timeout_int = int(value)
                converted_value = validate_timeout(timeout_int)
            except ValueError:
                raise ValidationError(f"Invalid timeout value: {value}. Must be an integer.")
        elif key in ['verbose', 'debug']:
            converted_value = validate_boolean_string(value)
        elif key == 'output_format':
            converted_value = validate_output_format(value)
        else:
            # For other keys, use the value as-is but validate it's not empty
            if not value.strip():
                raise ValidationError(f"Value for {key} cannot be empty")
            converted_value = value.strip()
        
        # Update the configuration value
        if config_manager.update_config_value(validated_key, converted_value):
            print_success(f"Updated {validated_key} to: {converted_value}")
        else:
            print_error(f"Failed to update {validated_key}")
            raise click.Abort()
            
    except ValidationError as e:
        print_error(f"Validation error: {e.message}")
        if e.hint:
            print_info(f"Hint: {e.hint}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to update configuration: {e}")
        raise click.Abort()


@config.command()
def edit():
    """Open configuration file in default editor"""
    try:
        config_file = config_manager.get_config_file()
        
        # Create config file if it doesn't exist
        if not config_file.exists():
            create_default_config()
            print_info(f"Created default configuration file: {config_file}")
        
        # Try to open in editor
        import subprocess
        import os
        
        # Try different editors
        editors = [
            os.environ.get('EDITOR'),
            'code',  # VS Code
            'notepad',  # Windows Notepad
            'nano',  # Linux/Mac nano
            'vim',   # Vim
        ]
        
        for editor in editors:
            if editor:
                try:
                    subprocess.run([editor, str(config_file)], check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        # If no editor worked, just show the file path
        print_info(f"Please edit the configuration file manually: {config_file}")
        
    except Exception as e:
        print_error(f"Failed to open configuration file: {e}")
        raise click.Abort()


if __name__ == '__main__':
    config()