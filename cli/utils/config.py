#!/usr/bin/env python3
"""
CLI Configuration Management
Handles configuration file loading, validation, and environment variable overrides
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field, validator
import click


@dataclass
class CLIConfig:
    """CLI Configuration data class"""
    server_url: str = "https://rencom-backend.fly.dev"
    timeout: int = 30
    output_format: str = "text"  # text, json
    verbose: bool = False
    debug: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CLIConfig':
        """Create from dictionary"""
        return cls(**data)


class CLIConfigValidator(BaseModel):
    """Pydantic model for configuration validation"""
    server_url: str = Field(default="https://rencom-backend.fly.dev", description="Server URL for API requests")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    output_format: str = Field(default="text", description="Output format")
    verbose: bool = Field(default=False, description="Enable verbose output")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    @validator('server_url')
    def validate_server_url(cls, v):
        if not isinstance(v, str):
            raise ValueError('Server URL must be a string')
        if not v.strip():
            raise ValueError('Server URL cannot be empty')
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Server URL must start with http:// or https://')
        # Basic URL format validation
        if not v.replace('http://', '').replace('https://', '').strip():
            raise ValueError('Server URL must contain a valid domain or IP address')
        return v.strip()
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if not isinstance(v, int):
            raise ValueError('Timeout must be an integer')
        if v < 1:
            raise ValueError('Timeout must be at least 1 second')
        if v > 300:
            raise ValueError('Timeout cannot exceed 300 seconds (5 minutes)')
        return v
    
    @validator('output_format')
    def validate_output_format(cls, v):
        if not isinstance(v, str):
            raise ValueError('Output format must be a string')
        valid_formats = ['text', 'json']
        if v not in valid_formats:
            raise ValueError(f'Output format must be one of: {", ".join(valid_formats)}')
        return v
    
    @validator('verbose')
    def validate_verbose(cls, v):
        if not isinstance(v, bool):
            raise ValueError('Verbose must be a boolean (true/false)')
        return v
    
    @validator('debug')
    def validate_debug(cls, v):
        if not isinstance(v, bool):
            raise ValueError('Debug must be a boolean (true/false)')
        return v


class ConfigManager:
    """Manages CLI configuration loading, validation, and saving"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.rencom'
        self.config_file = self.config_dir / 'config.yaml'
        self._config: Optional[CLIConfig] = None
    
    def get_config_dir(self) -> Path:
        """Get configuration directory path"""
        return self.config_dir
    
    def get_config_file(self) -> Path:
        """Get configuration file path"""
        return self.config_file
    
    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> CLIConfig:
        """Load configuration from file and environment variables"""
        if self._config is not None:
            return self._config
        
        # Start with default configuration
        config_data = CLIConfig().to_dict()
        
        # Load from configuration file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                config_data.update(file_config)
            except Exception as e:
                click.echo(f"Warning: Failed to load config file {self.config_file}: {e}", err=True)
        
        # Override with environment variables
        env_overrides = self._get_env_overrides()
        config_data.update(env_overrides)
        
        # Validate configuration
        try:
            validated_config = CLIConfigValidator(**config_data)
            self._config = CLIConfig(**validated_config.dict())
        except Exception as e:
            raise click.ClickException(f"Invalid configuration: {e}")
        
        return self._config
    
    def _get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        env_mapping = {
            'RENCOM_SERVER_URL': 'server_url',
            'RENCOM_TIMEOUT': 'timeout',
            'RENCOM_OUTPUT_FORMAT': 'output_format',
            'RENCOM_VERBOSE': 'verbose',
            'RENCOM_DEBUG': 'debug',
        }
        
        overrides = {}
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if config_key == 'timeout':
                    try:
                        overrides[config_key] = int(value)
                    except ValueError:
                        click.echo(f"Warning: Invalid timeout value in {env_var}: {value}", err=True)
                elif config_key in ['verbose', 'debug']:
                    overrides[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    overrides[config_key] = value
        
        return overrides
    
    def save_config(self, config: CLIConfig) -> None:
        """Save configuration to file"""
        self.ensure_config_dir()
        
        try:
            # Validate before saving
            CLIConfigValidator(**config.to_dict())
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=True)
            
            # Clear cached config to force reload
            self._config = None
            
        except Exception as e:
            raise click.ClickException(f"Failed to save configuration: {e}")
    
    def create_default_config(self) -> None:
        """Create default configuration file"""
        default_config = CLIConfig()
        self.save_config(default_config)
        click.echo(f"Created default configuration file: {self.config_file}")
    
    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        """Validate configuration data"""
        try:
            CLIConfigValidator(**config_data)
            return True
        except Exception as e:
            click.echo(f"Configuration validation failed: {e}", err=True)
            return False
    
    def validate_config_file(self) -> Dict[str, Any]:
        """Validate configuration file and return validation results"""
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'config_data': None
        }
        
        # Check if config file exists
        if not self.config_file.exists():
            result['warnings'].append(f"Configuration file does not exist: {self.config_file}")
            result['config_data'] = CLIConfig().to_dict()
            result['valid'] = True  # Default config is valid
            return result
        
        # Try to load and parse YAML
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            result['config_data'] = config_data
        except yaml.YAMLError as e:
            result['errors'].append(f"Invalid YAML format: {e}")
            return result
        except Exception as e:
            result['errors'].append(f"Failed to read config file: {e}")
            return result
        
        # Validate configuration data
        try:
            # Merge with defaults to ensure all fields are present
            default_config = CLIConfig().to_dict()
            merged_config = {**default_config, **config_data}
            
            # Validate merged configuration
            CLIConfigValidator(**merged_config)
            result['valid'] = True
            result['config_data'] = merged_config
            
            # Check for unknown keys
            known_keys = set(default_config.keys())
            provided_keys = set(config_data.keys())
            unknown_keys = provided_keys - known_keys
            
            if unknown_keys:
                result['warnings'].append(f"Unknown configuration keys (will be ignored): {', '.join(unknown_keys)}")
                
        except Exception as e:
            result['errors'].append(f"Configuration validation failed: {e}")
        
        return result
    
    def repair_config(self) -> bool:
        """Attempt to repair configuration file by removing invalid entries"""
        try:
            validation_result = self.validate_config_file()
            
            if validation_result['valid']:
                return True  # Nothing to repair
            
            # Load current config data
            config_data = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as f:
                        config_data = yaml.safe_load(f) or {}
                except:
                    pass  # Will use empty dict
            
            # Create a repaired config with only valid entries
            default_config = CLIConfig().to_dict()
            repaired_config = {}
            
            for key, default_value in default_config.items():
                if key in config_data:
                    try:
                        # Try to validate individual field
                        test_config = {**default_config, key: config_data[key]}
                        CLIConfigValidator(**test_config)
                        repaired_config[key] = config_data[key]
                    except:
                        # Use default value if validation fails
                        repaired_config[key] = default_value
                        click.echo(f"Warning: Reset invalid {key} to default value", err=True)
                else:
                    repaired_config[key] = default_value
            
            # Save repaired configuration
            repaired_cli_config = CLIConfig.from_dict(repaired_config)
            self.save_config(repaired_cli_config)
            
            return True
            
        except Exception as e:
            click.echo(f"Failed to repair configuration: {e}", err=True)
            return False
    
    def update_config_value(self, key: str, value: Any) -> bool:
        """Update a single configuration value"""
        try:
            # Load current configuration
            current_config = self.load_config()
            
            # Update the specific value
            if hasattr(current_config, key):
                setattr(current_config, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")
            
            # Save updated configuration
            self.save_config(current_config)
            return True
            
        except Exception as e:
            click.echo(f"Failed to update configuration value {key}: {e}", err=True)
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about current configuration"""
        config = self.load_config()
        return {
            'config_file': str(self.config_file),
            'config_file_exists': self.config_file.exists(),
            'config_dir': str(self.config_dir),
            'current_config': config.to_dict(),
            'env_overrides': self._get_env_overrides()
        }


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> CLIConfig:
    """Get current CLI configuration"""
    return config_manager.load_config()


def save_config(config: CLIConfig) -> None:
    """Save CLI configuration"""
    config_manager.save_config(config)


def create_default_config() -> None:
    """Create default configuration file"""
    config_manager.create_default_config()


def get_config_info() -> Dict[str, Any]:
    """Get configuration information"""
    return config_manager.get_config_info()