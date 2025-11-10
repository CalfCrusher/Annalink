"""
Config module for Annalink blockchain.

This module handles configuration loading from files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary
    """
    config = {}

    # Load default config
    default_path = Path(__file__).parent / "default.yaml"
    if default_path.exists():
        with open(default_path, 'r') as f:
            config = yaml.safe_load(f) or {}

    # Load custom config if provided
    if config_path:
        custom_path = Path(config_path)
        if custom_path.exists():
            with open(custom_path, 'r') as f:
                custom_config = yaml.safe_load(f) or {}
                # Merge configs (custom overrides default)
                config = _merge_configs(config, custom_config)

    # Override with environment variables
    config = _override_with_env(config)

    return config


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two config dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def _override_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override config with environment variables."""
    # Simple implementation - in production, use a proper env mapping
    if 'ANNALINK_HOST' in os.environ:
        config.setdefault('network', {})['host'] = os.environ['ANNALINK_HOST']
    if 'ANNALINK_PORT' in os.environ:
        config.setdefault('network', {})['port'] = int(os.environ['ANNALINK_PORT'])
    if 'ANNALINK_DIFFICULTY' in os.environ:
        config.setdefault('consensus', {})['difficulty_target'] = int(os.environ['ANNALINK_DIFFICULTY'])

    return config